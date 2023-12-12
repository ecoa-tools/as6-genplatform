/* Generated by PARSEC */
/* Module Implementation myCompReader_mod */

#include "ECOA.h"
#include "myCompReader_mod.h"

#include "VD_lib.h"
#include <stdio.h>
#include <assert.h>

/* Entry points for lifecycle operations */
#include <stdarg.h>
static void print_log(myCompReader_mod__context* context, const char *format, ...){
va_list vl;
ECOA__log log;
va_start(vl, format);
vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
va_end( vl);

myCompReader_mod_container__log_trace(context, log);
}

void myCompReader_mod__INITIALIZE__received(myCompReader_mod__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myCompReader_mod__REINITIALIZE__received(myCompReader_mod__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myCompReader_mod__START__received(myCompReader_mod__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myCompReader_mod__STOP__received(myCompReader_mod__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myCompReader_mod__SHUTDOWN__received(myCompReader_mod__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myCompReader_mod__read_vector__updated(myCompReader_mod__context* context){
  myCompReader_mod_container__read_vector_handle data_type;
  ECOA__return_status ret = myCompReader_mod_container__read_vector__get_read_access(context, &data_type);
  assert(ret == ECOA__return_status_OK);

  VD_lib__vector_data* new_vector=data_type.data;
  ECOA__uint32 reader_id;
  myCompReader_mod_container__get_reader_id_value(context, &reader_id);

  print_log(context,"[%x] DATA updated version %i %i %i\n",reader_id, new_vector->writer_id, new_vector->nb_x, new_vector->nb_y);
  assert(new_vector->writer_id == reader_id);

  if(new_vector->nb_x == new_vector->nb_y){
    print_log(context,"[%x] reader version finish", reader_id);
    myCompReader_mod_container__finish__send(context);
    assert(1);
  }
  ret = myCompReader_mod_container__read_vector__release_read_access(context, &data_type);
  assert(ret == ECOA__return_status_OK);
}
