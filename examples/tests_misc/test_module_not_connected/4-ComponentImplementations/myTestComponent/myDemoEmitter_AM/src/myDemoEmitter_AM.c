/* Generated by PARSEC */
/* Module Implementation myDemoEmitter_AM */

#include <assert.h>

#include "ECOA.h"
#include "lib_module.h"

#include <apr_time.h>
#include <stdio.h>
#include <stdarg.h>
#include "myDemoEmitter_AM.h"

static void print_log(myDemoEmitter_AM__context* context, const char *format, ...){
    va_list vl;
    ECOA__log log;

    va_start(vl, format);
    vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
    va_end( vl);

  myDemoEmitter_AM_container__log_trace(context, log);
}

/* Entry points for lifecycle operations */
void myDemoEmitter_AM__INITIALIZE__received(myDemoEmitter_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoEmitter_AM__START__received(myDemoEmitter_AM__context* context)
{
  apr_sleep(200000);

  ECOA__uint32 ID;
  ECOA__return_status ret;
  ECOA__uint32 module_implementation_identifier;
  myDemoEmitter_AM_container__get_module_identifier_value(context, &module_implementation_identifier);

  myDemoEmitter_AM_container__Event_Sent__send(context, module_implementation_identifier);
  print_log(context, "'myDemoEmitter_AM_container__Event_Sent__send' [SENT] with identifier : [%d]", module_implementation_identifier);

  // data written2
  myDemoEmitter_AM_container__write_data2_handle handle2;
  handle2.stamp = -1;
  memset(handle2.platform_hook, 0,ECOA_VERSIONED_DATA_HANDLE_PRIVATE_SIZE);

  apr_sleep(1000 * module_implementation_identifier);
  ret = myDemoEmitter_AM_container__write_data2__get_write_access(context, &handle2);
  print_log(context, "'myDemoEmitter_AM_container__write_data2__publish_write_access' [SENT] with identifier : [%d]", module_implementation_identifier);
  assert(ret == ECOA__return_status_OK || ret == ECOA__return_status_DATA_NOT_INITIALIZED);
  (*handle2.data)[module_implementation_identifier] = (ECOA__byte) module_implementation_identifier+10;
  ret=myDemoEmitter_AM_container__write_data2__publish_write_access(context, &handle2);
  assert(ret == ECOA__return_status_OK);

  // Sync RR
  ret = myDemoEmitter_AM_container__Request_Sync_Sent__request_sync(context, module_implementation_identifier);
  print_log(context, "'myDemoEmitter_AM_container__Request_Sync_Sent__request_sync' [SENT] with identifier : [%d]", module_implementation_identifier);
  if (module_implementation_identifier == 0x01){
    assert(ret == ECOA__return_status_OK);
  }else{
    assert(ret == ECOA__return_status_NO_RESPONSE);
  }

  // Async RR
  ret = myDemoEmitter_AM_container__Request_Async_Sent__request_async(context, &ID, module_implementation_identifier);
  print_log(context, "'myDemoEmitter_AM_container__Request_Async_Sent__request_async' [SENT] with identifier : [%d]", module_implementation_identifier);
  if (module_implementation_identifier == 0x01){
    assert(ret == ECOA__return_status_OK);
  }else{
    assert(ret == ECOA__return_status_NO_RESPONSE);
  }

  // data write
  myDemoEmitter_AM_container__write_data_handle handle;
  ret = myDemoEmitter_AM_container__write_data__get_write_access(context, &handle);
  if (ret != ECOA__return_status_DATA_NOT_INITIALIZED){
    printf("FAILED DW in module %i (%i)\n", module_implementation_identifier, ret);
  }else{
    assert(ret == ECOA__return_status_DATA_NOT_INITIALIZED);
    memcpy(handle.data, &module_implementation_identifier, sizeof(ECOA__uint32));
    print_log(context, "'myDemoEmitter_AM_container__write_data__publish_write_access' [SENT] with identifier : [%d]", module_implementation_identifier);
    ret=myDemoEmitter_AM_container__write_data__publish_write_access(context, &handle);
    assert(ret == ECOA__return_status_OK);
  }

  ret = myDemoEmitter_AM_container__write_data2__get_write_access(context, &handle2);
  printf("[%i] %i %i %i\n", module_implementation_identifier,
                            ((unsigned char*)handle2.data)[0],
                            ((unsigned char*)handle2.data)[1],
                            ((unsigned char*)handle2.data)[2]);
  ret=myDemoEmitter_AM_container__write_data2__cancel_write_access(context, &handle2);

  if (module_implementation_identifier != 0x01){
    myDemoEmitter_AM_container__Finish_Sent__send(context);
  }
}

void myDemoEmitter_AM__STOP__received(myDemoEmitter_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoEmitter_AM__SHUTDOWN__received(myDemoEmitter_AM__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoEmitter_AM__Request_Async_Sent__response_received(myDemoEmitter_AM__context* context, const ECOA__uint32 ID, const ECOA__return_status status)
{
  ECOA__uint32 module_implementation_identifier;
  myDemoEmitter_AM_container__get_module_identifier_value(context, &module_implementation_identifier);
  assert(module_implementation_identifier == 0x01);
  assert(status == ECOA__return_status_OK);
  myDemoEmitter_AM_container__Finish_Sent__send(context);
}