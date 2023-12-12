/* Generated by PARSEC */
/* Module Implementation myDemoServer2_AM */

#include "ECOA.h"
#include "myDemoServer2_AM.h"

#include "pingpong.h"

#include <stdio.h>
#include <string.h>
#include <stdarg.h>


int myDemoServer2_AM_log_trace(myDemoServer2_AM__context* context, const char *msg, ...) {
  ECOA__log log;
  va_list argp;
  va_start(argp, msg);
  vsnprintf((char *)&log.data, ECOA__LOG_MAXSIZE, msg, argp);
  va_end(argp);
  log.current_size = strnlen((char *)&log.data, ECOA__LOG_MAXSIZE);
  myDemoServer2_AM_container__log_trace(context, log);
  return log.current_size;
}



/* Entry points for lifecycle operations */
void myDemoServer2_AM__INITIALIZE__received(myDemoServer2_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoServer2_AM__REINITIALIZE__received(myDemoServer2_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoServer2_AM__START__received(myDemoServer2_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoServer2_AM__STOP__received(myDemoServer2_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoServer2_AM__SHUTDOWN__received(myDemoServer2_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoServer2_AM__req_Sync__request_received(myDemoServer2_AM__context* context, const ECOA__uint32 ID)
{
  /* @TODO TODO - To be implemented */
	myDemoServer2_AM_log_trace(context, "received req Sync extern ID=%i",ID);
  sleep(1);
	myDemoServer2_AM_container__req_Sync__response_send(context, ID);
  myDemoServer2_AM_container__finish__send(context);

}

void myDemoServer2_AM__req_Async__request_received(myDemoServer2_AM__context* context, const ECOA__uint32 ID)
{
  /* @TODO TODO - To be implemented */
	myDemoServer2_AM_log_trace(context, "received req Async extern ID=%i",ID);
  usleep(5*1000*100);
	myDemoServer2_AM_container__req_Async__response_send(context, ID);
  myDemoServer2_AM_container__finish__send(context);
}

