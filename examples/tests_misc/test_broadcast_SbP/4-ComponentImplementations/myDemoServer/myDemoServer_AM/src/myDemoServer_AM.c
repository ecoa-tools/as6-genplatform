/* @file "myDemoServer_AM.c"
 * This is the user code for Module myDemoServer_AM
 */

#include "../inc-gen/myDemoServer_AM.h"
#include <stdio.h>
#include <stdarg.h>

static void print_log(myDemoServer_AM__context* context, const char *format, ...){
    va_list vl;
    ECOA__log log;

    va_start(vl, format);
    vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
    va_end( vl);

  myDemoServer_AM_container__log_trace(context, log);
}

/* The following functions must be implemented by this module: */

/* Entrypoints for lifecycle events */
void myDemoServer_AM__INITIALIZE__received(myDemoServer_AM__context* context)
{
   /* One-shot initialisation activities: */
   /* @TODO TODO - To be implemented */

   /* Call REINITIALIZE entry-point: */
	context->user.ping_received=0;
}

void myDemoServer_AM__START__received(myDemoServer_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void myDemoServer_AM__STOP__received(myDemoServer_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void myDemoServer_AM__SHUTDOWN__received(myDemoServer_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}


/* Entrypoints for module operations */
void
myDemoServer_AM__ping01__received (
  myDemoServer_AM__context* context
 )
{
   /* @TODO TODO - To be implemented */
	context->user.ping_received++;
	print_log(context, " 	ping01 (%i)",context->user.ping_received);
	if (context->user.ping_received==4){
		myDemoServer_AM_container__pong__send(context);
	}
}


void
myDemoServer_AM__ping02__received (
  myDemoServer_AM__context* context
 )
{
   /* @TODO TODO - To be implemented */
	context->user.ping_received++;
	print_log(context, " 	ping02 (%i)",context->user.ping_received);
	if (context->user.ping_received==4){
		myDemoServer_AM_container__pong__send(context);
	}
}


void
myDemoServer_AM__ping11__received (
  myDemoServer_AM__context* context
 )
{
   /* @TODO TODO - To be implemented */
	context->user.ping_received++;
	print_log(context, " 	ping11 (%i)",context->user.ping_received);
	if (context->user.ping_received==4){
		myDemoServer_AM_container__pong__send(context);
	}
}


void
myDemoServer_AM__ping12__received (
  myDemoServer_AM__context* context
 )
{
   /* @TODO TODO - To be implemented */
	context->user.ping_received++;
	print_log(context, " 	ping12 (%i)",context->user.ping_received);
	if (context->user.ping_received==4){
		myDemoServer_AM_container__pong__send(context);
	}
}

