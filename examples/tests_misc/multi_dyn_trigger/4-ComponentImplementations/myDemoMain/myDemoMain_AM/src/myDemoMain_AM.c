/* Generated by PARSEC */
/* Module Implementation myDemoMain_AM */

#include "ECOA.h"
#include "myDemoMain_AM.h"
#include <stdio.h>
#include <unistd.h>

#include <time.h>
#include <assert.h>

#include "pingpong.h"
#include <stdarg.h>
#include "apr_time.h"

static void print_log(myDemoMain_AM__context* context, const char *format, ...){
    va_list vl;
    ECOA__log log;

    va_start(vl, format);
    vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
    va_end( vl);

  myDemoMain_AM_container__log_trace(context, log);
}

/* Entry points for lifecycle operations */
void myDemoMain_AM__INITIALIZE__received(myDemoMain_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoMain_AM__REINITIALIZE__received(myDemoMain_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoMain_AM__START__received(myDemoMain_AM__context* context)
{
	apr_sleep(200000); // wait initialization of dynamic trigger modules

  /* @TODO TODO - To be implemented */
  ECOA__duration delayDuration;
	delayDuration.seconds = 1;
	delayDuration.nanoseconds = 0;
	myDemoMain_AM_container__SetDTrigger__send (context,&delayDuration, 12) ;


	ECOA__duration delayDuration2;
	delayDuration2.seconds = 1;
	delayDuration2.nanoseconds = 500000;
	myDemoMain_AM_container__SetDTrigger__send (context,&delayDuration2, 13) ;
	myDemoMain_AM_container__SetDTrigger2__send (context,&delayDuration2) ;

  // incorrect delay
	// ECOA__duration delayDuration3;
	// delayDuration3.seconds = 6;
	// delayDuration3.nanoseconds = 100000;
	// myDemoMain_AM_container__SetDTrigger__send (context,&delayDuration3, 14);
 //  delayDuration3.seconds = 0;
 //  myDemoMain_AM_container__SetDTrigger__send (context,&delayDuration3, 14);
}

void myDemoMain_AM__STOP__received(myDemoMain_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoMain_AM__SHUTDOWN__received(myDemoMain_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

int param_received = 0;
void myDemoMain_AM__ResultDTrigger__received(myDemoMain_AM__context* context, ECOA__int32 param1)
{
  /* @TODO TODO - To be implemented */
  print_log(context, "==============result Dtrigger %i",param1);
  if (param_received == 0){
    assert(param1 == 12);
    param_received=12;
  }else if (param_received == 12){
    assert(param1 == 13);
  }else{
    assert(0);
  }



  //myDemoMain_AM_container__Finish__send(context);
}
int val=0;
void myDemoMain_AM__ResultDTrigger2__received(myDemoMain_AM__context* context)
{
  print_log(context, "==============result Dtrigger2 %i", val++);

  ECOA__duration delayDuration;
  delayDuration.seconds = 0;
  delayDuration.nanoseconds = 100*1000*1000;

  if( val <= 5){
    myDemoMain_AM_container__SetDTrigger2__send (context,&delayDuration);
  }else{
	 myDemoMain_AM_container__Finish__send(context);
  }
}
