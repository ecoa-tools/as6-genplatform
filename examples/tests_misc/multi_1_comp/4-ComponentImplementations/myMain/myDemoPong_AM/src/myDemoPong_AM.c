/* @file "myDemoPong_AM.c"
 * This is the user code for Module myDemoPong_AM
 */

#include "../inc-gen/myDemoPong_AM.h"
#include <stdio.h>
#include <stdarg.h>

static void print_log(myDemoPong_AM__context* context, const char *format, ...){
    va_list vl;
    ECOA__log log;

    va_start(vl, format);
    vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
    va_end( vl);

  myDemoPong_AM_container__log_trace(context, log);
}

/* The following functions must be implemented by this module: */

/* Entrypoints for lifecycle events */
void myDemoPong_AM__INITIALIZE__received(myDemoPong_AM__context* context)
{
   /* One-shot initialisation activities: */
   /* @TODO TODO - To be implemented */

   /* Call REINITIALIZE entry-point: */
context->user.nb=0;
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



/* Entrypoints for module operations */
void
myDemoPong_AM__Ping__received (
  myDemoPong_AM__context* context
  ,
  ECOA__uint32 nb_msg
 )
{
   /* @TODO TODO - To be implemented */
		print_log(context, "ping (%i) %i", nb_msg, context->user.nb);
	context->user.nb++;
	if(context->user.nb==4){
		myDemoPong_AM_container__Pong__send(context);
		context->user.nb=0;
	}
}



