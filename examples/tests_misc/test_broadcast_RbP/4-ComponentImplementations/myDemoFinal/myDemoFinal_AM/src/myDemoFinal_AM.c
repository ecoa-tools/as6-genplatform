/* @file "myDemoFinal_AM.c"
 * This is the user code for Module myDemoFinal_AM
 */

#include "../inc-gen/myDemoFinal_AM.h"
#include <stdio.h>
#include <unistd.h>
#include <signal.h>
#include "ldp_mod_container_util.h"
#include <stdarg.h>

static void print_log(myDemoFinal_AM__context* context, const char *format, ...){
    va_list vl;
    ECOA__log log;

    va_start(vl, format);
    vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
    va_end( vl);

  myDemoFinal_AM_container__log_trace(context, log);
}

/* The following functions must be implemented by this module: */

/* Entrypoints for lifecycle events */
void myDemoFinal_AM__INITIALIZE__received(myDemoFinal_AM__context* context)
{
   /* One-shot initialisation activities: */
   /* @TODO TODO - To be implemented */

   /* Call REINITIALIZE entry-point: */
	context->user.nb_finish=0;
}

void myDemoFinal_AM__START__received(myDemoFinal_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void myDemoFinal_AM__STOP__received(myDemoFinal_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void myDemoFinal_AM__SHUTDOWN__received(myDemoFinal_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void myDemoFinal_AM__Finish__received(myDemoFinal_AM__context* context){
		context->user.nb_finish++;
	print_log(context, "Finish %i",context->user.nb_finish);
	if (context->user.nb_finish==2){
		usleep(1000);
		print_log(context, "\033[1;32m SUCCESS \033[1;36m (with usleep !!)\033[0m");
        ldp_kill_platform((ldp_module_context*)context->platform_hook);
	}
}



