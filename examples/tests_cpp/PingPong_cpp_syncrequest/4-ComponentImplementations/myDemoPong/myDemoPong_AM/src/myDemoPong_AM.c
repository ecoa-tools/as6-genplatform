/* Generated by PARSEC */
/* Module Implementation myDemoPong_AM */

#include "ECOA.h"

#include "mylib.h"

#include <assert.h>
#include <stdio.h>
#include "ldp_mod_container_util.h"
#include <stdarg.h>
#include "myDemoPong_AM.h"

static void print_log(myDemoPong_AM__context* context, const char *format, ...){
  va_list vl;
  ECOA__log log;
  va_start(vl, format);
  vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
  va_end( vl);
  myDemoPong_AM_container__log_trace(context, log);
}

/* Entry points for lifecycle operations */
void myDemoPong_AM__INITIALIZE__received(myDemoPong_AM__context* context)
{
    context->user.RR_sync_ok = FALSE;
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

void myDemoPong_AM__Ping__received(myDemoPong_AM__context* context, const mylib__coord* recordwithping, const mylib__t1 nb_ping, const mylib__Test_array* arraywithping, const mylib__Test_fixed_array* fixedarraywithping, const mylib__Test_enum enumwithping)
{
	assert( arraywithping->data[0] == 61);
	assert( arraywithping->data[arraywithping->current_size -1] == 65);
	assert((*fixedarraywithping)[0] == 7);
	assert((*fixedarraywithping)[mylib__Test_fixed_array_MAXSIZE - 1] == 18);
	assert(enumwithping == 1);

	if (nb_ping == 999 && context->user.RR_sync_ok == TRUE) {
		print_log(context,"\033[1;32m SUCCESS\033[0m");
   		ldp_kill_platform((ldp_module_context*)context->platform_hook);
   	}
	else if (nb_ping != 999){
		mylib__coord recordwithpong_val;
		mylib__coord* recordwithpong = &recordwithpong_val;
		recordwithpong->x = recordwithping->x;
		recordwithpong->y = recordwithping->y;
		recordwithpong->x +=1;
		recordwithpong->y +=1;
		mylib__t1 nb_pong = nb_ping;
		nb_pong += 1;
		myDemoPong_AM_container__Pong__send(context, recordwithpong, nb_pong, arraywithping, fixedarraywithping, enumwithping);
	}
}

void myDemoPong_AM__RR_msg_recv_sync__request_received(myDemoPong_AM__context* context, const ECOA__uint32 ID, const mylib__t1 nb_send, const mylib__coord* coord_send)
{
        
	if (nb_send == 13 && coord_send->x == 6 && coord_send->y == 66){
		context->user.RR_sync_ok = TRUE;
	}
	else {
		assert(0);
	}
	mylib__t1 nb_send_back = 666 + nb_send;
	mylib__coord coord_send_back_val = { .x = coord_send->x +1 , .y = coord_send->y +1};
	mylib__coord* coord_send_back = &coord_send_back_val;
	int ret=myDemoPong_AM_container__RR_msg_recv_sync__response_send(context, ID, nb_send_back, coord_send_back);
	assert(ret == ECOA__return_status_OK);
}

