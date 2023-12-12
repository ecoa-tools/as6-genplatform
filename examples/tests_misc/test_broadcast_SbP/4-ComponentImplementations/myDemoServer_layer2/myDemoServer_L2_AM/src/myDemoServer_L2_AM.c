/* @file "myDemoServer_L2_AM.c"
 * This is the user code for Module myDemoServer_L2_AM
 */

#include "../inc-gen/myDemoServer_L2_AM.h"
#include <stdio.h>
#include <stdarg.h>

static void print_log(myDemoServer_L2_AM__context* context, const char *format, ...){
    va_list vl;
    ECOA__log log;

    va_start(vl, format);
    vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
    va_end( vl);

  myDemoServer_L2_AM_container__log_trace(context, log);
}

/* The following functions must be implemented by this module: */

/* Entrypoints for lifecycle events */
void myDemoServer_L2_AM__INITIALIZE__received(myDemoServer_L2_AM__context* context)
{

  context->user.nb_of_pong =0;
}


void myDemoServer_L2_AM__START__received(myDemoServer_L2_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void myDemoServer_L2_AM__STOP__received(myDemoServer_L2_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void myDemoServer_L2_AM__SHUTDOWN__received(myDemoServer_L2_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}





/* Entrypoints for module operations */
void
myDemoServer_L2_AM__pong__received (
  myDemoServer_L2_AM__context* context
 )
{
   /* @TODO TODO - To be implemented */
	context->user.nb_of_pong++;
	print_log(context, " pong %i!!",context->user.nb_of_pong);
	if (context->user.nb_of_pong == 2)
		myDemoServer_L2_AM_container__finish__send(context);
}



