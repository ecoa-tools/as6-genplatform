/* @file "Receiver_AM.c"
 * This is the user code for Module Receiver_AM
 */

#include "../inc-gen/Receiver_AM.h"
#include <stdio.h>
#include <stdarg.h>

static void print_log(Receiver_AM__context* context, const char *format, ...){
    va_list vl;
    ECOA__log log;

    va_start(vl, format);
    vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
    va_end( vl);

  Receiver_AM_container__log_trace(context, log);
}

/* The following functions must be implemented by this module: */

/* Entrypoints for lifecycle events */
void Receiver_AM__INITIALIZE__received(Receiver_AM__context* context)
{
   /* One-shot initialisation activities: */
   /* @TODO TODO - To be implemented */

   /* Call REINITIALIZE entry-point: */
	context->user.nb_ping=0;
}

void Receiver_AM__START__received(Receiver_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void Receiver_AM__STOP__received(Receiver_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void Receiver_AM__SHUTDOWN__received(Receiver_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}



/* Entrypoints for module operations */
void
Receiver_AM__Ping__received (
  Receiver_AM__context* context
  ,
  ECOA__uint32 nb_msg
 )
{
   /* @TODO TODO - To be implemented */
	context->user.nb_ping++;
	print_log(context, "Ping %i" , context->user.nb_ping);
	if (context->user.nb_ping ==3){
		context->user.nb_ping=0;
		Receiver_AM_container__Pong__send(context);
	}
}



