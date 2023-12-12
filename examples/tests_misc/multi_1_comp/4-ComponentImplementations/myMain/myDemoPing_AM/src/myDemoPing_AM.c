/* Generated by PARSEC */
/* Module Implementation myDemoPing_AM */

#include "ECOA.h"
#include "myDemoPing_AM.h"

#include "pingpong.h"
#include "ldp_mod_container_util.h"

#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <time.h>
#include <stdarg.h>
#include <apr_time.h>

static void print_log(myDemoPing_AM__context* context, const char *format, ...){
    va_list vl;
    ECOA__log log;

    va_start(vl, format);
    vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
    va_end( vl);

  myDemoPing_AM_container__log_trace(context, log);
}

void myDemoPing_AM__INITIALIZE__received(myDemoPing_AM__context* context)
{
   /* One-shot initialisation activities: */
   /* @TODO TODO - To be implemented */

   /* Call REINITIALIZE entry-point: */
  context->user.nb_pong=0;
}


void myDemoPing_AM__START__received(myDemoPing_AM__context* context)
{
   /* @TODO TODO - To be implemented */
  apr_sleep(200000);
myDemoPing_AM_container__sPing__send(context,context->user.nb_pong);
myDemoPing_AM_container__sPing__send(context,context->user.nb_pong);
myDemoPing_AM_container__sPing__send(context,context->user.nb_pong);
myDemoPing_AM_container__sPing__send(context,context->user.nb_pong);
}

void myDemoPing_AM__STOP__received(myDemoPing_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void myDemoPing_AM__SHUTDOWN__received(myDemoPing_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

/* Entrypoints for module operations */
void
myDemoPing_AM__sPong__received (
  myDemoPing_AM__context* context
 )
{
   /* @TODO TODO - To be implemented */
	print_log(context, "pong %i", context->user.nb_pong++);
	if(context->user.nb_pong == 30){
		fflush(stdout);
		print_log(context,"\033[1;32m SUCCESS  \033[0m");
        ldp_kill_platform((ldp_module_context*)context->platform_hook);
        return;
	}
	myDemoPing_AM_container__sPing__send(context,context->user.nb_pong);
	myDemoPing_AM_container__sPing__send(context,context->user.nb_pong);
	myDemoPing_AM_container__sPing__send(context,context->user.nb_pong);
	myDemoPing_AM_container__sPing__send(context,context->user.nb_pong);


}
