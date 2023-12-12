/* @file "myReceiverCom_AM_AM.c"
 * This is the user code for Module myReceiverCom_AM_AM
 */

#include "../inc-gen/myReceiverCom_AM_AM.h"
#include <stdio.h>
#include <stdarg.h>

static void print_log(myReceiverCom_AM_AM__context* context, const char *format, ...){
    va_list vl;
    ECOA__log log;

    va_start(vl, format);
    vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
    va_end( vl);

  myReceiverCom_AM_AM_container__log_trace(context, log);
}


/* The following functions must be implemented by this module: */

/* Entrypoints for lifecycle events */
void myReceiverCom_AM_AM__INITIALIZE__received(myReceiverCom_AM_AM__context* context)
{
   /* One-shot initialisation activities: */
   /* @TODO TODO - To be implemented */

   /* Call REINITIALIZE entry-point: */
	context->user.nb_ping=0;
}

void myReceiverCom_AM_AM__START__received(myReceiverCom_AM_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void myReceiverCom_AM_AM__STOP__received(myReceiverCom_AM_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void myReceiverCom_AM_AM__SHUTDOWN__received(myReceiverCom_AM_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

/* Entrypoints for module operations */
void
myReceiverCom_AM_AM__Ping__received (
  myReceiverCom_AM_AM__context* context
 )
{
   /* @TODO TODO - To be implemented */
	print_log(context, "Ping %i",context->user.nb_ping);
	context->user.nb_ping++;
	if(context->user.nb_ping >= 3)
		myReceiverCom_AM_AM_container__Pong__send(context);
}



