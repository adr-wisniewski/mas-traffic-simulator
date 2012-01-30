#ifndef CROSSROADS_DESCRIPTOR
#define CROSSROADS_DESCRIPTOR

//Sta³e okreœlaj¹ce kierunek sketu
#define RIGHT		1
#define STRAIGTH	2
#define LEFT		3

//Sta³e okreœlaj¹ce powody niejechania
#define NON		0
#define JAM		1
#define BLOCK	2

#include "EnviromentVariables.h"
#include "MessageDescriptor.h"
#include "RoadDescriptor.h"
#include "DescriptorInterface.h"
#include <agents.h>
#include "CarDescriptor.h"


class CrossroadsDescriptor: public DescriptorInterface, public Concurrency::agent
{
public:
	int id;
	int x;
	int y;

	CrossroadsDescriptor *blup;

	CrossroadsDescriptor *neighbors[4];
	RoadDescriptor *roads[4];

	Concurrency::unbounded_buffer<MessageDescriptor> crossroadsInput[5];
	Concurrency::unbounded_buffer<MessageDescriptor> crossroadsOutput[4];

	Concurrency::ITarget<MessageDescriptor> &mainAgentInput;

	CarDescriptor *waitings [5];
	int waitingsDirection [5];
	int waitingTurnDirection[4];


	CrossroadsDescriptor(int id, Concurrency::ITarget<MessageDescriptor> &mainAgentInputRef):
	mainAgentInput(mainAgentInputRef)
	{
		this->id=id;
		setType(CROSSROAD_DESCRIPTOR_TYPE);

		for(int i = 0 ; i < 5 ; i ++)
		{
			waitings[i] = NULL;
		}
	}

protected:
	void run();

private:
	int findDirction(CarDescriptor *car);
	int giveTurnDirection(int start, int destination);
};

#endif