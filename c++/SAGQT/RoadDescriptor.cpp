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

			//Znaczy ¿e dostaliœmy nowy samochodzik, trzeba go powitaæ i i wys³aæ siebie aby mia³ komunikacjê. 
			else if(message.messageType == ENTERING)
			{
				MessageDescriptor answer;

				answer.messageType = WELCOME;

				//Jeœli przybywa od strony bli¿szego nale¿y daæ komunikator przychodz¹cy od dalszego
				answer.target = fartherComunication[INPUT_ROAD];

				//Umieszczanie nowego pupilka w lisæie
				CarDescriptor *pupilek = (CarDescriptor *)(message.descriptor);

				carsOnRoadsCloserToFarther.push_back(pupilek);
				//Okreœlanie wspó³rzêdnych

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

			//Jeœli samochód opóœci³ drogê od strony bli¿szego. to usuñ go z drogi
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
			//Znaczy ¿e dostaliœmy nowy samochodzik, trzeba go powitaæ i i wys³aæ siebie aby mia³ komunikacjê. 
			else if(message.messageType == ENTERING)
			{
				MessageDescriptor answer;

				answer.messageType = WELCOME;

				//Jeœli przybywa od strony dalszego nale¿y daæ komunikator przychodz¹cy od bi¿szego
				answer.target = closerComunication[INPUT_ROAD];

				//Umieszczanie nowego pupilka w lisæie
				CarDescriptor *pupilek = (CarDescriptor *)(message.descriptor);

				carsOnRoadsFartherToCloser.push_back(pupilek);
				//Okreœlanie wspó³rzêdnych

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
			//Jeœli samochód opóœci³ drogê od strony dalsego. to usuñ go z drogi
			else if(message.messageType == OUTGOING)
			{
				carsOnRoadsCloserToFarther.pop_front();
				fartherWaiting = false;
				continue;
			}
		}

		//Przesówanie samochodów
		//W  Poziomie
		if(direction == HORRIZONTAL)
		{
			if(!carsOnRoadsCloserToFarther.empty())
			{
				std::list<CarDescriptor*>::iterator elier = carsOnRoadsCloserToFarther.begin();
				std::list<CarDescriptor*>::iterator later = carsOnRoadsCloserToFarther.begin();

				//Jeœli to zasz³o to znaczy ¿e samochód stoi ju¿ przy szkrzy¿owaniu
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

				//Jeœli to zasz³o to znaczy ¿e samochód stoi ju¿ przy szkrzy¿owaniu
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

				//Jeœli to zasz³o to znaczy ¿e samochód stoi ju¿ przy szkrzy¿owaniu
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

				//Jeœli to zasz³o to znaczy ¿e samochód stoi ju¿ przy szkrzy¿owaniu
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

		//Zbieranie info o po³o¿eniu i wysy³anie do rysuj¹cego
		
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
	//Zapisanie d³ugoœci œcie¿ki
	roadLength = dijxtraArray[begin][1][target];
	int buffer = target;

	//Zapisanie kolejnych elementów œcie¿ki
	while(buffer != -1)
	{
		road.push_front(buffer);
		buffer = dijxtraArray[begin][2][buffer];
	}

	//Usówanie startowego bo zostawiamy zawsze cel
	road.pop_front();

	while(1)
	{
		MessageDescriptor message;
		//Odbieram wiadomoœæ
		message = Concurrency::receive(input);

		//Jeœli finish to znaczy ¿e koniec
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
		//Jeœli welcome to znaczy ¿e na nowej drodze
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
		//Jeœli entering zanczy ¿e trzeba przedstawiæ siê nowej drodze
		else if(message.messageType ==ENTERING)
		{
			//Jeœli to pierwszy raz zapisz startowy czas
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
	//Ryliser uruchamiaj¹cy nasze skrzy¿owanie dwukrotnie czêœciej ni¿ drogê
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

			//Jeœli nie ma oczekuj¹cych na rozpoczêcie wjazdu to srpawdŸ czy nie 
			if(waitings[4] == NULL)
			{
				//Jeœli ktoœ jednak chce wjechaæ
				if(Concurrency::try_receive(crossroadsInput[4], message))
				{
					waitings[4] = (CarDescriptor *)message.descriptor;
					waitingsDirection[4] = findDirction(waitings[4]);
				}
			}

			//Jeœli dosta³em jakiegoœ wje¿d¿aj¹cego staram siê go ulokowaæ jeœli mi siê nie uda to staram siê roz³adowywaæ ruch
			if(waitings[4] != NULL)
			{
				//Jeœli przyby³y jest w celu to go skoñcz nie powinno to mieæ miejsca ale lepiej to ni¿ wywalic app
				if(waitingsDirection[4]==-1)
				{
					MessageDescriptor finishMessage;
					finishMessage.messageType = FINISH;
					Concurrency::asend(waitings[4]->input, finishMessage);

					waitings[4] = NULL;
				}

				//A jeœli nie równa siê null to trzeba zagajaæ do drogi
				else
				{
					MessageDescriptor carMessage;
					carMessage.messageType = CAR;

					Concurrency::asend(crossroadsOutput[waitingsDirection[4]], carMessage);

					carMessage = Concurrency::receive(crossroadsInput[waitingsDirection[4]]);

					//Jeœli jest miejsce to wyœlj tam samochód
					if(carMessage.messageType == SPACE)
					{
						carMessage.messageType = ENTERING;
						carMessage.target = &crossroadsOutput[waitingsDirection[4]];

						Concurrency::asend(waitings[4]->input, carMessage);

						waitings[4] = NULL;
					}
				}
			}

			
			//Teraz przystêpujemy do kierowania ruchem normalnym
			//Zbieranie oczekuj¹cych
			for(int i = 0; i < 4; i++)
			{
				//Jeœli nie ma ju¿ oczekuj¹cego i s¹siad nie jest NULLEM to sprawdŸ czy nie masz wiadomoœci
				if(waitings[i] == NULL && neighbors[i] != NULL)
				{
					MessageDescriptor inputMessage;

					//Jeœli dosta³em wiadomoœæ to dodaj do oczekuj¹cych 
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

			//Sprawdzamy czy ktoœ nie dotar³ ju¿ do celu
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

			
			//Roz³adowywanie skrzy¿owania pozornie nieskoñczone 
			while(1)
			{
				bool someoneWent = false;
				int stopReason[4];
				//zerowanie stop reson co próba bo mo¿e coœ siê przesunê³o
				for(int i = 0 ; i < 4; i++)
					stopReason[i] = 0;

				//Najpierw sprawdzanie prawoskrêtnych
				for(int i = 0; i < 4; i++)
				{
					if(waitings[i] != NULL && waitingTurnDirection[i] == RIGHT)
					{
						MessageDescriptor carMessage;
						carMessage.messageType = CAR;

						Concurrency::asend(crossroadsOutput[waitingsDirection[i]], carMessage);

						carMessage = Concurrency::receive(crossroadsInput[waitingsDirection[i]]);

						//Jeœli jest miejsce to wyœlj tam samochód
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
				}//Prawoskrêtni

				//Potem jad¹cych prosto
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

							//Jeœli jest miejsce to wyœlj tam samochód
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
						}//Sprawdzanie prawego s¹siada
						else
						{
							stopReason[i] = BLOCK;
						}
					}
				}//Prosci

				//Na koniec lewoskrêtni
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

							//Jeœli jest miejsce to wyœlj tam samochód
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
						}//Sprawdzanie prawego s¹siada
						else
						{
							stopReason[i] = BLOCK;
						}
					}
				}//Prosci

				//Jeœli ktoœ pojecha³ to kontynuuj
				if(someoneWent)
					continue;

				//Jeœli nikt nie pojecha³ to sprawdŸ powody jeœli choæ jeden jest po prostu zablokowany to go puœæ a jak nie to koñcz
				for(int i = 0 ; i < 4 ; i ++)
				{
					if(waitings[i] != NULL && stopReason[i] == BLOCK)
					{
						MessageDescriptor carMessage;
						carMessage.messageType = CAR;

						Concurrency::asend(crossroadsOutput[waitingsDirection[i]], carMessage);

						carMessage = Concurrency::receive(crossroadsInput[waitingsDirection[i]]);

						//Jeœli jest miejsce to wyœlj tam samochód
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
				}//Sprawdzanie czy jest ktoœ kogo trzeba przepchn¹æ

				//Jeœli mimo to nikt nie pojecha³ to idziemy spaæ
				if(!someoneWent)
					break;

			}//Roz³adowywanie skrzy¿owania

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