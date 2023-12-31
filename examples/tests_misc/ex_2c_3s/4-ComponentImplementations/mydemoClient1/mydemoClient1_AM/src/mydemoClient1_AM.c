/* Generated by PARSEC */
/* Module Implementation mydemoClient1_AM */

#include "ECOA.h"
#include "../inc-gen/mydemoClient1_AM.h"

#include <stdio.h>
#include "mylib.h"
#include <stdarg.h>
#include <apr_time.h>

static void print_log(mydemoClient1_AM__context* context, const char *format, ...){
    va_list vl;
    ECOA__log log;

    va_start(vl, format);
    vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
    va_end( vl);

  mydemoClient1_AM_container__log_trace(context, log);
}


/* Entry points for lifecycle operations */
void mydemoClient1_AM__INITIALIZE__received(mydemoClient1_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void mydemoClient1_AM__REINITIALIZE__received(mydemoClient1_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void mydemoClient1_AM__START__received(mydemoClient1_AM__context* context)
{
  /* @TODO TODO - To be implemented */

  apr_sleep(200000);
	mydemoClient1_AM_container__cPing__send(context);
}

void mydemoClient1_AM__STOP__received(mydemoClient1_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void mydemoClient1_AM__SHUTDOWN__received(mydemoClient1_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

