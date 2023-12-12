/* @file "receiver_mod_AM.c"
 * This is the user code for Module receiver_mod_AM
 */

#include "../inc-gen/receiver_mod_AM.h"
#include <stdio.h>
#include <stdarg.h>

static void print_log(receiver_mod_AM__context* context, const char *format, ...){
    va_list vl;
    ECOA__log log;

    va_start(vl, format);
    vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
    va_end( vl);

  receiver_mod_AM_container__log_trace(context, log);
}

/* The following functions must be implemented by this module: */

/* Entrypoints for lifecycle events */
void receiver_mod_AM__INITIALIZE__received(receiver_mod_AM__context* context)
{
   /* One-shot initialisation activities: */
   /* @TODO TODO - To be implemented */

   /* Call REINITIALIZE entry-point: */
  context->user.ping_nb=0;
}

void receiver_mod_AM__START__received(receiver_mod_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void receiver_mod_AM__STOP__received(receiver_mod_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void receiver_mod_AM__SHUTDOWN__received(receiver_mod_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}



/* Entrypoints for module operations */
void
receiver_mod_AM__Ping__received (
  receiver_mod_AM__context* context
 )
{
   /* @TODO TODO - To be implemented */
	//printf("Ping\n");
	context->user.ping_nb++;
	if(context->user.ping_nb == 2){
		receiver_mod_AM_container__Trig__send(context);
		context->user.ping_nb=0;
	}

}



