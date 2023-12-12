/* @file "myDemoPong_AM.c"
 * This is the user code for Module myDemoPong_AM
 */

#include <stdio.h>
#include <signal.h>
#include <stdlib.h>
#include <unistd.h>
#include "ldp_mod_container_util.h"
#include <stdarg.h>
#include "../inc-gen/myDemoPong_AM.h"

static void print_log(myDemoPong_AM__context* context, const char *format, ...){
    va_list vl;
    ECOA__log log;

    va_start(vl, format);
    vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
    va_end( vl);

  myDemoPong_AM_container__log_trace(context, log);
}
/* The following functions must be implemented by this module: */

/* Entrypoints for lifecycle events */
void myDemoPong_AM__INITIALIZE__received(myDemoPong_AM__context* context)
{
   /* One-shot initialisation activities: */
   /* @TODO TODO - To be implemented */

   /* Call REINITIALIZE entry-point: */
	context->user.nb_received_req=0;
}

void myDemoPong_AM__START__received(myDemoPong_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void myDemoPong_AM__STOP__received(myDemoPong_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void myDemoPong_AM__SHUTDOWN__received(myDemoPong_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}





/* Entrypoints for module operations */
void
myDemoPong_AM__Ping__request_received (
  myDemoPong_AM__context* context,
  const ECOA__uint32 ID
  ,
  const pingpong__T_2D_Position *Ping_Position
  ,
  ECOA__uint32 Ping_Target
)
{
   /* @TODO TODO - To be implemented */
	context->user.nb_received_req++;

	ECOA__uint32 new_Ping = Ping_Target+1;
	//printf("received request :  %i\n",context->user.nb_received_req);
	myDemoPong_AM_container__Ping__response_send(context, ID, Ping_Position, new_Ping);
	if(context->user.nb_received_req ==360){
		print_log(context, "\033[1;32m SUCCESS \033[0m");
        ldp_kill_platform((ldp_module_context*)context->platform_hook);
	}

}



