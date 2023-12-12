/* @file "myDemoPing_AM.c"
 * This is the user code for Module myDemoPing_AM
 */

#include "myDemoPing_AM.h"
//#include "ecoalib.h"
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
 #include <unistd.h>
#include "ldp_mod_container_util.h"
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


/* The following functions must be implemented by this module: */

/* Entrypoints for lifecycle events */
void myDemoPing_AM__INITIALIZE__received(myDemoPing_AM__context* context)
{
   /* One-shot initialisation activities: */
   /* @TODO TODO - To be implemented */
	context->user.pong_received=0;

}

void myDemoPing_AM__START__received(myDemoPing_AM__context* context)
{
   /* @TODO TODO - To be implemented */
	int i;

	lib__Test_array_10 t_array_10;
	for(i=0;i<lib__Test_array_10_MAXSIZE;i++){
		t_array_10[i]=i;
	}

	lib__Test_array_11 t_array_11;
	for(i=0;i<lib__Test_array_11_MAXSIZE;i++){
		t_array_11[i]=i;
	}


	lib__Test_array_12 t_array_12;
	for(i=0;i<lib__Test_array_12_MAXSIZE;i++){
		t_array_12[i]=i;
	}


	lib__Test_array_13 t_array_13;
	for(i=0;i<lib__Test_array_13_MAXSIZE;i++){
		t_array_13[i]=i;
	}


	lib__Test_array_14 t_array_14;
	for(i=0;i<lib__Test_array_14_MAXSIZE;i++){
		t_array_14[i]=i;
	}


	lib__Test_array_15 t_array_15;
	for(i=0;i<lib__Test_array_15_MAXSIZE;i++){
		t_array_15[i]=i;
	}


	lib__Test_array_16 t_array_16;
	for(i=0;i<lib__Test_array_16_MAXSIZE;i++){
		t_array_16[i]=i;
	}
	apr_sleep(200000);
	myDemoPing_AM_container__Ping_array_10__send(context, (const lib__Test_array_10*) &t_array_10);
	myDemoPing_AM_container__Ping_array_10__send(context, (const lib__Test_array_10*) &t_array_10);
	myDemoPing_AM_container__Ping_array_11__send(context, (const lib__Test_array_11*) &t_array_11);
	myDemoPing_AM_container__Ping_array_12__send(context, (const lib__Test_array_12*) &t_array_12);
	myDemoPing_AM_container__Ping_array_13__send(context, (const lib__Test_array_13*) &t_array_13);
	myDemoPing_AM_container__Ping_array_14__send(context, (const lib__Test_array_14*) &t_array_14);
	myDemoPing_AM_container__Ping_array_15__send(context, (const lib__Test_array_15*) &t_array_15);
	myDemoPing_AM_container__Ping_array_16__send(context, (const lib__Test_array_16*) &t_array_16);



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
myDemoPing_AM__Pong__received (
  myDemoPing_AM__context* context
 )
{
   /* @TODO TODO - To be implemented */
	context->user.pong_received++;
	print_log(context, "	received Pong %i!!", context->user.pong_received);
	if(context->user.pong_received==8){
		print_log(context, "\033[1;32m SUCCESS \033[0m");
        ldp_kill_platform((ldp_module_context*)context->platform_hook);
	}
}



