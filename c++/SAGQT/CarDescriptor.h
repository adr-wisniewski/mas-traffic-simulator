#ifndef CAR_DESCRIPTOR
#define CAR_DESCRIPTOR
#include "DescriptorInterface.h"
#include "MessageDescriptor.h"
#include <agents.h>
#include <time.h>
#include <list>

class CrossroadsDescriptor;
class RoadDescriptor;

class CarDescriptor: public DescriptorInterface, public Concurrency::agent
{
public:
	CarDescriptor(Concurrency::ITarget<MessageDescriptor> *mainAgentInputPtr, int idVal)
	{
		setType(CAR_DESCRIPTOR_TYPE);
		this->mainAgentInput = mainAgentInputPtr;
		id = idVal;

		started = true;

		outgoing = NULL;
		incoming = NULL;

		x=y=-40;
	}


	Concurrency::unbounded_buffer<MessageDescriptor> input;
	//Te w kt�rych b�d� si� wita� i �egna�
	Concurrency::ITarget<MessageDescriptor> *incoming;
	Concurrency::ITarget<MessageDescriptor> *outgoing;

	Concurrency::ITarget<MessageDescriptor> *mainAgentInput;

	//cel
	int target;
	//index w tablicy startPointow rozpoczecia
	int started;
	//id skrzy�owania startowego
	int begin;
	int id;
	int x,y;

	//dane do dijxtry
	int (*dijxtraArray)[4][28];

	//scie�ka
	std::list<int> road;

	//D�ugo�� �cie�ki
	double roadLength;


	//Czas ropzocz�cia
	time_t startTime;
	//Info czy wystartowa� ju� zegar
	bool notRunning;

	//�rednia pr�dko�� liczona po dojechaniu do celu
	double avarageSpeed;

protected:
	void run();
};
#endif