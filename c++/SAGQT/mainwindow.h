#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QtGui/QMainWindow>
#include <vector>
#include <list>
#include <agents.h>
#include<string>
#include <sstream>
#include <time.h>
#include <cstdlib>
#include "ui_mainwindow.h"
#include "EnviromentVariables.h"
#include "CrossroadsDescriptor.h"
#include "RoadDescriptor.h"
#include "DrawingSpace.h"
#include "DrawingInfo.h"


class MainWindow : public QMainWindow
{
	Q_OBJECT

public:
	MainWindow(QWidget *parent = 0, Qt::WFlags flags = 0);
	~MainWindow();
	void init();

protected:
	void timerEvent(QTimerEvent *event);

public slots:
	void buttonClicked();

private:
	/*
	pierwszy - node startowy
	podtablice okreœlij¹ (wiersz - indeks, najkrutsza droga do startu, poprzednik, czy ju¿ odwiedzono)
	*/

	bool started;

	void dijkstra();
	Ui::MainWindowClass ui;

	CrossroadsDescriptor *crossroads[28];
	CrossroadsDescriptor *startPoint[12];
	std::vector<CarDescriptor *> allCars;
	std::vector<CarDescriptor *> carsOnStartPosition[12];
	int dijkstraResults[28][4][28];
	std::vector<RoadDescriptor *> roads;
	DrawingSpace drawingSpace;

	Concurrency::unbounded_buffer<DrawingInfo> drawingSpaceInput;
	Concurrency::unbounded_buffer<MessageDescriptor> mainAgentInput;

	int numberOfCars;
	int carsThatReturned;
	double speed;
};

#endif // MAINWINDOW_H
