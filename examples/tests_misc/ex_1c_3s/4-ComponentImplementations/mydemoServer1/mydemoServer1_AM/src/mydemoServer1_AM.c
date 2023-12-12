/* @file "mydemoServer1_AM.c"
 * This is the user code for Module mydemoServer1_AM
 */

#include <stdio.h>
#include "../inc-gen/mydemoServer1_AM.h"
#include <stdarg.h>

static void print_log(mydemoServer1_AM__context* context, const char *format, ...){
    va_list vl;
    ECOA__log log;

    va_start(vl, format);
    vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
    va_end( vl);

  mydemoServer1_AM_container__log_trace(context, log);
}
/* The following functions must be implemented by this module: */

/* Entrypoints for lifecycle events */
void mydemoServer1_AM__INITIALIZE__received(mydemoServer1_AM__context* context)
{
   /* One-shot initialisation activities: */
   /* @TODO TODO - To be implemented */
}

void mydemoServer1_AM__START__received(mydemoServer1_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void mydemoServer1_AM__STOP__received(mydemoServer1_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void mydemoServer1_AM__SHUTDOWN__received(mydemoServer1_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

/* Entrypoints for module operations */
void
mydemoServer1_AM__sPing__received (
  mydemoServer1_AM__context* context
 )
{
   /* @TODO TODO - To be implemented */
	print_log(context, "	mydemoServer1 received Ping !!!!");
	print_log(context, "mydemoServer1 send Pong !!!!");
	mydemoServer1_AM_container__Pong__send(context);
}



