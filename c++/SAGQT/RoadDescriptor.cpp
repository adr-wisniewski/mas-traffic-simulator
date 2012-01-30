#include "CrossroadsDescriptor.h"
//==============================================================================================================
RoadDescriptor::RoadDescriptor(int size, CrossroadsDescriptor *closer, CrossroadsDescriptor *farther, Concurrency::ITarget<DrawingInfo> &drawingInfoInputRef):
drawingInfoInput(drawingInfoInputRef)
{
	this->size = size;
	this->closer = closer;
	this->farther = farther;
	setType(ROAD_DESCRIPTOR_TYPE);

	for(int i =2; i < 4; i++)
	{
		if(closer->neighbors[i]!=NULL && closer->neighbors[i]==farther)
		{
			direction = i;
			closerComunication[INPUT_ROAD] = &(closer->crossroadsOutput[i]);
			closerComunication[OUTPUT_ROAD] = &(closer->crossroadsInput[i]);

			fartherComunication[INPUT_ROAD] = &(farther->crossroadsOutput[i-2]);
			fartherComunication[OUTPUT_ROAD] = &(farther->crossroadsInput[i-2]);
		}
			
	}

	closerWaiting = fartherWaiting = false;
}
//==============================================================================================================
void RoadDescriptor::run()
{
	Concurrency::unbounded_buffer<MessageDescriptor> releser;
	Concurrency::call<int> releserCaller([&releser](int type)
		{
			MessageDescriptor message;
			message.messageType = TIMER;
			message.descriptor = NULL;

			Concurrency::asend(releser, message);

		});

	Concurrency::timer<int> releserTimer(40, TIMER, &releserCaller, true);

	releserTimer.start();

	while(1)
	{
		MessageDescriptor message;

		message = Concurrency::receive(releser);

		while(Concurrency::try_receive(closerComunication[INPUT_ROAD], message))
		{
			if(message.messageType == CAR)
			{
				MessageDescriptor answer;
				if(direction == HORRIZONTAL)
				{
					
					if(carsOnRoadsCloserToFarther.empty() || (carsOnRoadsCloserToFarther.back()->x) - closer->x >10)
					{						
						answer.messageType = SPACE;
					}
					else
					{
						answer.messageType = LACK;
					}
				}
				if(direction == VERTICAL)
				{
					
					if(carsOnRoadsCloserToFarther.empty() || (carsOnRoadsCloserToFarther.back()->y - closer->y) >10)
					{						
						answer.messageType = SPACE;
					}
					else
					{
						answer.messageType = LACK;
					}
				}

				Concurrency::asend(closerComunication[OUTPUT_ROAD], answer);

				continue;
			}

			//Znaczy �e dostali�my nowy samochodzik, trzeba go powita� i i wys�a� siebie aby mia� komunikacj�. 
			else if(message.messageType == ENTERING)
			{
				MessageDescriptor answer;

				answer.messageType = WELCOME;

				//Je�li przybywa od strony bli�szego nale�y da� komunikator przychodz�cy od dalszego
				answer.target = fartherComunication[INPUT_ROAD];

				//Umieszczanie nowego pupilka w lis�ie
				CarDescriptor *pupilek = (CarDescriptor *)(message.descriptor);

				carsOnRoadsCloserToFarther.push_back(pupilek);
				//Okre�lanie wsp�rz�dnych

				pupilek->x = closer->x;
				pupilek->y = closer->y;

				if(direction == HORRIZONTAL)
				{
					pupilek->x += 5;
					pupilek->y +=5;
				}
				else if(direction == VERTICAL)
				{
					pupilek->y += 5;
					pupilek->x -= 5;
				}

				Concurrency::asend(pupilek->input, answer);

				continue;
			}

			//Je�li samoch�d op�ci� drog� od strony bli�szego. to usu� go z drogi
			else if(message.messageType == OUTGOING)
			{
				carsOnRoadsFartherToCloser.pop_front();
				closerWaiting = false;

				continue;
			}
		}

		while(Concurrency::try_receive(fartherComunication[INPUT_ROAD], message))
		{
			if(message.messageType == CAR)
			{
				MessageDescriptor answer;
				if(direction == HORRIZONTAL)
				{
					
					if(carsOnRoadsFartherToCloser.empty() || (farther->x - carsOnRoadsFartherToCloser.back()->x) >10)
					{						
						answer.messageType = SPACE;
					}
					else
					{
						answer.messageType = LACK;
					}
				}
				if(direction == VERTICAL)
				{
					
					if(carsOnRoadsFartherToCloser.empty() || (farther->y - carsOnRoadsFartherToCloser.back()->y) >10)
					{						
						answer.messageType = SPACE;
					}
					else
					{
						answer.messageType = LACK;
					}
				}

				Concurrency::asend(fartherComunication[OUTPUT_ROAD], answer);
				continue;
			}
			//Znaczy �e dostali�my nowy samochodzik, trzeba go powita� i i wys�a� siebie aby mia� komunikacj�. 
			else if(message.messageType == ENTERING)
			{
				MessageDescriptor answer;

				answer.messageType = WELCOME;

				//Je�li przybywa od strony dalszego nale�y da� komunikator przychodz�cy od bi�szego
				answer.target = closerComunication[INPUT_ROAD];

				//Umieszczanie nowego pupilka w lis�ie
				CarDescriptor *pupilek = (CarDescriptor *)(message.descriptor);

				carsOnRoadsFartherToCloser.push_back(pupilek);
				//Okre�lanie wsp�rz�dnych

				pupilek->x = farther->x;
				pupilek->y = farther->y;

				if(direction == HORRIZONTAL)
				{
					pupilek->x -= 5;
					pupilek->y -=5;
				}
				else if(direction == VERTICAL)
				{
					pupilek->y -= 5;
					pupilek->x += 5;
				}

				Concurrency::asend(pupilek->input, answer);
				continue;
			}
			//Je�li samoch�d op�ci� drog� od strony dalsego. to usu� go z drogi
			else if(message.messageType == OUTGOING)
			{
				carsOnRoadsCloserToFarther.pop_front();
				fartherWaiting = false;
				continue;
			}
		}

		//Przes�wanie samochod�w
		//W  Poziomie
		if(direction == HORRIZONTAL)
		{
			if(!carsOnRoadsCloserToFarther.empty())
			{
				std::list<CarDescriptor*>::iterator elier = carsOnRoadsCloserToFarther.begin();
				std::list<CarDescriptor*>::iterator later = carsOnRoadsCloserToFarther.begin();

				//Je�li to zasz�o to znaczy �e samoch�d stoi ju� przy szkrzy�owaniu
				if((farther->x - (*later)->x) <=12)
				{
					if(!fartherWaiting)
					{
						MessageDescriptor crossroadMessage;

						crossroadMessage.messageType = CAR;
						crossroadMessage.descriptor = (*later);

						Concurrency::asend(fartherComunication[OUTPUT_ROAD], crossroadMessage);
						fartherWaiting = true;
					}
				}
				else
					(*later)->x++;


				later++;

				while(later != carsOnRoadsCloserToFarther.end())
				{
					if(((*elier)->x - (*later)->x) > 12)
						(*later)->x++;

					elier++;
					later++;
				}
			}
			if(!carsOnRoadsFartherToCloser.empty())
			{
				std::list<CarDescriptor*>::iterator elier = carsOnRoadsFartherToCloser.begin();
				std::list<CarDescriptor*>::iterator later = carsOnRoadsFartherToCloser.begin();

				//Je�li to zasz�o to znaczy �e samoch�d stoi ju� przy szkrzy�owaniu
				if(( (*later)->x  - closer->x ) <=12)
				{
					if(!closerWaiting)
					{
						MessageDescriptor crossroadMessage;

						crossroadMessage.messageType = CAR;
						crossroadMessage.descriptor = (*later);

						Concurrency::asend(closerComunication[OUTPUT_ROAD], crossroadMessage);
						closerWaiting = true;
					}
				}
				else
					(*later)->x--;

				later++;

				while(later != carsOnRoadsFartherToCloser.end())
				{
					if(((*later)->x - (*elier)->x) > 12)
						(*later)->x--;

					elier++;
					later++;
				}
			}
		}

		//W pionie
		if(direction == VERTICAL)
		{
			if(!carsOnRoadsCloserToFarther.empty())
			{
				std::list<CarDescriptor*>::iterator elier = carsOnRoadsCloserToFarther.begin();
				std::list<CarDescriptor*>::iterator later = carsOnRoadsCloserToFarther.begin();

				//Je�li to zasz�o to znaczy �e samoch�d stoi ju� przy szkrzy�owaniu
				if((farther->y - (*later)->y) <=12)
				{
					if(!fartherWaiting)
					{
						MessageDescriptor crossroadMessage;

						crossroadMessage.messageType = CAR;
						crossroadMessage.descriptor = (*later);

						Concurrency::asend(fartherComunication[OUTPUT_ROAD], crossroadMessage);
						fartherWaiting = true;
					}
				}
				else 
					(*later)->y++;
				later++;

				while(later != carsOnRoadsCloserToFarther.end())
				{
					if(((*elier)->y - (*later)->y) > 12)
						(*later)->y++;

					elier++;
					later++;
				}
			}
			if(!carsOnRoadsFartherToCloser.empty())
			{
				std::list<CarDescriptor*>::iterator elier = carsOnRoadsFartherToCloser.begin();
				std::list<CarDescriptor*>::iterator later = carsOnRoadsFartherToCloser.begin();

				//Je�li to zasz�o to znaczy �e samoch�d stoi ju� przy szkrzy�owaniu
				if(( (*later)->y  - closer->y ) <=12)
				{
					if(!closerWaiting)
					{
						MessageDescriptor crossroadMessage;

						crossroadMessage.messageType = CAR;
						crossroadMessage.descriptor = (*later);

						Concurrency::asend(closerComunication[OUTPUT_ROAD], crossroadMessage);
						closerWaiting = true;
					}
				}
				else
					(*later)->y--;

				later++;

				while(later != carsOnRoadsFartherToCloser.end())
				{
					if(((*later)->y - (*elier)->y) > 12)
						(*later)->y--;

					elier++;
					later++;
				}
			}
		}

		//Zbieranie info o po�o�eniu i wysy�anie do rysuj�cego
		
		std::list<CarDescriptor*>::iterator iter = carsOnRoadsCloserToFarther.begin();
		std::list<CarDescriptor*>::iterator iter2 = carsOnRoadsFartherToCloser.begin();

		while(iter != carsOnRoadsCloserToFarther.end())
		{
			DrawingInfo info;

			info.id = (*iter)->id;
			info.x = (*iter)->x;
			info.y = (*iter)->y;

			Concurrency::asend(drawingInfoInput, info);
			iter++;
		}
		while(iter2 != carsOnRoadsFartherToCloser.end())
		{
			DrawingInfo info;

			info.id = (*iter2)->id;
			info.x = (*iter2)->x;
			info.y = (*iter2)->y;

			Concurrency::asend(drawingInfoInput, info);
			iter2++;
		}
	}//while(1)
}

