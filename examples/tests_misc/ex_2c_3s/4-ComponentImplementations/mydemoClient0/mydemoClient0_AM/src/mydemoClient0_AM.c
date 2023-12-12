/* @file "mydemoClient0_AM.c"
 * This is the user code for Module mydemoClient0_AM
 */

#include "../inc-gen/mydemoClient0_AM.h"
#include <stdio.h>
#include <stdarg.h>
#include <apr_time.h>

static void print_log(mydemoClient0_AM__context* context, const char *format, ...){
    va_list vl;
    ECOA__log log;

    va_start(vl, format);
    vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
    va_end( vl);

  mydemoClient0_AM_container__log_trace(context, log);
}


/* The following functions must be implemented by this module: */

/* Entrypoints for lifecycle events */
void mydemoClient0_AM__INITIALIZE__received(mydemoClient0_AM__context* context)
{
   /* One-shot initialisation activities: */
   /* @TODO TODO - To be implemented */

   /* Call REINITIALIZE entry-point: */
}

void mydemoClient0_AM__REINITIALIZE__received(mydemoClient0_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void mydemoClient0_AM__START__received(mydemoClient0_AM__context* context)
{
	print_log(context, "client0 send ping");
  apr_sleep(200000);
	mydemoClient0_AM_container__cPing__send(context);
	//mydemoClient0_AM_container__cPing__send(context);
   /* @TODO TODO - To be implemented */
}

void mydemoClient0_AM__STOP__received(mydemoClient0_AM__context* context)
{
   /* @TODO TODO - To be implemented */
	//mydemoClient0_AM_container__cPing__send(context);
	//mydemoClient0_AM_container__cPing__send(context);
}

void mydemoClient0_AM__SHUTDOWN__received(mydemoClient0_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}
