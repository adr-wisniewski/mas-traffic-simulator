#ifndef MESSAGE_DESCRIPTOR
#define MESSAGE_DESCRIPTOR

#include <agents.h>

#define NO_MESSAGE	-1
//kierunki to typy wiadomosci jesli chodzi o skrety. To wiadomosci do skrzyzowania
//Wiadomosci do g³ównego agenta
//Od skrzy¿owania które wpóœci³o
#define START		10
//Od agenta który zakoñczy³
#define FINISH		11

//Wiadomosci do drogi od samochodu
#define ENTERING	12
#define OUTGOING	13

//Wiadomoœci do samochodu od drogi
#define WELCOME		18

//Wiadomoœci do drogi od skrzy¿owania
#define SPACE		16

//Wiadomoœci od drogi do skrzy¿owania
#define CAR			15
#define LACK		17


//Wiadomoœci techniczne
#define TIMER		14



#include "DescriptorInterface.h"
class MessageDescriptor: public DescriptorInterface
{
public:
	MessageDescriptor()
	{
		setType(MESSAGE_DESCRIPTOR_TYPE);
	}

	DescriptorInterface *descriptor;
	int messageType;
	Concurrency::ITarget<MessageDescriptor> *target;
};

#endif