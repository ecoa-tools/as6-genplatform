/* Generated by PARSEC */
/* Module Implementation myDemoPong_AM */

#include "ECOA.h"
#include "myDemoPong_AM.h"

#include "pingpong.h"

/* Entry points for lifecycle operations */
void myDemoPong_AM__INITIALIZE__received(myDemoPong_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoPong_AM__START__received(myDemoPong_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoPong_AM__STOP__received(myDemoPong_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoPong_AM__SHUTDOWN__received(myDemoPong_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoPong_AM__Ping__received(myDemoPong_AM__context* context)
{
	myDemoPong_AM_container__Pong__send(context);
}
