/* Generated by PARSEC */
/* Module Implementation myCompReader_mod */

#include "ECOA.h"
#include "myCompReader_mod.h"

#include "ECOA.h"
#include "VD_lib.h"
#include <stdarg.h>
#include <assert.h>

static void print_log(myCompReader_mod__context* context, const char *format, ...){
	va_list vl;
	ECOA__log log;
	va_start(vl, format);
	vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
	va_end( vl);

	myCompReader_mod_container__log_trace(context, log);
}
/* Entry points for lifecycle operations */
void myCompReader_mod__INITIALIZE__received(myCompReader_mod__context* context)
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
  assert( ret == ECOA__return_status_OK);

  VD_lib__vector_data* new_vector=data_type.data;

  print_log(context,"DATA updated %i %i",new_vector->nb_x, new_vector->nb_y);
  if(new_vector->nb_x == new_vector->nb_y){
    print_log(context,"reader finish");
    myCompReader_mod_container__finish__send(context);
    assert(1);
  }
  ret = myCompReader_mod_container__read_vector__release_read_access(context, &data_type);
  assert(ret == ECOA__return_status_OK);
}

