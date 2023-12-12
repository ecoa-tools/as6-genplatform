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
#include "apr_time.h"

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

   /* Call REINITIALIZE entry-point: */
	context->user.pong_received=0;
}

void myDemoPing_AM__START__received(myDemoPing_AM__context* context)
{
	int i;
   	//simple
   	apr_sleep(200000);
	myDemoPing_AM_container__Ping_simple__send (context,3.1415);

	// record
	lib__Test_record t_record;
	t_record.Latitude = 3.1415;
	t_record.Longitude = 12;
	myDemoPing_AM_container__Ping_record__send(context, &t_record);

	//fixed array
	lib__Test_fixed_array t_fixed_array;
	for(i=0;i<lib__Test_fixed_array_MAXSIZE;i++){
		t_fixed_array[i]=i;
	}
	myDemoPing_AM_container__Ping_fixed_array__send(context, (const lib__Test_fixed_array*) &t_fixed_array);

	//array
	lib__Test_array t_array;
	t_array.current_size= lib__Test_array_MAXSIZE/2;
	for(i=0;i<t_array.current_size;i++){
		t_array.data[i]=i;
	}
	myDemoPing_AM_container__Ping_array__send(context,&t_array);

	//enum
	lib__Test_enum t_enum = lib__Test_enum_SUNDAY;

	myDemoPing_AM_container__Ping_enum__send(context, t_enum);

	//multi
	myDemoPing_AM_container__Ping_multi_param__send (context, 3.1415, 42, &t_array);
	apr_sleep(10); // avoid to fill buffer in tcp_read function

	// variant record
	lib__Test_variant_record var_record;
	var_record.nb0=12;
	var_record.u_id.int_Sunday = 314;
	var_record.id = lib__Test_enum_SUNDAY;
	myDemoPing_AM_container__Ping_var_record__send(context, (const lib__Test_variant_record*)&var_record);
	apr_sleep(10); // avoid to fill buffer in tcp_read function

	lib__Test_variant_record var_record2;
	var_record2.nb0=12;
	var_record2.id = lib__Test_enum_SATURDAY;
	for(i=0;i<lib__Test_fixed_array_MAXSIZE;i++){
		var_record2.u_id.array_Saturday[i]=i;
	}
	myDemoPing_AM_container__Ping_var_record__send(context, &var_record2);

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

