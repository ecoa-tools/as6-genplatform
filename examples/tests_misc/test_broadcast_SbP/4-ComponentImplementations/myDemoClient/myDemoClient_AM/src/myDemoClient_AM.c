/* @file "myDemoClient_AM.c"
 * This is the user code for Module myDemoClient_AM
 */

#include "../inc-gen/myDemoClient_AM.h"
#include <apr_time.h>
/* The following functions must be implemented by this module: */

/* Entrypoints for lifecycle events */
void myDemoClient_AM__INITIALIZE__received(myDemoClient_AM__context* context)
{
   /* One-shot initialisation activities: */
   /* @TODO TODO - To be implemented */

   /* Call REINITIALIZE entry-point: */
}

void myDemoClient_AM__REINITIALIZE__received(myDemoClient_AM__context* context)
{
   /* @TODO TODO - To be implemented */



}

void myDemoClient_AM__START__received(myDemoClient_AM__context* context)
{
   /* @TODO TODO - To be implemented */
	//usleep(100);
	apr_sleep(200000);
	myDemoClient_AM_container__ping01__send(context);
	//usleep(1000);
	myDemoClient_AM_container__ping02__send(context);
	//usleep(1000);
	myDemoClient_AM_container__ping11__send(context);
	//usleep(1000);
	myDemoClient_AM_container__ping12__send(context);
}

void myDemoClient_AM__STOP__received(myDemoClient_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void myDemoClient_AM__SHUTDOWN__received(myDemoClient_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}


