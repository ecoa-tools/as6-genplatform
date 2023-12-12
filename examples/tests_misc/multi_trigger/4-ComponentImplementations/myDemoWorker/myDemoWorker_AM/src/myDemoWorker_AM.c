/* @file "myDemoWorker_AM.c"
 * This is the user code for Module myDemoWorker_AM
 */

#include "myDemoWorker_AM.h"
#include <assert.h>

/* The following functions must be implemented by this module: */

/* Entrypoints for lifecycle events */
void myDemoWorker_AM__INITIALIZE__received(myDemoWorker_AM__context* context)
{
   /* One-shot initialisation activities: */
   /* @TODO TODO - To be implemented */

   /* Call REINITIALIZE entry-point: */
	context->user.trigger0=0;
	context->user.trigger1=0;

	myDemoWorker_AM_container__get_relative_local_time(context, &context->user.xxxtime);
}

void myDemoWorker_AM__START__received(myDemoWorker_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void myDemoWorker_AM__STOP__received(myDemoWorker_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void myDemoWorker_AM__SHUTDOWN__received(myDemoWorker_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}




/* Entrypoints for module operations */

void
myDemoWorker_AM__TriggerEvent0__received (
  myDemoWorker_AM__context* context
 )
{

   /* @TODO TODO - To be implemented */
	if(context->user.trigger0 < 5){
		context->user.trigger0++;
		//printf("trigger0 event %i !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n",context->user.trigger0);
		if(context->user.trigger0 >=5)

			myDemoWorker_AM_container__Finish__send(context);

	}
}


void
myDemoWorker_AM__TriggerEvent1__received (
  myDemoWorker_AM__context* context
 )
{

	/*ECOA__hr_time time2;
	ECOA__hr_time time3;
    myDemoWorker_AM_container__get_relative_local_time(context, &time2);
	time3.seconds = time2.seconds - context->user.xxxtime.seconds;
	time3.nanoseconds = time2.nanoseconds - context->user.xxxtime.nanoseconds;
	if (time2.nanoseconds < context->user.xxxtime.nanoseconds){
		time3.seconds--;
		time3.nanoseconds += 1000000000;
	}
	ECOA__log log;
	ECOA__int32 diff =(time3.nanoseconds - 200000000);
	sprintf(log.data,"%u.%09u -> diff = %i", time3.seconds, time3.nanoseconds, diff);
	log.current_size = strlen(log.data);
	myDemoWorker_AM_container__log_trace(context,log);

	context->user.xxxtime.seconds = time2.seconds;
	context->user.xxxtime.nanoseconds = time2.nanoseconds;

	if (diff > 500000 ||  diff <  - 500000 ){
	if (context->user.trigger1 != 0)
	assert(0);
	}*/
   /* @TODO TODO - To be implemented */
	if(context->user.trigger1 < 5){
		context->user.trigger1++;
		//printf("trigger1 event %i !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n",context->user.trigger1);
		if(context->user.trigger1 >=5)

			myDemoWorker_AM_container__Finish__send(context);

	}
}

