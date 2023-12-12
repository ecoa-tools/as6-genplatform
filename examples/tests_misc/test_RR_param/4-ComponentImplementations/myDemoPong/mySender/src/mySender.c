/* @file "mySender.c"
 * This is the user code for Module mySender
 */

#include <assert.h>
#include <stdio.h>
#include <stdarg.h>
#include <apr_time.h>
#include "mySender.h"

static void print_log(mySender__context* context, const char *format, ...){
    va_list vl;
    ECOA__log log;

    va_start(vl, format);
    vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
    va_end( vl);

  mySender_container__log_trace(context, log);
}

/* The following functions must be implemented by this module: */

/* Entrypoints for lifecycle events */
void mySender__INITIALIZE__received(mySender__context* context)
{
   /* One-shot initialisation activities: */
   /* @TODO TODO - To be implemented */

   /* Call REINITIALIZE entry-point: */
   context->user.nb_run=1;
context->user.check_nb= 100;
}

void mySender__START__received(mySender__context* context)
{
   /* @TODO TODO - To be implemented */
	//sleep(10);

	pingpong__T_2D_Position Ping_Position;
	Ping_Position.Latitude = 12345;
	Ping_Position.Longitude = 0.007;
  	ECOA__uint32 Ping_Target = context->user.check_nb;

	ECOA__uint32 Async_ID;
	apr_sleep(200000);
	mySender_container__Ping_Async__request_async (context, &Async_ID , &Ping_Position, Ping_Target);


}

void mySender__STOP__received(mySender__context* context)
{
   /* @TODO TODO - To be implemented */
}

void mySender__SHUTDOWN__received(mySender__context* context)
{
   /* @TODO TODO - To be implemented */
}



/* Entrypoints for module operations */
void
mySender__Ping_Async__response_received (
  mySender__context* context,
  const ECOA__uint32 ID,
  const ECOA__return_status status
  ,
  const pingpong__T_2D_Position *Pong_Position
  ,
  ECOA__uint32 Pong_Target
)
{
   print_log(context, " SENDER RESP async : %i %i,%f", Pong_Target, Pong_Position->Latitude, Pong_Position->Longitude);
	assert( Pong_Target== context->user.check_nb+1);

	context->user.check_nb++;
	pingpong__T_2D_Position Ping_Position;
	Ping_Position.Latitude = 12345;
	Ping_Position.Longitude = 0.007;
  	ECOA__uint32 Ping_Target = context->user.check_nb;

	pingpong__T_2D_Position Pong_Position2;
	ECOA__uint32 Pong_Target2;
	mySender_container__Ping_Sync__request_sync(context, &Ping_Position, Ping_Target, &Pong_Position2, &Pong_Target2);
	//print_log(context, " SENDER RESP sync : %i %i,%f\n\n", Pong_Target2, Pong_Position2.Latitude, Pong_Position2.Longitude);
	assert(Pong_Target2==context->user.check_nb+1);
	assert(Pong_Position2.Latitude==Ping_Position.Latitude);

  	Ping_Target = context->user.check_nb;
	if(context->user.nb_run < 20){
		context->user.nb_run++;
		ECOA__uint32 Async_ID;
		mySender_container__Ping_Async__request_async (context,&Async_ID , &Ping_Position, Ping_Target);
	}

}



