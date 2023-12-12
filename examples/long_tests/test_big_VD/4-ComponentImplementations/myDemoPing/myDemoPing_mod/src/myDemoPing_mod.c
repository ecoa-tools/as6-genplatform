/* Generated by PARSEC */
/* Module Implementation myDemoPing_mod */

#include "ECOA.h"
#include "myDemoPing_mod.h"

#include "lib_array.h"
#include "apr_time.h"
#include <assert.h>

#include <stdio.h>
#include <stdarg.h>
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
  /* @TODO TODO - To be implemented */
}

void myDemoPing_mod__REINITIALIZE__received(myDemoPing_mod__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoPing_mod__START__received(myDemoPing_mod__context* context)
{
  apr_sleep(200000);
  context->user.nb_pong_received = 0;

  myDemoPing_mod_container__Ping_array_1k_handle data_handle_1k;
  int ret = myDemoPing_mod_container__Ping_array_1k__get_write_access(context, &data_handle_1k);
  assert(ret == ECOA__return_status_DATA_NOT_INITIALIZED);
  fill_array(context, (ECOA__uint32*) data_handle_1k.data, lib_array__array_1k_MAXSIZE);
  ret = myDemoPing_mod_container__Ping_array_1k__publish_write_access(context, &data_handle_1k);
  assert(ret == ECOA__return_status_OK);

  myDemoPing_mod_container__Ping_array_4k_handle data_handle_4k;
  ret = myDemoPing_mod_container__Ping_array_4k__get_write_access(context, &data_handle_4k);
  assert(ret == ECOA__return_status_DATA_NOT_INITIALIZED);
  fill_array(context, (ECOA__uint32*) data_handle_4k.data, lib_array__array_4k_MAXSIZE);
  ret = myDemoPing_mod_container__Ping_array_4k__publish_write_access(context, &data_handle_4k) ;
  assert(ret== ECOA__return_status_OK);


  myDemoPing_mod_container__Ping_array_64k_handle data_handle_64k;
  ret = myDemoPing_mod_container__Ping_array_64k__get_write_access(context, &data_handle_64k);
  assert(ret == ECOA__return_status_DATA_NOT_INITIALIZED);
  fill_array(context, (ECOA__uint32*) data_handle_64k.data, lib_array__array_64k_MAXSIZE);
  ret = myDemoPing_mod_container__Ping_array_64k__publish_write_access(context, &data_handle_64k);
  assert(ret == ECOA__return_status_OK);


  myDemoPing_mod_container__Ping_array_16k_handle data_handle_16k;
  ret = myDemoPing_mod_container__Ping_array_16k__get_write_access(context, &data_handle_16k);
  assert(ret == ECOA__return_status_DATA_NOT_INITIALIZED);
  fill_array(context, (ECOA__uint32*) data_handle_16k.data, lib_array__array_16k_MAXSIZE);
  ret = myDemoPing_mod_container__Ping_array_16k__publish_write_access(context, &data_handle_16k);
  assert(ret == ECOA__return_status_OK);


  myDemoPing_mod_container__Ping_array_256k_handle data_handle_256k;
  ret = myDemoPing_mod_container__Ping_array_256k__get_write_access(context, &data_handle_256k);
  assert(ret == ECOA__return_status_DATA_NOT_INITIALIZED);
  fill_array(context, (ECOA__uint32*) data_handle_256k.data, lib_array__array_256k_MAXSIZE);
  ret = myDemoPing_mod_container__Ping_array_256k__publish_write_access(context, &data_handle_256k);
  assert(ret == ECOA__return_status_OK);

  myDemoPing_mod_container__Ping_array_10m_handle data_handle_10m;
  ret = myDemoPing_mod_container__Ping_array_10m__get_write_access(context, &data_handle_10m);
  assert(ret == ECOA__return_status_DATA_NOT_INITIALIZED);
  fill_array(context, (ECOA__uint32*) data_handle_10m.data, lib_array__array_10m_MAXSIZE);
  ret = myDemoPing_mod_container__Ping_array_10m__publish_write_access(context, &data_handle_10m);
  assert(ret == ECOA__return_status_OK);

}

void myDemoPing_mod__STOP__received(myDemoPing_mod__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoPing_mod__SHUTDOWN__received(myDemoPing_mod__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoPing_mod__Pong__received(myDemoPing_mod__context* context)
{
  context->user.nb_pong_received++;
  print_log(context, "pong received %i", context->user.nb_pong_received);

  if (context->user.nb_pong_received == 10000){
    print_log(context, "\033[1;32m SUCCESS  \033[0m");
    fflush(stdout);
    ldp_kill_platform((ldp_module_context*)context->platform_hook);
    apr_sleep(1000000);
  }

  myDemoPing_mod_container__Ping_array_1k_handle data_handle_1k;
  myDemoPing_mod_container__Ping_array_4k_handle data_handle_4k;
  myDemoPing_mod_container__Ping_array_64k_handle data_handle_64k;
  myDemoPing_mod_container__Ping_array_16k_handle data_handle_16k;
  myDemoPing_mod_container__Ping_array_256k_handle data_handle_256k;
  int ret;
  switch (context->user.nb_pong_received % 5){
    case 0 :
      ret = myDemoPing_mod_container__Ping_array_1k__get_write_access(context, &data_handle_1k);
      assert(ret == ECOA__return_status_OK);
      fill_array(context, (ECOA__uint32*) data_handle_1k.data, lib_array__array_1k_MAXSIZE);
      ret = myDemoPing_mod_container__Ping_array_1k__publish_write_access(context, &data_handle_1k);
      assert(ret == ECOA__return_status_OK);
      break;

    case 1 :
      ret = myDemoPing_mod_container__Ping_array_4k__get_write_access(context, &data_handle_4k);
      assert(ret == ECOA__return_status_OK);
      fill_array(context, (ECOA__uint32*) data_handle_4k.data, lib_array__array_4k_MAXSIZE);
      ret = myDemoPing_mod_container__Ping_array_4k__publish_write_access(context, &data_handle_4k);
      assert(ret == ECOA__return_status_OK);
      break;

    case 2 :
      ret = myDemoPing_mod_container__Ping_array_64k__get_write_access(context, &data_handle_64k);
      assert(ret== ECOA__return_status_OK);
      fill_array(context, (ECOA__uint32*) data_handle_64k.data, lib_array__array_64k_MAXSIZE);
      ret = myDemoPing_mod_container__Ping_array_64k__publish_write_access(context, &data_handle_64k);
      assert(ret == ECOA__return_status_OK);
      break;

    case 3 :
      ret = myDemoPing_mod_container__Ping_array_16k__get_write_access(context, &data_handle_16k);
      assert(ret == ECOA__return_status_OK);
      fill_array(context, (ECOA__uint32*) data_handle_16k.data, lib_array__array_16k_MAXSIZE);
      ret = myDemoPing_mod_container__Ping_array_16k__publish_write_access(context, &data_handle_16k);
      assert(ret == ECOA__return_status_OK);
      break;

    case 4 :
      ret = myDemoPing_mod_container__Ping_array_256k__get_write_access(context, &data_handle_256k);
      assert(ret == ECOA__return_status_OK);
      fill_array(context, (ECOA__uint32*) data_handle_256k.data, lib_array__array_256k_MAXSIZE);
      ret = myDemoPing_mod_container__Ping_array_256k__publish_write_access(context, &data_handle_256k);
      assert(ret == ECOA__return_status_OK);
      break;
    default:
      print_log(context, "????");
  }

}