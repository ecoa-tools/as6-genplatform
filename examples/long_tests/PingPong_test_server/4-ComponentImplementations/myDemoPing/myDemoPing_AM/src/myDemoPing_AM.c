/* Generated by PARSEC */
/* Module Implementation myDemoPing_AM */

#include "ECOA.h"
#include "myDemoPing_AM.h"

#include "pingpong.h"
#include <signal.h>

/* Entry points for lifecycle operations */
void myDemoPing_AM__INITIALIZE__received(myDemoPing_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoPing_AM__START__received(myDemoPing_AM__context* context)
{
  context->user.nb_pong=0;

  ECOA__duration delayDuration;
  delayDuration.seconds = 0;
  delayDuration.nanoseconds = 1;
  myDemoPing_AM_container__SetDTrigger__send(context, &delayDuration);

  delayDuration.seconds = 1;
  delayDuration.nanoseconds = 500000;
  myDemoPing_AM_container__SetDTrigger__send(context, &delayDuration);

  delayDuration.seconds = 0;
  delayDuration.nanoseconds = 500000;
  myDemoPing_AM_container__SetDTrigger__send(context, &delayDuration);
}

void myDemoPing_AM__STOP__received(myDemoPing_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoPing_AM__SHUTDOWN__received(myDemoPing_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoPing_AM__trigger__received(myDemoPing_AM__context* context)
{
  myDemoPing_AM_container__Ping__send(context,1,context->user.nb_pong);
}

void myDemoPing_AM__ResultDTrigger__received(myDemoPing_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoPing_AM__Pong__received(myDemoPing_AM__context* context)
{
  context->user.nb_pong++;

	if (context->user.nb_pong>=2){

    myDemoPing_AM_container__read_vector_handle handle;
    ECOA__return_status ret;
    ret = myDemoPing_AM_container__read_vector__get_read_access(context, &handle);
    pingpong__vector_data new_vector={0,0};

    if( ret == ECOA__return_status_NO_DATA){
    } else{
      memcpy(&new_vector,handle.data,sizeof(pingpong__vector_data) );
      ret = myDemoPing_AM_container__read_vector__release_read_access(context, &handle);
    }

		kill(getpid(), SIGTERM);
	}
}
