#include "mainwindow.h"

MainWindow::MainWindow(QWidget *parent, Qt::WFlags flags)
	: QMainWindow(parent, flags), drawingSpace(roads, drawingSpaceInput)
{
	ui.setupUi(this);

	setWindowFlags(windowFlags() ^ Qt::WindowMaximizeButtonHint);

	for(int i = 0 ; i < 29; i ++)
		crossroads[i] = new CrossroadsDescriptor(i, mainAgentInput);

	started = false;

	ui.visualisationLayout->addWidget(&drawingSpace);	

	numberOfCars = 0;
	carsThatReturned = 0;
	speed = 0;
}

MainWindow::~MainWindow()
{

}

void MainWindow::init()
{
	//skrzyzowania
	crossroads[0]->x =180;
	crossroads[0]->y =20;
	crossroads[1]->x = 420;
	crossroads[1]->y =20;
	crossroads[2]->x = 580;
	crossroads[2]->y =20;
	crossroads[3]->x = 700;
	crossroads[3]->y =20;
	crossroads[4]->x = 180;
	crossroads[4]->y =140;
	crossroads[5]->x = 420;
	crossroads[5]->y =140;
	crossroads[6]->x = 580;
	crossroads[6]->y =140;
	crossroads[7]->x = 700;
	crossroads[7]->y =140;
	crossroads[8]->x = 820;
	crossroads[8]->y =140;
	crossroads[9]->x = 180;
	crossroads[9]->y = 250;
	crossroads[10]->x = 420;
	crossroads[10]->y = 250;
	crossroads[11]->x = 580;
	crossroads[11]->y =340;
	crossroads[12]->x = 700;
	crossroads[12]->y =340;
	crossroads[13]->x = 820;
	crossroads[13]->y = 340;
	crossroads[14]->x = 20;
	crossroads[14]->y = 380;
	crossroads[15]->x = 180;
	crossroads[15]->y = 380;
	crossroads[16]->x = 500;
	crossroads[16]->y =500;
	crossroads[17]->x = 700;
	crossroads[17]->y =500;
	crossroads[18]->x = 180;
	crossroads[18]->y =540;
	crossroads[19]->x = 420;
	crossroads[19]->y = 540;
	crossroads[20]->x = 500;
	crossroads[20]->y = 540;
	crossroads[21]->x = 660;
	crossroads[21]->y = 620;
	crossroads[22]->x = 700;
	crossroads[22]->y = 620;
	crossroads[23]->x = 820;
	crossroads[23]->y = 620;
	crossroads[24]->x = 180;
	crossroads[24]->y = 700;
	crossroads[25]->x = 420;
	crossroads[25]->y = 700;
	crossroads[26]->x = 500;
	crossroads[26]->y = 700;
	crossroads[27]->x = 660;
	crossroads[27]->y = 700;
	//neighborts

	//Punkty startowe
	startPoint[0] = crossroads[0];
	startPoint[1] = crossroads[1];
	startPoint[2] = crossroads[2];
	startPoint[3] = crossroads[3];
	startPoint[4] = crossroads[8];
	startPoint[5] = crossroads[13];
	startPoint[6] = crossroads[23];
	startPoint[7] = crossroads[27];
	startPoint[8] = crossroads[26];
	startPoint[9] = crossroads[25];
	startPoint[10] = crossroads[24];
	startPoint[11] = crossroads[14];

	//S¹siedzi
	crossroads[0]->neighbors[NORTH] = NULL;
	crossroads[0]->neighbors[WEST] =  NULL;
	crossroads[0]->neighbors[SOUTH] = crossroads[4];
	crossroads[0]->neighbors[EAST] =  NULL;
	crossroads[1]->neighbors[NORTH] =  NULL;
	crossroads[1]->neighbors[WEST] =  NULL;
	crossroads[1]->neighbors[SOUTH] = crossroads[5];
	crossroads[1]->neighbors[EAST] =  NULL;
	crossroads[2]->neighbors[NORTH] =  NULL;
	crossroads[2]->neighbors[WEST] =  NULL;
	crossroads[2]->neighbors[SOUTH] = crossroads[6];
	crossroads[2]->neighbors[EAST] =  NULL;
	crossroads[3]->neighbors[NORTH] =  NULL;
	crossroads[3]->neighbors[WEST] =  NULL;
	crossroads[3]->neighbors[SOUTH] = crossroads[7];
	crossroads[3]->neighbors[EAST] =  NULL;
	crossroads[4]->neighbors[NORTH] = crossroads[0];
	crossroads[4]->neighbors[WEST] =  NULL;
	crossroads[4]->neighbors[SOUTH] = crossroads[9];
	crossroads[4]->neighbors[EAST] = crossroads[5];
	crossroads[5]->neighbors[NORTH] = crossroads[1];
	crossroads[5]->neighbors[WEST] = crossroads[4];
	crossroads[5]->neighbors[SOUTH] = crossroads[10];
	crossroads[5]->neighbors[EAST] = crossroads[6];
	crossroads[6]->neighbors[NORTH] = crossroads[2];
	crossroads[6]->neighbors[WEST] = crossroads[5];
	crossroads[6]->neighbors[SOUTH] = crossroads[11];
	crossroads[6]->neighbors[EAST] = crossroads[7];
	crossroads[7]->neighbors[NORTH] = crossroads[3];
	crossroads[7]->neighbors[WEST] = crossroads[6];
	crossroads[7]->neighbors[SOUTH] = crossroads[12];
	crossroads[7]->neighbors[EAST] = crossroads[8];
	crossroads[8]->neighbors[NORTH] =  NULL;
	crossroads[8]->neighbors[WEST] = crossroads[7];
	crossroads[8]->neighbors[SOUTH] =  NULL;
	crossroads[8]->neighbors[EAST] =  NULL;
	crossroads[9]->neighbors[NORTH] = crossroads[4];
	crossroads[9]->neighbors[WEST] =  NULL;
	crossroads[9]->neighbors[SOUTH] = crossroads[15];
	crossroads[9]->neighbors[EAST] = crossroads[10];
	crossroads[10]->neighbors[NORTH] = crossroads[5];
	crossroads[10]->neighbors[WEST] = crossroads[9];
	crossroads[10]->neighbors[SOUTH] = crossroads[19];
	crossroads[10]->neighbors[EAST] =  NULL;
	crossroads[11]->neighbors[NORTH] = crossroads[6];
	crossroads[11]->neighbors[WEST] =  NULL;
	crossroads[11]->neighbors[SOUTH] =  NULL;
	crossroads[11]->neighbors[EAST] = crossroads[12];
	crossroads[12]->neighbors[NORTH] = crossroads[7];
	crossroads[12]->neighbors[WEST] = crossroads[11];
	crossroads[12]->neighbors[SOUTH] = crossroads[17];
	crossroads[12]->neighbors[EAST] = crossroads[13];
	crossroads[13]->neighbors[NORTH] =  NULL;
	crossroads[13]->neighbors[WEST] = crossroads[12];
	crossroads[13]->neighbors[SOUTH] =  NULL;
	crossroads[13]->neighbors[EAST] =  NULL;
	crossroads[14]->neighbors[NORTH] =  NULL;
	crossroads[14]->neighbors[WEST] =  NULL;
	crossroads[14]->neighbors[SOUTH] =  NULL;
	crossroads[14]->neighbors[EAST] = crossroads[15];
	crossroads[15]->neighbors[NORTH] = crossroads[9];
	crossroads[15]->neighbors[WEST] = crossroads[14];
	crossroads[15]->neighbors[SOUTH] = crossroads[18];
	crossroads[15]->neighbors[EAST] =  NULL;
	crossroads[16]->neighbors[NORTH] =  NULL;
	crossroads[16]->neighbors[WEST] =  NULL;
	crossroads[16]->neighbors[SOUTH] = crossroads[20];
	crossroads[16]->neighbors[EAST] = crossroads[17];
	crossroads[17]->neighbors[NORTH] = crossroads[12];
	crossroads[17]->neighbors[WEST] = crossroads[16];
	crossroads[17]->neighbors[SOUTH] = crossroads[22];
	crossroads[17]->neighbors[EAST] =  NULL;
	crossroads[18]->neighbors[NORTH] = crossroads[15];
	crossroads[18]->neighbors[WEST] =  NULL;
	crossroads[18]->neighbors[SOUTH] = crossroads[24];
	crossroads[18]->neighbors[EAST] = crossroads[19];
	crossroads[19]->neighbors[NORTH] = crossroads[10];
	crossroads[19]->neighbors[WEST] = crossroads[18];
	crossroads[19]->neighbors[SOUTH] = crossroads[25];
	crossroads[19]->neighbors[EAST] = crossroads[20];
	crossroads[20]->neighbors[NORTH] = crossroads[16];
	crossroads[20]->neighbors[WEST] = crossroads[19];
	crossroads[20]->neighbors[SOUTH] = crossroads[26];
	crossroads[20]->neighbors[EAST] =  NULL;
	crossroads[21]->neighbors[NORTH] =  NULL;
	crossroads[21]->neighbors[WEST] =  NULL;
	crossroads[21]->neighbors[SOUTH] = crossroads[27];
	crossroads[21]->neighbors[EAST] = crossroads[22];
	crossroads[22]->neighbors[NORTH] = crossroads[17];
	crossroads[22]->neighbors[WEST] = crossroads[21];
	crossroads[22]->neighbors[SOUTH] =  NULL;
	crossroads[22]->neighbors[EAST] = crossroads[23];
	crossroads[23]->neighbors[NORTH] =  NULL;
	crossroads[23]->neighbors[WEST] = crossroads[22];
	crossroads[23]->neighbors[SOUTH] =  NULL;
	crossroads[23]->neighbors[EAST] =  NULL;
	crossroads[24]->neighbors[NORTH] =  crossroads[18];
	crossroads[24]->neighbors[WEST] =  NULL;
	crossroads[24]->neighbors[SOUTH] = NULL;
	crossroads[24]->neighbors[EAST] = NULL;
	crossroads[25]->neighbors[NORTH] = crossroads[19];
	crossroads[25]->neighbors[WEST] = NULL;
	crossroads[25]->neighbors[SOUTH] = NULL;
	crossroads[25]->neighbors[EAST] = NULL;
	crossroads[26]->neighbors[NORTH] = crossroads[20];
	crossroads[26]->neighbors[WEST] = NULL;
	crossroads[26]->neighbors[SOUTH] = NULL;
	crossroads[26]->neighbors[EAST] = NULL;
	crossroads[27]->neighbors[NORTH] = crossroads[21];
	crossroads[27]->neighbors[WEST] = NULL;
	crossroads[27]->neighbors[SOUTH] = NULL;
	crossroads[27]->neighbors[EAST] = NULL;

	//Drogi
	roads.push_back(new RoadDescriptor(120,crossroads[0],crossroads[4], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(120,crossroads[1],crossroads[5], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(120,crossroads[2],crossroads[6], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(120,crossroads[3],crossroads[7], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(240,crossroads[4],crossroads[5], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(160,crossroads[5],crossroads[6], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(120,crossroads[6],crossroads[7], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(120,crossroads[7],crossroads[8], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(120,crossroads[4],crossroads[9], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(120,crossroads[5],crossroads[10], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(200,crossroads[6],crossroads[11], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(200,crossroads[7],crossroads[12], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(240,crossroads[9],crossroads[10], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(120,crossroads[9],crossroads[15], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(160,crossroads[14],crossroads[15], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(120,crossroads[11],crossroads[12], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(120,crossroads[12],crossroads[13], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(160,crossroads[12],crossroads[17], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(200,crossroads[16],crossroads[17], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(120,crossroads[17],crossroads[22], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(120,crossroads[22],crossroads[23], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(40,crossroads[21],crossroads[22], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(80,crossroads[21],crossroads[27], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(160,crossroads[20],crossroads[26], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(40,crossroads[16],crossroads[20], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(80,crossroads[19],crossroads[20], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(160,crossroads[19],crossroads[25], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(240,crossroads[18],crossroads[19], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(160,crossroads[18],crossroads[24], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(160,crossroads[15],crossroads[18], drawingSpaceInput));
	roads.push_back(new RoadDescriptor(280,crossroads[10],crossroads[19], drawingSpaceInput));

	//S¹siedztwa dróg
	crossroads[0]->roads[NORTH] = NULL;
	crossroads[0]->roads[WEST] =  NULL;
	crossroads[0]->roads[SOUTH] = roads[0];
	crossroads[0]->roads[EAST] =  NULL;
	crossroads[1]->roads[NORTH] =  NULL;
	crossroads[1]->roads[WEST] =  NULL;
	crossroads[1]->roads[SOUTH] = roads[1];
	crossroads[1]->roads[EAST] =  NULL;
	crossroads[2]->roads[NORTH] =  NULL;
	crossroads[2]->roads[WEST] =  NULL;
	crossroads[2]->roads[SOUTH] = roads[2];
	crossroads[2]->roads[EAST] =  NULL;
	crossroads[3]->roads[NORTH] =  NULL;
	crossroads[3]->roads[WEST] =  NULL;
	crossroads[3]->roads[SOUTH] = roads[3];
	crossroads[3]->roads[EAST] =  NULL;
	crossroads[4]->roads[NORTH] = roads[0];
	crossroads[4]->roads[WEST] =  NULL;
	crossroads[4]->roads[SOUTH] = roads[8];
	crossroads[4]->roads[EAST] = roads[4];
	crossroads[5]->roads[NORTH] = roads[1];
	crossroads[5]->roads[WEST] = roads[4];
	crossroads[5]->roads[SOUTH] = roads[9];
	crossroads[5]->roads[EAST] = roads[5];
	crossroads[6]->roads[NORTH] = roads[2];
	crossroads[6]->roads[WEST] = roads[5];
	crossroads[6]->roads[SOUTH] = roads[10];
	crossroads[6]->roads[EAST] = roads[6];
	crossroads[7]->roads[NORTH] = roads[3];
	crossroads[7]->roads[WEST] = roads[6];
	crossroads[7]->roads[SOUTH] = roads[11];
	crossroads[7]->roads[EAST] = roads[7];
	crossroads[8]->roads[NORTH] =  NULL;
	crossroads[8]->roads[WEST] = roads[7];
	crossroads[8]->roads[SOUTH] =  NULL;
	crossroads[8]->roads[EAST] =  NULL;
	crossroads[9]->roads[NORTH] = roads[8];
	crossroads[9]->roads[WEST] =  NULL;
	crossroads[9]->roads[SOUTH] = roads[13];
	crossroads[9]->roads[EAST] = roads[12];
	crossroads[10]->roads[NORTH] = roads[9];
	crossroads[10]->roads[WEST] = roads[12];
	crossroads[10]->roads[SOUTH] = roads[30];
	crossroads[10]->roads[EAST] =  NULL;
	crossroads[11]->roads[NORTH] = roads[10];
	crossroads[11]->roads[WEST] =  NULL;
	crossroads[11]->roads[SOUTH] =  NULL;
	crossroads[11]->roads[EAST] = roads[15];
	crossroads[12]->roads[NORTH] = roads[11];
	crossroads[12]->roads[WEST] = roads[15];
	crossroads[12]->roads[SOUTH] = roads[17];
	crossroads[12]->roads[EAST] = roads[16];
	crossroads[13]->roads[NORTH] =  NULL;
	crossroads[13]->roads[WEST] = roads[16];
	crossroads[13]->roads[SOUTH] =  NULL;
	crossroads[13]->roads[EAST] =  NULL;
	crossroads[14]->roads[NORTH] =  NULL;
	crossroads[14]->roads[WEST] =  NULL;
	crossroads[14]->roads[SOUTH] =  NULL;
	crossroads[14]->roads[EAST] = roads[14];
	crossroads[15]->roads[NORTH] = roads[13];
	crossroads[15]->roads[WEST] = roads[14];
	crossroads[15]->roads[SOUTH] = roads[29];
	crossroads[15]->roads[EAST] =  NULL;
	crossroads[16]->roads[NORTH] =  NULL;
	crossroads[16]->roads[WEST] =  NULL;
	crossroads[16]->roads[SOUTH] = roads[24];
	crossroads[16]->roads[EAST] = roads[18];
	crossroads[17]->roads[NORTH] = roads[17];
	crossroads[17]->roads[WEST] = roads[18];
	crossroads[17]->roads[SOUTH] = roads[19];
	crossroads[17]->roads[EAST] =  NULL;
	crossroads[18]->roads[NORTH] = roads[29];
	crossroads[18]->roads[WEST] =  NULL;
	crossroads[18]->roads[SOUTH] = roads[28];
	crossroads[18]->roads[EAST] = roads[27];
	crossroads[19]->roads[NORTH] = roads[30];
	crossroads[19]->roads[WEST] = roads[27];
	crossroads[19]->roads[SOUTH] = roads[26];
	crossroads[19]->roads[EAST] = roads[25];
	crossroads[20]->roads[NORTH] = roads[24];
	crossroads[20]->roads[WEST] = roads[25];
	crossroads[20]->roads[SOUTH] = roads[23];
	crossroads[20]->roads[EAST] =  NULL;
	crossroads[21]->roads[NORTH] =  NULL;
	crossroads[21]->roads[WEST] =  NULL;
	crossroads[21]->roads[SOUTH] = roads[22];
	crossroads[21]->roads[EAST] = roads[21];
	crossroads[22]->roads[NORTH] = roads[19];
	crossroads[22]->roads[WEST] = roads[21];
	crossroads[22]->roads[SOUTH] =  NULL;
	crossroads[22]->roads[EAST] = roads[20];
	crossroads[23]->roads[NORTH] =  NULL;
	crossroads[23]->roads[WEST] = roads[20];
	crossroads[23]->roads[SOUTH] =  NULL;
	crossroads[23]->roads[EAST] =  NULL;
	crossroads[24]->roads[NORTH] = roads[28];
	crossroads[24]->roads[WEST] =  NULL;
	crossroads[24]->roads[SOUTH] = NULL;
	crossroads[24]->roads[EAST] = NULL;
	crossroads[25]->roads[NORTH] = roads[26];
	crossroads[25]->roads[WEST] = NULL;
	crossroads[25]->roads[SOUTH] = NULL;
	crossroads[25]->roads[EAST] = NULL;
	crossroads[26]->roads[NORTH] = roads[23];
	crossroads[26]->roads[WEST] = NULL;
	crossroads[26]->roads[SOUTH] = NULL;
	crossroads[26]->roads[EAST] = NULL;
	crossroads[27]->roads[NORTH] = roads[22];
	crossroads[27]->roads[WEST] = NULL;
	crossroads[27]->roads[SOUTH] = NULL;
	crossroads[27]->roads[EAST] = NULL;

	

	dijkstra();
}

void MainWindow::dijkstra()
{

	for(int nods = 0; nods < 28; nods++)
	{
		for(int record = 0; record<28; record++)
		{
			dijkstraResults[nods][0][record] = record;
			dijkstraResults[nods][1][record] = -1;
			dijkstraResults[nods][2][record] = -1;
			dijkstraResults[nods][3][record] = 0;
		}
	}

	for(int start = 0 ; start<28; start++)
	{
		dijkstraResults[start][1][start] = 0;

		  
		while(1)
		{
			//Zmienne do buforowania
			int test = -1;
			int length = -1;

			//Wybieranie aktualnie o najmniejszej drodze
			for(int index = 0 ; index < 28; index++)
			{
				if(!dijkstraResults[start][3][index] && dijkstraResults[start][1][index] != -1)
				{
					if(length == -1 ||dijkstraResults[start][1][index] <= length )
					{
						test = index;
						length = dijkstraResults[start][1][index];
					}
				}
			}
			//Jeœli nie znaleziono ¿adnego do stestowania zacznij dla nastêpnego 
			if(test < 0)
				break;

			dijkstraResults[start][3][test] = 1;

			//sprawdzanie s¹siadów
			for(int index = 0; index < 4; index++)
			{
				//skrot aby nie wypisywac tonow kodu
				if(crossroads[test]->neighbors[index] != NULL)
				{
					int chackingNeighbourId = crossroads[test]->neighbors[index]->id;

					if(dijkstraResults[start][1][chackingNeighbourId] == -1 || dijkstraResults[start][1][chackingNeighbourId] > length + crossroads[test]->roads[index]->size)
					{
						dijkstraResults[start][1][chackingNeighbourId] = length + crossroads[test]->roads[index]->size;
						dijkstraResults[start][2][chackingNeighbourId] = test;
					}

				}
			}


			
		}
		
	}
}

void MainWindow::buttonClicked()
{
	//Rozpoczynamy prezentacje
	if(!started)
	{
		ui.okButton->setText(QString("EXIT"));

		numberOfCars =  ui.carNumber->value();

		//To równie¿ startuje odrysowywanie
		drawingSpace.setNumberOfCars(numberOfCars);

		ui.carNumber->setValue(carsThatReturned);

		QString labelText;

		labelText += "0 KM/H";

		ui.avSpeddLabel->setText(labelText);


		//Startowanie
		for(int i = 0 ; i < 28; i++)
			crossroads[i]->start();

		for(int i = 0 ; i < roads.size(); i++)
			roads[i]->start();
		srand(time(NULL));

		bool test;

		for(int i = 0 ; i < numberOfCars; i++)
		{
			CarDescriptor *buffer = new CarDescriptor(&mainAgentInput, i);
			int startPosition = rand()%12;
			int endPosition = rand()%12;
			while(endPosition == startPosition)
			{
				endPosition = rand()%12;
			}

			buffer->begin = startPoint[startPosition]->id;
			buffer->started = startPosition;
			buffer->target = startPoint[endPosition]->id;
			buffer->dijxtraArray = dijkstraResults;

			allCars.push_back(buffer);
			carsOnStartPosition[startPosition].push_back(buffer);

			MessageDescriptor startMessage;
			startMessage.messageType = CAR;
			startMessage.descriptor = buffer;

			buffer->start();

			test  = Concurrency::send(startPoint[startPosition]->crossroadsInput[4], startMessage);

		}

		startTimer(333);

		started = true;


	}
	else
		exit(0);
}

void MainWindow::timerEvent(QTimerEvent *event)
{
	event->accept();

	//Zbieranie info o skoñczonych samochodach
	
	MessageDescriptor message;

	while(Concurrency::try_receive(mainAgentInput, message))
	{
		if(message.messageType == FINISH)
		{
			CarDescriptor *car = (CarDescriptor *)message.descriptor;

			carsThatReturned ++;
			speed += car->avarageSpeed;

			ui.carNumber->setValue(carsThatReturned);

			QString labelText;

			double wholeAvaradgeSpeed;

			if(carsThatReturned)
				wholeAvaradgeSpeed = speed/carsThatReturned;
			else
				wholeAvaradgeSpeed = 0;

			std::stringstream sstr;

			sstr << wholeAvaradgeSpeed;

			std::string buffer = sstr.str();
			

			labelText +=QString(buffer.c_str());
			labelText += " KM/H";

			ui.avSpeddLabel->setText(labelText);

			DrawingInfo info;

			info.id = car->id;
			info.x = -40;
			info.y = -40;

			Concurrency::asend(drawingSpaceInput, info);
		}
		else
			bool test = false;
	}


		

}

