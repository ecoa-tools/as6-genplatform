/* @file "mydemoServer0_AM.c"
 * This is the user code for Module mydemoServer0_AM
 */

#include "../inc-gen/mydemoServer0_AM.h"

#include <stdio.h>
#include <stdarg.h>

static void print_log(mydemoServer0_AM__context* context, const char *format, ...){
    va_list vl;
    ECOA__log log;

    va_start(vl, format);
    vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
    va_end( vl);

  mydemoServer0_AM_container__log_trace(context, log);
}


/* The following functions must be implemented by this module: */

/* Entrypoints for lifecycle events */
void mydemoServer0_AM__INITIALIZE__received(mydemoServer0_AM__context* context)
{
   /* One-shot initialisation activities: */
   /* @TODO TODO - To be implemented */

   /* Call REINITIALIZE entry-point: */
context->user.nb_ping=0;
}

void mydemoServer0_AM__REINITIALIZE__received(mydemoServer0_AM__context* context)
{
   /* @TODO TODO - To be implemented */



}

void mydemoServer0_AM__START__received(mydemoServer0_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void mydemoServer0_AM__STOP__received(mydemoServer0_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void mydemoServer0_AM__SHUTDOWN__received(mydemoServer0_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

/* Entrypoints for module operations */
void
mydemoServer0_AM__sPing__received (
  mydemoServer0_AM__context* context
 )
{
   /* @TODO TODO - To be implemented */
	context->user.nb_ping++;
	print_log(context, "  ping %i !!", context->user.nb_ping);
	if(context->user.nb_ping>=4)
		mydemoServer0_AM_container__finish__send(context);
}



