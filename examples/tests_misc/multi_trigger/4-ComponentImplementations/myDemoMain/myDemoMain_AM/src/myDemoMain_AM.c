/* @file "myDemoMain_AM.c"
 * This is the user code for Module myDemoMain_AM
 */

#include "myDemoMain_AM.h"
#include <stdio.h>

/* The following functions must be implemented by this module: */

/* Entrypoints for lifecycle events */
void myDemoMain_AM__INITIALIZE__received(myDemoMain_AM__context* context)
{
   /* One-shot initialisation activities: */
   /* @TODO TODO - To be implemented */

   /* Call REINITIALIZE entry-point: */
}

void myDemoMain_AM__START__received(myDemoMain_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void myDemoMain_AM__STOP__received(myDemoMain_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void myDemoMain_AM__SHUTDOWN__received(myDemoMain_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}


int t0=0;
int t1=0;
/* Entrypoints for module operations */
void
myDemoMain_AM__TriggerEvent0__received (
  myDemoMain_AM__context* context
 )
{
   /* @TODO TODO - To be implemented */
	if(t0 < 100){
		t0++;
		//printf("trigger0 : %i\n",t0);
		if(t0 >=100)
			myDemoMain_AM_container__Finish__send(context);
	}
}


void
myDemoMain_AM__TriggerEvent1__received (
  myDemoMain_AM__context* context
 )
{
   /* @TODO TODO - To be implemented */
	/*ECOA__log log = {8,"trigger"};
	myDemoMain_AM_container__log_trace(context,log);*/
	if(t1 < 10){
		t1++;
		//printf("trigger1 : %i\n",t1);
		if(t1 >=10)
			myDemoMain_AM_container__Finish__send(context);
	}
}




