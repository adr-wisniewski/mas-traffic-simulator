#ifndef ROAD_DESCRIPTOR
#define ROAD_DESCRIPTOR

#include <list>
#include "EnviromentVariables.h"
#include "DescriptorInterface.h"
#include "MessageDescriptor.h"
#include "DrawingInfo.h"
#include "CarDescriptor.h"

#define INPUT_ROAD		0
#define OUTPUT_ROAD		1

#define HORRIZONTAL		3
#define VERTICAL		2

class CrossroadsDescriptor;

class RoadDescriptor: public DescriptorInterface, public Concurrency::agent
{


public:
	int size;
	CrossroadsDescriptor *closer;
	CrossroadsDescriptor *farther;

	//Z przodu wylot z tylu wlot
	Concurrency::unbounded_buffer<MessageDescriptor> *closerComunication[2];
	Concurrency::unbounded_buffer<MessageDescriptor> *fartherComunication[2];
	Concurrency::ITarget<DrawingInfo> &drawingInfoInput;

	std::list<CarDescriptor *> carsOnRoadsCloserToFarther;
	std::list<CarDescriptor *> carsOnRoadsFartherToCloser;

	int direction;

	//Informuje czy samochód z przodu oczekuje na przekazanie do nastêpnej drogi Jeœli tru nie trzeba powtarzaæ komunikatów
	bool closerWaiting, fartherWaiting;

	RoadDescriptor(int size, CrossroadsDescriptor *closer, CrossroadsDescriptor *farther, Concurrency::ITarget<DrawingInfo> &drawingInfoInputRef);

protected:
	void run();
};
#endif