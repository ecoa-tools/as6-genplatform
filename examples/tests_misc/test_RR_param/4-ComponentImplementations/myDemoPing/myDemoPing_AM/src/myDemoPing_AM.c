/* @file "myDemoPing_AM.c"
 * This is the user code for Module myDemoPing_AM
 */

#include <assert.h>
#include <stdio.h>
#include <apr_time.h>
#include "../inc-gen/myDemoPing_AM.h"

/* The following functions must be implemented by this module: */

/* Entrypoints for lifecycle events */
void myDemoPing_AM__INITIALIZE__received(myDemoPing_AM__context* context)
{
   context->user.nb_run=1;
}


void myDemoPing_AM__START__received(myDemoPing_AM__context* context)
{
   /* @TODO TODO - To be implemented */

		context->user.check_nb= 0;
		pingpong__T_2D_Position Ping_Position;
		Ping_Position.Latitude = 134;
		Ping_Position.Longitude = 0.007;
	  	ECOA__uint32 Ping_Target = context->user.check_nb;
		ECOA__uint32 Async_ID;
		apr_sleep(200000);
		myDemoPing_AM_container__Ping_Async__request_async (context,&Async_ID , &Ping_Position, Ping_Target);

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
myDemoPing_AM__Ping_Async__response_received (
  myDemoPing_AM__context* context,
  const ECOA__uint32 ID,
  const ECOA__return_status status
  ,
  const pingpong__T_2D_Position *Pong_Position
  ,
  ECOA__uint32 Pong_Target
)
{
		//printf( " PING RESP async : %i %i,%f\n",Pong_Target, Pong_Position->Latitude, Pong_Position->Longitude);
		assert( Pong_Target== context->user.check_nb+1);

		context->user.check_nb++;
		pingpong__T_2D_Position Ping_Position;
		Ping_Position.Latitude = 134;
		Ping_Position.Longitude = 0.007;
	  	ECOA__uint32 Ping_Target = context->user.check_nb;

	  	pingpong__T_2D_Position Pong_Position2;
		ECOA__uint32 Pong_Target2;
		if(myDemoPing_AM_container__Ping_Sync__request_sync(context, &Ping_Position, Ping_Target, &Pong_Position2, &Pong_Target2 ) == ECOA__return_status_OK){
			//printf( " PING RESP sync : %i %i,%f\n",Pong_Target2, Pong_Position2.Latitude, Pong_Position2.Longitude);
			assert(Pong_Target2==Ping_Target+1);
			assert(Pong_Position2.Latitude==Ping_Position.Latitude);
		}


		if(context->user.nb_run < 20){
			context->user.nb_run++;
			Ping_Target = context->user.check_nb;
			ECOA__uint32 Async_ID;
			myDemoPing_AM_container__Ping_Async__request_async (context,&Async_ID , &Ping_Position, Ping_Target);
		}

}



