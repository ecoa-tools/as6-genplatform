/* @file "mydemoServer2_AM.c"
 * This is the user code for Module mydemoServer2_AM
 */

#include "../inc-gen/mydemoServer2_AM.h"
#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include "ldp_mod_container_util.h"
#include <stdarg.h>

static void print_log(mydemoServer2_AM__context* context, const char *format, ...){
    va_list vl;
    ECOA__log log;

    va_start(vl, format);
    vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
    va_end( vl);

  mydemoServer2_AM_container__log_trace(context, log);
}

/* The following functions must be implemented by this module: */

/* Entrypoints for lifecycle events */
void mydemoServer2_AM__INITIALIZE__received(mydemoServer2_AM__context* context)
{
   /* One-shot initialisation activities: */
   /* @TODO TODO - To be implemented */

   /* Call REINITIALIZE entry-point: */
}

void mydemoServer2_AM__REINITIALIZE__received(mydemoServer2_AM__context* context)
{
   /* @TODO TODO - To be implemented */

}

void mydemoServer2_AM__START__received(mydemoServer2_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void mydemoServer2_AM__STOP__received(mydemoServer2_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void mydemoServer2_AM__SHUTDOWN__received(mydemoServer2_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

int nb_of_ping=0;
void mydemoServer2_AM__Pong__received(mydemoServer2_AM__context* context){
	print_log(context,"	mydemoServer2 Pong received!!!!");
	nb_of_ping++;
	if(nb_of_ping==3){
		print_log(context,"\033[1;32m SUCCESS \033[0m");
        ldp_kill_platform((ldp_module_context*)context->platform_hook);
	}
}


 
