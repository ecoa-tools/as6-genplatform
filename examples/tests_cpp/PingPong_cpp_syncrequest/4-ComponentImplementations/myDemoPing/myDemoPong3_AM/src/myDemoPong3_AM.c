/* Generated by PARSEC */
/* Module Implementation myDemoPong3_AM */

#include "ECOA.h"

#include "mylib.h"

#include <assert.h>
#include <stdio.h>
#include "ldp_mod_container_util.h"
#include <stdarg.h>
#include "myDemoPong3_AM.h"

/* Entry points for lifecycle operations */
void myDemoPong3_AM__INITIALIZE__received(myDemoPong3_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoPong3_AM__START__received(myDemoPong3_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoPong3_AM__STOP__received(myDemoPong3_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoPong3_AM__SHUTDOWN__received(myDemoPong3_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoPong3_AM__Ping__received(myDemoPong3_AM__context* context, const mylib__coord* recordwithping, const mylib__t1 nb_ping, const mylib__Test_array* arraywithping, const mylib__Test_fixed_array* fixedarraywithping, const mylib__Test_enum enumwithping)
{
	assert( arraywithping->data[0] == 61);
	assert( arraywithping->data[arraywithping->current_size -1] == 65);
	assert((*fixedarraywithping)[0] == 7);
	assert((*fixedarraywithping)[mylib__Test_fixed_array_MAXSIZE - 1] == 18);
	assert(enumwithping == 1);

	if (nb_ping != 999){
		mylib__coord recordwithpong_val;
		mylib__coord* recordwithpong = &recordwithpong_val;
		recordwithpong->x = recordwithping->x;
		recordwithpong->y = recordwithping->y;
		recordwithpong->x +=3;
		recordwithpong->y +=3;

		mylib__t1 nb_pong = nb_ping;
		nb_pong += 3;
		myDemoPong3_AM_container__Pong__send(context, recordwithpong, nb_pong, arraywithping, fixedarraywithping, enumwithping);
	}
}

void myDemoPong3_AM__RR_msg2_recv_sync__request_received(myDemoPong3_AM__context* context, const ECOA__uint32 ID, const mylib__t1 nb_send, const mylib__coord* coord_send)
{
	assert(0);
}

