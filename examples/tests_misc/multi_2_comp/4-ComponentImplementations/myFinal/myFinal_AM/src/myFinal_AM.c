/* @file "myFinal_AM.c"
 * This is the user code for Module myFinal_AM
 */

#include "../inc-gen/myFinal_AM.h"
#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <time.h>
#include "ldp_mod_container_util.h"
#include <stdarg.h>
#include <apr_time.h>

static void print_log(myFinal_AM__context* context, const char *format, ...){
    va_list vl;
    ECOA__log log;

    va_start(vl, format);
    vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
    va_end( vl);

  myFinal_AM_container__log_trace(context, log);
}

/* The following functions must be implemented by this module: */

/* Entrypoints for lifecycle events */
void myFinal_AM__INITIALIZE__received(myFinal_AM__context* context)
{
   /* One-shot initialisation activities: */
   /* @TODO TODO - To be implemented */

   /* Call REINITIALIZE entry-point: */
    context->user.nb=0;
    context->user.run_nb=0;
}

void myFinal_AM__START__received(myFinal_AM__context* context)
{
   /* @TODO TODO - To be implemented */
  apr_sleep(200000);
myFinal_AM_container__Run__send(context);
}

void myFinal_AM__STOP__received(myFinal_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void myFinal_AM__SHUTDOWN__received(myFinal_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}






/* Entrypoints for module operations */
void
myFinal_AM__Finish__received (
  myFinal_AM__context* context
 )
{
   /* @TODO TODO - To be implemented */
	context->user.nb++;
   /* @TODO TODO - To be implemented */
	print_log(context, "Finish %i",context->user.nb);
	if(context->user.nb==3){
		context->user.nb=0;
    print_log(context, "NB OF RUN : %i ", ++context->user.run_nb);
    if(context->user.run_nb>15){
      fflush(stdout);
      print_log(context, "\033[1;32m SUCCESS  \033[0m");
            ldp_kill_platform((ldp_module_context*)context->platform_hook);
    }else{
		  myFinal_AM_container__Run__send(context);
    }
	}

}



