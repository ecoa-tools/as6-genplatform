/* @file "myDemoPong_AM.c"
 * This is the user code for Module myDemoPong_AM
 */

#include "myDemoPong_AM.h"
//#include "ecoalib.h"
#include <stdio.h>
#include <stdarg.h>

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
}

void myDemoPong_AM__REINITIALIZE__received(myDemoPong_AM__context* context)
{
   /* @TODO TODO - To be implemented */

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

void 
myDemoPong_AM__Ping_array_10__received( 
  myDemoPong_AM__context* context
  , 
  const lib__Test_array_10 *array1
 ){
   /* @TODO TODO - To be implemented */
	print_log(context, "	Ping_array_10 received : ");
	int i;
	for(i=0;i<lib__Test_array_10_MAXSIZE;i++){
		if((*array1)[i]!=i){
			print_log(context, " FAILED array 10");
			return;
		}
	}
	myDemoPong_AM_container__Pong__send(context);
}


void 
myDemoPong_AM__Ping_array_11__received (
  myDemoPong_AM__context* context
  , 
  const lib__Test_array_11 *array1
 )
{
   /* @TODO TODO - To be implemented */
	print_log(context, "	Ping_array_11 received : ");
	int i;
	for(i=0;i<lib__Test_array_11_MAXSIZE;i++){
		if((*array1)[i]!=i){
			print_log(context, " FAILED array 11");
			return;
		}
	}
	myDemoPong_AM_container__Pong__send(context);
}


void 
myDemoPong_AM__Ping_array_12__received (
  myDemoPong_AM__context* context
  , 
  const lib__Test_array_12 *array1
 )
{
   /* @TODO TODO - To be implemented */
	print_log(context, "	Ping_array_12 received : ");
	int i;
	for(i=0;i<lib__Test_array_12_MAXSIZE;i++){
		if((*array1)[i]!=i){
			print_log(context, " FAILED array 12");
			return;
		}
	}
	myDemoPong_AM_container__Pong__send(context);
}


void 
myDemoPong_AM__Ping_array_13__received (
  myDemoPong_AM__context* context
  , 
  const lib__Test_array_13 *array1
 )
{
   /* @TODO TODO - To be implemented */
	print_log(context, "	Ping_array_13 received : ");
	int i;
	for(i=0;i<lib__Test_array_13_MAXSIZE;i++){
		if((*array1)[i]!=i){
			print_log(context, " FAILED array 13");
			return;
		}
	}
	myDemoPong_AM_container__Pong__send(context);
}


void 
myDemoPong_AM__Ping_array_14__received (
  myDemoPong_AM__context* context
  , 
  const lib__Test_array_14 *array1
 )
{
   /* @TODO TODO - To be implemented */
	print_log(context, "	Ping_array_14 received : ");
	int i;
	for(i=0;i<lib__Test_array_14_MAXSIZE;i++){
		if((*array1)[i]!=i){
			print_log(context, " FAILED array 14");
			return;
		}
	}
	myDemoPong_AM_container__Pong__send(context);
}


void 
myDemoPong_AM__Ping_array_15__received (
  myDemoPong_AM__context* context
  , 
  const lib__Test_array_15 *array1
 )
{
   /* @TODO TODO - To be implemented */
	print_log(context, "	Ping_array_15 received : ");
	int i;
	for(i=0;i<lib__Test_array_15_MAXSIZE;i++){
		if((*array1)[i]!=i){
			print_log(context, " FAILED array 15");
			return;
		}
	}
	myDemoPong_AM_container__Pong__send(context);
}


void 
myDemoPong_AM__Ping_array_16__received (
  myDemoPong_AM__context* context
  , 
  const lib__Test_array_16 *array1
 )
{
   /* @TODO TODO - To be implemented */
	print_log(context, "	Ping_array_16 received : ");
	int i;
	for(i=0;i<lib__Test_array_16_MAXSIZE;i++){
		if((*array1)[i]!=i){
			print_log(context, " FAILED array 16");
			return;
		}
	}
	myDemoPong_AM_container__Pong__send(context);
}


 
