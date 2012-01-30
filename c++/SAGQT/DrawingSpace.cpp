#include "DrawingSpace.h"

//=====================================================================================================================
DrawingSpace::DrawingSpace( std::vector<RoadDescriptor * > &roadsList, Concurrency::ISource<DrawingInfo> &drawingSpaceInputRef, QWidget *parent): 
roads(roadsList), drawingSpaceInput(drawingSpaceInputRef), QWidget(parent)
{
	numberOfCars = 0;
}
//=====================================================================================================================
void DrawingSpace::paintEvent(QPaintEvent *event)
{
	event->accept();
	QPen pen(Qt::black, 20, Qt::SolidLine);
	QPainter painter(this);
	painter.setPen(pen);
	
	for(std::vector<RoadDescriptor * >::iterator iter = roads.begin(); iter!=roads.end(); iter++)
		painter.drawLine((*iter)->closer->x,(*iter)->closer->y,(*iter)->farther->x,(*iter)->farther->y);

	pen.setColor(Qt::white);
	pen.setStyle(Qt::DashLine);
	pen.setWidth(1);

	painter.setPen(pen);
	for(std::vector<RoadDescriptor * >::iterator iter = roads.begin(); iter!=roads.end(); iter++)
		painter.drawLine((*iter)->closer->x,(*iter)->closer->y,(*iter)->farther->x,(*iter)->farther->y);

	//Malowanie fantomów
	pen.setColor(Qt::green);
	pen.setStyle(Qt::SolidLine);
	pen.setWidth(1);
	painter.setPen(pen);
	QBrush brush(Qt::green);
	painter.setBrush(brush);

	for(int i = 0 ; i < numberOfCars ; i++)
	{
		QPoint center(fantoms[i].x, fantoms[i].y);

		painter.drawEllipse(center, 4,4);
	}
		
}
//=====================================================================================================================

void DrawingSpace::timerEvent(QTimerEvent *event)
{
	event->accept();

	DrawingInfo newCar;

	//Aktualizacja fantomów
	//for(int i = 0 ; i < numberOfCars && Concurrency::try_receive(drawingSpaceInput, newCar); i++)
	while(Concurrency::try_receive(drawingSpaceInput, newCar))
	{
		fantoms[newCar.id] = newCar;
	}

	repaint();
}
//=====================================================================================================================
void DrawingSpace::setNumberOfCars(int number)
{
	numberOfCars = number;

	
	//Tworzenie graficznych fantomow
	for(int i = 0 ; i < numberOfCars; i++)
	{
		DrawingInfo car;
		car.id = i;
		car.x = -40;
		car.y = -40;

		fantoms.push_back(car);
	}

	startTimer(40);
}