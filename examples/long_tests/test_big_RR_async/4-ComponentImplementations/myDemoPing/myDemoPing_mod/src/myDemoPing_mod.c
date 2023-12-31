/* Generated by PARSEC */
/* Module Implementation myDemoPing_mod */

#include "ECOA.h"
#include "myDemoPing_mod.h"

#include "lib_array.h"
#include "apr_time.h"
#include <stdio.h>
#include <stdarg.h>
#include <assert.h>
#include "ldp_mod_container_util.h"

static void print_log(myDemoPing_mod__context* context, const char *format, ...){
    va_list vl;
    ECOA__log log;

    va_start(vl, format);
    vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
    va_end( vl);

  myDemoPing_mod_container__log_trace(context, log);
}

static void fill_array(myDemoPing_mod__context* context, ECOA__uint32* array, int size){
  for ( int i=0; i<size; i++){
    array[i] = context->user.nb_pong_received + i;
  }
  array[0] = 0XEC0A + context->user.nb_pong_received;
  array[size -1] = 0XEC0A;
}


/* Entry points for lifecycle operations */
void myDemoPing_mod__INITIALIZE__received(myDemoPing_mod__context* context)
{
  context->user.nb_pong_received = 0;
}

void myDemoPing_mod__REINITIALIZE__received(myDemoPing_mod__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoPing_mod__START__received(myDemoPing_mod__context* context)
{
  apr_sleep(200000);

  lib_array__array_1k* array_1k = malloc(sizeof(lib_array__array_1k));
  lib_array__array_4k* array_4k = malloc(sizeof(lib_array__array_4k));
  lib_array__array_16k* array_16k = malloc(sizeof(lib_array__array_16k));
  lib_array__array_64k* array_64k = malloc(sizeof(lib_array__array_64k));
  lib_array__array_256k* array_256k = malloc(sizeof(lib_array__array_256k));
  lib_array__array_10m* array_10m = malloc(sizeof(lib_array__array_10m));

  fill_array(context, *array_1k,lib_array__array_1k_MAXSIZE );
  int ret = myDemoPing_mod_container__Ping_array_1k__request_async(context, &context->user.ID_RR_1k, array_1k);
  assert(ret == ECOA__return_status_OK);
  fill_array(context, *array_4k,lib_array__array_4k_MAXSIZE );
  ret = myDemoPing_mod_container__Ping_array_4k__request_async(context, &context->user.ID_RR_4k, array_4k);
  assert(ret == ECOA__return_status_OK);
  fill_array(context, *array_16k,lib_array__array_16k_MAXSIZE );
  ret = myDemoPing_mod_container__Ping_array_16k__request_async(context, &context->user.ID_RR_16k, array_16k);
  assert(ret == ECOA__return_status_OK);
  fill_array(context, *array_64k,lib_array__array_64k_MAXSIZE );
  ret = myDemoPing_mod_container__Ping_array_64k__request_async(context, &context->user.ID_RR_64k, array_64k);
  assert(ret == ECOA__return_status_OK);
  fill_array(context, *array_256k,lib_array__array_256k_MAXSIZE );
  ret = myDemoPing_mod_container__Ping_array_256k__request_async(context, &context->user.ID_RR_256k, array_256k);
  assert(ret == ECOA__return_status_OK);
  fill_array(context, *array_10m,lib_array__array_10m_MAXSIZE );
  ret = myDemoPing_mod_container__Ping_array_10m__request_async(context, &context->user.ID_RR_10m, array_10m);
  assert(ret == ECOA__return_status_OK);

  free(array_1k);
  free(array_4k);
  free( array_16k);
  free( array_64k);
  free(array_256k);
  free(array_10m );
}

void myDemoPing_mod__STOP__received(myDemoPing_mod__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoPing_mod__SHUTDOWN__received(myDemoPing_mod__context* context)
{
  /* @TODO TODO - To be implemented */
}

static int max_run = 10000;
void myDemoPing_mod__Ping_array_4k__response_received(myDemoPing_mod__context* context, const ECOA__uint32 ID, const ECOA__return_status status)
{
  context->user.nb_pong_received++;
  print_log(context, "pong received 4k %i", context->user.nb_pong_received);

  assert(ID == context->user.ID_RR_4k);
  assert(status == ECOA__return_status_OK);

  lib_array__array_4k* array_4k = malloc(sizeof(lib_array__array_4k));
  fill_array(context, *array_4k,lib_array__array_4k_MAXSIZE );

  if( context->user.ID_RR_4k < max_run){
    int ret = myDemoPing_mod_container__Ping_array_4k__request_async(context, &context->user.ID_RR_4k, array_4k);
    assert(ret == ECOA__return_status_OK);
  }
  free(array_4k);
}

void myDemoPing_mod__Ping_array_16k__response_received(myDemoPing_mod__context* context, const ECOA__uint32 ID, const ECOA__return_status status)
{
  context->user.nb_pong_received++;
  print_log(context, "pong received 16k %i", context->user.nb_pong_received);

  assert(ID == context->user.ID_RR_16k);
  assert(status == ECOA__return_status_OK);

  lib_array__array_16k* array_16k = malloc(sizeof(lib_array__array_16k));
  fill_array(context, *array_16k,lib_array__array_16k_MAXSIZE );

  if( context->user.ID_RR_16k < max_run){
    int ret = myDemoPing_mod_container__Ping_array_16k__request_async(context, &context->user.ID_RR_16k, array_16k);
    assert(ret == ECOA__return_status_OK);
  }
  free(array_16k);
}

void myDemoPing_mod__Pong__received(myDemoPing_mod__context* context)
{
  context->user.nb_pong_received++;
  print_log(context, "pong received %i", context->user.nb_pong_received);
}

void myDemoPing_mod__Ping_array_64k__response_received(myDemoPing_mod__context* context, const ECOA__uint32 ID, const ECOA__return_status status)
{
  context->user.nb_pong_received++;
  print_log(context, "pong received 64k %i", context->user.nb_pong_received);

  assert(ID == context->user.ID_RR_64k);
  assert(status == ECOA__return_status_OK);

  lib_array__array_64k* array_64k = malloc(sizeof(lib_array__array_64k));
  fill_array(context, *array_64k,lib_array__array_64k_MAXSIZE );

  if( context->user.ID_RR_64k < max_run){
    int ret = myDemoPing_mod_container__Ping_array_64k__request_async(context, &context->user.ID_RR_64k, array_64k);
    assert(ret == ECOA__return_status_OK);
  }
  free(array_64k);
}

void myDemoPing_mod__Ping_array_256k__response_received(myDemoPing_mod__context* context, const ECOA__uint32 ID, const ECOA__return_status status)
{
  context->user.nb_pong_received++;
  print_log(context, "pong received 256k %i", context->user.nb_pong_received);

  assert(ID == context->user.ID_RR_256k);
  assert(status == ECOA__return_status_OK);

  lib_array__array_256k* array_256k = malloc(sizeof(lib_array__array_256k));
  fill_array(context, *array_256k,lib_array__array_256k_MAXSIZE );

  if( context->user.ID_RR_256k < max_run){
    int ret = myDemoPing_mod_container__Ping_array_256k__request_async(context, &context->user.ID_RR_256k, array_256k);
    assert(ret == ECOA__return_status_OK);
  }
  free(array_256k);
}

void myDemoPing_mod__Ping_array_1k__response_received(myDemoPing_mod__context* context, const ECOA__uint32 ID, const ECOA__return_status status)
{
  context->user.nb_pong_received++;
  print_log(context, "pong received 1k %i", context->user.nb_pong_received);

  assert(ID == context->user.ID_RR_1k);
  assert(status == ECOA__return_status_OK);

  lib_array__array_1k* array_1k = malloc(sizeof(lib_array__array_1k));
  fill_array(context, *array_1k,lib_array__array_1k_MAXSIZE );

  if( context->user.ID_RR_1k < max_run){
    int ret = myDemoPing_mod_container__Ping_array_1k__request_async(context, &context->user.ID_RR_1k, array_1k);
    assert(ret == ECOA__return_status_OK);
  }
  free(array_1k);
}

void myDemoPing_mod__Ping_array_10m__response_received(myDemoPing_mod__context* context, const ECOA__uint32 ID, const ECOA__return_status status)
{
  context->user.nb_pong_received++;
  print_log(context, "pong received 10m %i", context->user.nb_pong_received);

  assert(ID == context->user.ID_RR_10m);
  assert(status == ECOA__return_status_OK);

  lib_array__array_10m* array_10m = malloc(sizeof(lib_array__array_10m));
  fill_array(context, *array_10m,lib_array__array_10m_MAXSIZE );

  if( context->user.ID_RR_10m < max_run){
    int ret = myDemoPing_mod_container__Ping_array_10m__request_async(context, &context->user.ID_RR_10m, array_10m);
    assert(ret == ECOA__return_status_OK);
  }else{
    print_log(context, "\033[1;32m SUCCESS  \033[0m");
    fflush(stdout);
    ldp_kill_platform((ldp_module_context*)context->platform_hook);
  }
  free(array_10m);
}