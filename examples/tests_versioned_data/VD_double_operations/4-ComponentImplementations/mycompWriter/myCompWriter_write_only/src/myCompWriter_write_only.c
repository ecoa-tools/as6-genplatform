/*******************************************************/
/* Generated by : PARSEC 5.0                           */
/*                Copyright Dassault Aviation          */
/*                date: 2019-03-04 11:44:35.287522     */
/*******************************************************/


/* Module Implementation myCompWriter_write_only */

#include <string.h>
#include <stdlib.h>
#include <assert.h>
#include <stdio.h>
#include "ECOA.h"
#include "myCompWriter_write_only.h"
#include "VD_lib.h"

/* Entry points for lifecycle operations */
void myCompWriter_write_only__INITIALIZE__received(myCompWriter_write_only__context* context)
{
  /* @TODO TODO - To be implemented */

  context->user.vector.nb_x = -33;
  context->user.vector.nb_y = 33;
  myCompWriter_write_only_container__get_writer_id_value(context,
                                                         &context->user.vector.writer_id);
}

void myCompWriter_write_only__START__received(myCompWriter_write_only__context* context)
{
  myCompWriter_write_only_container__write_vector_handle handle;

  while(1){
    context->user.vector.nb_x++;
    context->user.vector.nb_y--;
  	ECOA__return_status ret = myCompWriter_write_only_container__write_vector__get_write_access(context, &handle);
  	if(ret == ECOA__return_status_DATA_NOT_INITIALIZED){
  		// first write
      // pass
  	}else{
  		assert(ret == ECOA__return_status_OK);
  	}

    // write data
  	memcpy(handle.data, &context->user.vector, sizeof(VD_lib__vector_data));

    ret=myCompWriter_write_only_container__write_vector__publish_write_access(context, &handle);
    assert(ret == ECOA__return_status_OK);

    if(context->user.vector.nb_x == context->user.vector.nb_y){
      break;
    }
    usleep(10000);
    printf("whaaaaaaa\n");
  }
  printf("writer (write-only) finish\n");
  myCompWriter_write_only_container__finish__send(context);
}

void myCompWriter_write_only__STOP__received(myCompWriter_write_only__context* context)
{

}

void myCompWriter_write_only__SHUTDOWN__received(myCompWriter_write_only__context* context)
{
  /* @TODO TODO - To be implemented */
}
