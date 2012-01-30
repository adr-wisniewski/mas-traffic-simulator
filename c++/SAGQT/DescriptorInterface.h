#ifndef DESCRIPTOR_INTERFACE
#define DESCRIPTOR_INTERFACE

#define MESSAGE_DESCRIPTOR_TYPE			0
#define CAR_DESCRIPTOR_TYPE				1
#define ROAD_DESCRIPTOR_TYPE			2
#define CROSSROAD_DESCRIPTOR_TYPE		3

class DescriptorInterface
{
public:
	int getType()
	{
		return type;
	}

protected:
	void setType(int newType)
	{
		type = newType;
	}

private:
	int type;
};
#endif