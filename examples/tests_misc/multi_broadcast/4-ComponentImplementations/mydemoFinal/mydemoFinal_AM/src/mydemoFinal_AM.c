/* @file "mydemoFinal_AM.c"
 * This is the user code for Module mydemoFinal_AM
 */

#include "../inc-gen/mydemoFinal_AM.h"
#include <signal.h>
#include <stdio.h>
#include <unistd.h>

#include "ldp_mod_container_util.h"
#include <stdarg.h>

static void print_log(mydemoFinal_AM__context* context, const char *format, ...){
    va_list vl;
    ECOA__log log;

    va_start(vl, format);
    vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
    va_end( vl);

  mydemoFinal_AM_container__log_trace(context, log);
}




/* The following functions must be implemented by this module: */

/* Entrypoints for lifecycle events */
void mydemoFinal_AM__INITIALIZE__received(mydemoFinal_AM__context* context)
{
   /* One-shot initialisation activities: */
   /* @TODO TODO - To be implemented */

   /* Call REINITIALIZE entry-point: */
	context->user.nb_pong=0;
}

void mydemoFinal_AM__START__received(mydemoFinal_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void mydemoFinal_AM__STOP__received(mydemoFinal_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void mydemoFinal_AM__SHUTDOWN__received(mydemoFinal_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}


void mydemoFinal_AM__Pong__received(mydemoFinal_AM__context* context){
	context->user.nb_pong++;
	if(context->user.nb_pong >=4){
		print_log(context, "\033[1;32m SUCCESS\033[0m");
        ldp_kill_platform((ldp_module_context*)context->platform_hook);
    }

}



