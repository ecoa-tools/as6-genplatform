/* @file "myDemoPong_AM.c"
 * This is the user code for Module myDemoPong_AM
 */

#include "myDemoPong_AM.h"
//#include "ecoalib.h"
#include <stdio.h>
#include <math.h>
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


void myDemoPong_AM__Ping_record__received(myDemoPong_AM__context* context, const lib__Test_record* record1){
	print_log(context, "	Ping_record received :");
	if(record1->Longitude == 12.0 && fabs(record1->Latitude-3.1415) < 0.0001)
		myDemoPong_AM_container__Pong__send(context);
	else
		print_log(context, " FAILED ping_record");
}


void
myDemoPong_AM__Ping_simple__received (
  myDemoPong_AM__context* context
  ,
  lib__Test_simple param1
 )
{
	print_log(context, "	Ping_simple received : ");
	if(fabs(param1-3.1415) < 0.0001)
		myDemoPong_AM_container__Pong__send(context);
	else
		print_log(context, " FAILED ping_simple");
}


void
myDemoPong_AM__Ping_array__received (
  myDemoPong_AM__context* context
  ,
  const lib__Test_array *array1
 )
{
   /* @TODO TODO - To be implemented */
	print_log(context, "	Ping_array received : ");
	int i;
	for(i=0;i<array1->current_size;i++){
		if(array1->data[i]!=i){
			print_log(context, " FAILED array");
			return;
		}
	}
	myDemoPong_AM_container__Pong__send(context);
}


void
myDemoPong_AM__Ping_fixed_array__received (
  myDemoPong_AM__context* context
  ,
  const lib__Test_fixed_array *array1
 )
{
   /* @TODO TODO - To be implemented */
	print_log(context, "	Ping_fixed_array received : ");
	int i;
	for(i=0;i<lib__Test_fixed_array_MAXSIZE;i++){
		if((*array1)[i]!=i){
			print_log(context, " FAILED fixed array");
			return;
		}
	}
	myDemoPong_AM_container__Pong__send(context);
}


void
myDemoPong_AM__Ping_enum__received (
  myDemoPong_AM__context* context
  ,
  lib__Test_enum array1
 )
{
   /* @TODO TODO - To be implemented */
	print_log(context, "	Ping_enum received : ");
	if(array1 == lib__Test_enum_SUNDAY)
		myDemoPong_AM_container__Pong__send(context);
	else
		print_log(context, " FAILED enum");
}


void
myDemoPong_AM__Ping_multi_param__received (
  myDemoPong_AM__context* context
  ,
  lib__Test_simple param1
  ,
  ECOA__uint32 param2
  ,
  const lib__Test_array *param3
 )
{
   /* @TODO TODO - To be implemented */
	print_log(context, "	Ping_multi_param received : ");
	int i;
	if(fabs(param1-3.1415) > 0.00001 || param2 != 42){
		for(i=0;i<param3->current_size;i++){
			if(param3->data[i]!=i){
				print_log(context, "FAILED multi");
				return;
			}
		}
	}
	myDemoPong_AM_container__Pong__send(context);
}


void
myDemoPong_AM__Ping_var_record__received (
  myDemoPong_AM__context* context
  ,
  const lib__Test_variant_record *var_record
 )
{
   /* @TODO TODO - To be implemented */
	print_log(context, "	Ping_variant_record received :");
	if(var_record->nb0 != 12){
		print_log(context, " FAILED variant record 0");
		return;
	}

	if(var_record->id == lib__Test_enum_SUNDAY){
		if(var_record->u_id.int_Sunday != 314){
			print_log(context, " FAILED variant record 1");
			return;
		}
		myDemoPong_AM_container__Pong__send(context);
	}else{
		int i;
		for(i=0;i<lib__Test_fixed_array_MAXSIZE;i++){
			if(var_record->u_id.array_Saturday[i]!=i){
				print_log(context, " FAILED variant record in array : index = %i != %i",i,var_record->u_id.array_Saturday[i] );
				return;
			}
		}
		myDemoPong_AM_container__Pong__send(context);
	}

}