void CarDescriptor::run()
{
	//Zapisanie d�ugo�ci �cie�ki
	roadLength = dijxtraArray[begin][1][target];
	int buffer = target;

	//Zapisanie kolejnych element�w �cie�ki
	while(buffer != -1)
	{
		road.push_front(buffer);
		buffer = dijxtraArray[begin][2][buffer];
	}

	//Us�wanie startowego bo zostawiamy zawsze cel
	road.pop_front();

	while(1)
	{
		MessageDescriptor message;
		//Odbieram wiadomo��
		message = Concurrency::receive(input);

		//Je�li finish to znaczy �e koniec
		if(message.messageType ==FINISH)
		{
			if(outgoing != NULL)
			{
				MessageDescriptor bybyMessage;
				bybyMessage.messageType = OUTGOING;
				Concurrency::send(outgoing, bybyMessage);
			}

			MessageDescriptor finishMessage;
			finishMessage.messageType = FINISH;
			finishMessage.descriptor = this;

			time_t actualTime = time(NULL);

			double seconds = (double)(actualTime - startTime);

			avarageSpeed = (roadLength/2000.0)/(seconds/3600);

			Concurrency::asend(mainAgentInput, finishMessage);

			break;
		}
		//Je�li welcome to znaczy �e na nowej drodze
		else if(message.messageType ==WELCOME)
		{	
			if(outgoing != NULL)
			{
				MessageDescriptor bybyMessage;
				bybyMessage.messageType = OUTGOING;
				Concurrency::send(outgoing, bybyMessage);
			}

			outgoing = message.target;

			road.pop_front();
		}
		//Je�li entering zanczy �e trzeba przedstawi� si� nowej drodze
		else if(message.messageType ==ENTERING)
		{
			//Je�li to pierwszy raz zapisz startowy czas
			if(notRunning)
			{
				startTime = time(NULL);
				notRunning = false;
			}

			incoming = message.target;

			MessageDescriptor welcomeMessage;
			welcomeMessage.messageType = ENTERING;
			welcomeMessage.descriptor = this;

			Concurrency::asend(incoming, welcomeMessage);
		}
	}
}

