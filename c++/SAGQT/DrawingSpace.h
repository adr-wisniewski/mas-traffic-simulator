#ifndef DRAWING_SPACE
#define DRAWING_SPACE

#include <qevent.h>
#include <qpoint.h>
#include <qpen.h>
#include <qpainter.h>
#include <qwidget.h>
#include <agents.h>
#include "CrossroadsDescriptor.h"
#include "DrawingInfo.h"
#include <list>
#include <vector>

class DrawingSpace:public QWidget
{
 Q_OBJECT
public:
	DrawingSpace( std::vector<RoadDescriptor * > &roadsList, Concurrency::ISource<DrawingInfo> &drawingSpaceInputRef, QWidget *parent=0);

	void setNumberOfCars(int number);

protected:
	 virtual void paintEvent(QPaintEvent *event);
	 void timerEvent(QTimerEvent *event);

private:
	std::vector<RoadDescriptor * > &roads;
	int numberOfCars;
	Concurrency::ISource<DrawingInfo> &drawingSpaceInput;
	std::vector<DrawingInfo> fantoms;

};

#endif