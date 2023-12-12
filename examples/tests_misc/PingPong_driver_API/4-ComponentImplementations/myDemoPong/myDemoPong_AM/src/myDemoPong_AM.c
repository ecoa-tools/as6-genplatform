/* Generated by PARSEC */
/* Module Implementation myDemoPong_AM */

#include "ECOA.h"
#include "myDemoPong_AM.h"

#include "pingpong.h"
#include <stdarg.h>
#include <stdio.h>

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
  /* @TODO TODO - To be implemented */
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

void myDemoPong_AM__Ping__received(myDemoPong_AM__context* context)
{
  print_log(context, "Ping received. Send Pong");
  myDemoPong_AM_container__Pong__send(context);
}