//==============================================================================================================
void CrossroadsDescriptor::run()
{
	//Ryliser uruchamiaj�cy nasze skrzy�owanie dwukrotnie cz�ciej ni� drog�
	Concurrency::unbounded_buffer<MessageDescriptor> releser;
	Concurrency::call<int> releserCaller([&releser](int type)
	{
		MessageDescriptor message;
		message.messageType = TIMER;
		message.descriptor = NULL;

		Concurrency::asend(releser, message);

	});
	Concurrency::timer<int> releserTimer(40, TIMER, &releserCaller, true);

	releserTimer.start();

		while(1)
		{
			MessageDescriptor message;

			message = Concurrency::receive(releser);

			//Je�li nie ma oczekuj�cych na rozpocz�cie wjazdu to srpawd� czy nie 
			if(waitings[4] == NULL)
			{
				//Je�li kto� jednak chce wjecha�
				if(Concurrency::try_receive(crossroadsInput[4], message))
				{
					waitings[4] = (CarDescriptor *)message.descriptor;
					waitingsDirection[4] = findDirction(waitings[4]);
				}
			}

			//Je�li dosta�em jakiego� wje�d�aj�cego staram si� go ulokowa� je�li mi si� nie uda to staram si� roz�adowywa� ruch
			if(waitings[4] != NULL)
			{
				//Je�li przyby�y jest w celu to go sko�cz nie powinno to mie� miejsca ale lepiej to ni� wywalic app
				if(waitingsDirection[4]==-1)
				{
					MessageDescriptor finishMessage;
					finishMessage.messageType = FINISH;
					Concurrency::asend(waitings[4]->input, finishMessage);

					waitings[4] = NULL;
				}

				//A je�li nie r�wna si� null to trzeba zagaja� do drogi
				else
				{
					MessageDescriptor carMessage;
					carMessage.messageType = CAR;

					Concurrency::asend(crossroadsOutput[waitingsDirection[4]], carMessage);

					carMessage = Concurrency::receive(crossroadsInput[waitingsDirection[4]]);

					//Je�li jest miejsce to wy�lj tam samoch�d
					if(carMessage.messageType == SPACE)
					{
						carMessage.messageType = ENTERING;
						carMessage.target = &crossroadsOutput[waitingsDirection[4]];

						Concurrency::asend(waitings[4]->input, carMessage);

						waitings[4] = NULL;
					}
				}
			}

			
			//Teraz przyst�pujemy do kierowania ruchem normalnym
			//Zbieranie oczekuj�cych
			for(int i = 0; i < 4; i++)
			{
				//Je�li nie ma ju� oczekuj�cego i s�siad nie jest NULLEM to sprawd� czy nie masz wiadomo�ci
				if(waitings[i] == NULL && neighbors[i] != NULL)
				{
					MessageDescriptor inputMessage;

					//Je�li dosta�em wiadomo�� to dodaj do oczekuj�cych 
					if(Concurrency::try_receive(crossroadsInput[i] ,inputMessage))
					{
						waitings[i] = (CarDescriptor *)inputMessage.descriptor;
						waitingsDirection[i] = findDirction(waitings[i]);
						waitingTurnDirection[i] = giveTurnDirection(i, waitingsDirection[i]);
					}
				}
				else if(waitings[i] != NULL)
					bool test = true;
			
			}

			//Sprawdzamy czy kto� nie dotar� ju� do celu
			for(int i = 0 ; i < 4; i++)
			{
				if(waitings[i] != NULL && waitingsDirection[i] == -1)
				{
					MessageDescriptor finishMessage;
					finishMessage.messageType = FINISH;
					Concurrency::asend(waitings[i]->input, finishMessage);

					waitings[i] = NULL;
				}	
			}

			
			//Roz�adowywanie skrzy�owania pozornie niesko�czone 
			while(1)
			{
				bool someoneWent = false;
				int stopReason[4];
				//zerowanie stop reson co pr�ba bo mo�e co� si� przesun�o
				for(int i = 0 ; i < 4; i++)
					stopReason[i] = 0;

				//Najpierw sprawdzanie prawoskr�tnych
				for(int i = 0; i < 4; i++)
				{
					if(waitings[i] != NULL && waitingTurnDirection[i] == RIGHT)
					{
						MessageDescriptor carMessage;
						carMessage.messageType = CAR;

						Concurrency::asend(crossroadsOutput[waitingsDirection[i]], carMessage);

						carMessage = Concurrency::receive(crossroadsInput[waitingsDirection[i]]);

						//Je�li jest miejsce to wy�lj tam samoch�d
						if(carMessage.messageType == SPACE)
						{
							carMessage.messageType = ENTERING;
							carMessage.target = &crossroadsOutput[waitingsDirection[i]];

							Concurrency::asend(waitings[i]->input, carMessage);

							waitings[i] = NULL;
							stopReason[i] = NON;

							someoneWent = true;
						}
						else
						{
							stopReason[i] = JAM;
						}
					}
				}//Prawoskr�tni

				//Potem jad�cych prosto
				for(int i = 0; i < 4; i++)
				{
					if(waitings[i] != NULL && waitingTurnDirection[i] == STRAIGTH)
					{
						//Sprawdzam czy po prawej nikt nie stoi
						if(waitings[(i+1)%4] == NULL)
						{
							MessageDescriptor carMessage;
							carMessage.messageType = CAR;

							Concurrency::asend(crossroadsOutput[waitingsDirection[i]], carMessage);

							carMessage = Concurrency::receive(crossroadsInput[waitingsDirection[i]]);

							//Je�li jest miejsce to wy�lj tam samoch�d
							if(carMessage.messageType == SPACE)
							{
								carMessage.messageType = ENTERING;
								carMessage.target = &crossroadsOutput[waitingsDirection[i]];

								Concurrency::asend(waitings[i]->input, carMessage);

								waitings[i] = NULL;
								stopReason[i] = NON;

								someoneWent = true;
							}
							else
							{
								stopReason[i] = JAM;
							}
						}//Sprawdzanie prawego s�siada
						else
						{
							stopReason[i] = BLOCK;
						}
					}
				}//Prosci

				//Na koniec lewoskr�tni
				for(int i = 0; i < 4; i++)
				{
					if(waitings[i] != NULL && waitingTurnDirection[i] == LEFT)
					{
						//Sprawdzam czy po prawej i prosto nikt nie stoi
						if(waitings[(i+1)%4] == NULL && waitings[(i+2)%4] == NULL)
						{
							MessageDescriptor carMessage;
							carMessage.messageType = CAR;

							Concurrency::asend(crossroadsOutput[waitingsDirection[i]], carMessage);

							carMessage = Concurrency::receive(crossroadsInput[waitingsDirection[i]]);

							//Je�li jest miejsce to wy�lj tam samoch�d
							if(carMessage.messageType == SPACE)
							{
								carMessage.messageType = ENTERING;
								carMessage.target = &crossroadsOutput[waitingsDirection[i]];

								Concurrency::asend(waitings[i]->input, carMessage);

								waitings[i] = NULL;
								stopReason[i] = NON;

								someoneWent = true;
							}
							else
							{
								stopReason[i] = JAM;
							}
						}//Sprawdzanie prawego s�siada
						else
						{
							stopReason[i] = BLOCK;
						}
					}
				}//Prosci

				//Je�li kto� pojecha� to kontynuuj
				if(someoneWent)
					continue;

				//Je�li nikt nie pojecha� to sprawd� powody je�li cho� jeden jest po prostu zablokowany to go pu�� a jak nie to ko�cz
				for(int i = 0 ; i < 4 ; i ++)
				{
					if(waitings[i] != NULL && stopReason[i] == BLOCK)
					{
						MessageDescriptor carMessage;
						carMessage.messageType = CAR;

						Concurrency::asend(crossroadsOutput[waitingsDirection[i]], carMessage);

						carMessage = Concurrency::receive(crossroadsInput[waitingsDirection[i]]);

						//Je�li jest miejsce to wy�lj tam samoch�d
						if(carMessage.messageType == SPACE)
						{
							carMessage.messageType = ENTERING;
							carMessage.target = &crossroadsOutput[waitingsDirection[i]];
							Concurrency::asend(waitings[i]->input, carMessage);

							waitings[i] = NULL;
							stopReason[i] = NON;

							someoneWent = true;
							break;
						}
						else
						{
							stopReason[i] = JAM;
						}

					}
				}//Sprawdzanie czy jest kto� kogo trzeba przepchn��

				//Je�li mimo to nikt nie pojecha� to idziemy spa�
				if(!someoneWent)
					break;

			}//Roz�adowywanie skrzy�owania

		}//while(1)
}
//==============================================================================================================
int CrossroadsDescriptor::findDirction(CarDescriptor *car)
{
	if(car->road.empty())
		return -1;

	int idNext = *(car->road.begin());

	for(int i = 0 ; i < 4; i++)
	{
		if(neighbors[i] != NULL && neighbors[i]->id == idNext)
			return i;
	}

	return -1;
}
//==============================================================================================================
int CrossroadsDescriptor::giveTurnDirection(int start, int destination)
{
	if(start>destination)
		return start - destination;
	else
		return destination - start;
}
//==============================================================================================================