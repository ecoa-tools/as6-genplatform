/* Generated by PARSEC */
/* Module Implementation myDemoPong_AM */

#include "ECOA.h"
#include "myDemoPong_AM.h"

#include "ECOA.h"
#include "libRoot__level1A.h"
#include "libRoot.h"
#include "LDP_myDemoPong_AM.h"
#include "assert.h"
#include "ldp_mod_container_util.h"


#include "ECOA_simple_types_serialization.h"
#include "libRoot_serialization.h"
#include "libRoot__level1A_serialization.h"


#include "LDP__libRoot_types_compare.h"
#include "LDP__libRoot__level1A_types_compare.h"
#include "math.h"


static void print_byte(unsigned char* data, int byte_number){
  for(int i=0; i<byte_number; i++){
    printf("%02x",data[i]);
    if((i+1)%4 == 0){
      printf(" ");
    }
    if((i+1)%32 == 0){
      printf("\n");
    }
  }
  printf("\n");
}

/* Entry points for lifecycle operations */
void myDemoPong_AM__INITIALIZE__received(myDemoPong_AM__context* context)
{
  usleep(1000);
  libRoot__level1A__simple1B simple_16 = 0xffdd;
  libRoot__level1A__simple1A simple_32 = 0xffddccaa;

  libRoot__level1A__simple1B simple_16_s=0;
  libRoot__level1A__simple1A simple_32_s=0;
  libRoot__level1A__simple1B simple_16_d=0;
  libRoot__level1A__simple1A simple_32_d=0;

  ECOA__uint32 added_size=0;
  serialize_libRoot__level1A__simple1B(simple_16, &simple_16_s, 2, &added_size);
  serialize_libRoot__level1A__min_simple1A(simple_32, &simple_32_s, 4, &added_size);

  deserialize_libRoot__level1A__simple1B(&simple_16_d, &simple_16_s, 2);
  deserialize_libRoot__level1A__min_simple1A(&simple_32_d, &simple_32_s, 4);
  assert(simple_32 == simple_32_d);
  assert(simple_16 == simple_16_d);

  //////////////////////////////////////////////////
  // double/float
  libRoot__root_float simple_float_32 = 3.1415;
  unsigned char* simple_float_32_s = malloc(sizeof(libRoot__root_float));
  libRoot__root_float simple_float_32_d = 0.0;

  serialize_libRoot__root_float(simple_float_32, simple_float_32_s, sizeof(libRoot__root_float), &added_size);
  deserialize_libRoot__root_float(&simple_float_32_d, simple_float_32_s,  sizeof(libRoot__root_float));

  assert(fabs(simple_float_32-simple_float_32_d) < 0.0001 );

  libRoot__root_double simple_double_64 = 3.1415;
  unsigned char* simple_double_64_s = malloc(sizeof(libRoot__root_double));
  libRoot__root_double simple_double_64_d = 0.0;

  serialize_libRoot__root_double(simple_double_64, simple_double_64_s, sizeof(libRoot__root_double), &added_size);

  libRoot__root_double* tmp = &simple_double_64;
  print_byte( (void*)tmp, 8);
  print_byte( simple_double_64_s, 8);

  deserialize_libRoot__root_double(&simple_double_64_d, simple_double_64_s,  sizeof(libRoot__root_double));
  assert(fabs(simple_double_64-simple_double_64_d) < 0.0001 );

  //////////////////////////////////////////////////
  libRoot__fixedArray_1A simple_32_f_array;
  for(int i=0;i<libRoot__fixedArray_1A_MAXSIZE;i++){
    simple_32_f_array[i]=0xAABBCC00+i;
  }
  libRoot__fixedArray_1A simple_32_f_array_s;
  libRoot__fixedArray_1A simple_32_f_array_d;


  serialize_libRoot__fixedArray_1A(&simple_32_f_array, &simple_32_f_array_s, 10000, &added_size);
  deserialize_libRoot__fixedArray_1A(&simple_32_f_array_d, &simple_32_f_array_s, 10000);

  // printf("\nfixed array uint32:\n");
  // print_byte((unsigned char*)&simple_32_f_array, libRoot__fixedArray_1A_MAXSIZE*4);
  // print_byte((unsigned char*)&simple_32_f_array_s, libRoot__fixedArray_1A_MAXSIZE*4);
  // print_byte((unsigned char*)&simple_32_f_array_d, libRoot__fixedArray_1A_MAXSIZE*4);


  ////////////////////////////////////////////////
  libRoot__array_1A simple_32_array;
  libRoot__array_1A simple_32_array_d;
  unsigned char* simple32_array_buf = malloc( sizeof(libRoot__array_1A));

  memset(simple32_array_buf, 0x11, sizeof(libRoot__array_1A));
  memset(&simple_32_array_d, 0x12, sizeof(libRoot__array_1A));
  memset(&simple_32_array, 0x13, sizeof(libRoot__array_1A));
  simple_32_array.current_size=0;
  for(int i=0;i<libRoot__array_1A_MAXSIZE;i++){
    if (i < 10){
      simple_32_array.current_size++;
      simple_32_array.data[i]=0xAABBCC00+i;
    }else{
      simple_32_array.data[i]=0;
    }
  }

  serialize_libRoot__array_1A(&simple_32_array, simple32_array_buf, 10000, &added_size);
  deserialize_libRoot__array_1A(&simple_32_array_d, simple32_array_buf, 10000);

  printf("\narray uint32: %i\n", added_size);
  // print_byte((unsigned char*)&simple_32_array.data, libRoot__array_1A_MAXSIZE*4);
  // print_byte((unsigned char*)&simple_32_array.current_size, 4);
  // print_byte((unsigned char*)&simple_32_array_d.data, libRoot__array_1A_MAXSIZE*4);
  // print_byte((unsigned char*)&simple_32_array_d.current_size, 4);

  // assert(is_equals((unsigned char*) &simple_32_array, (unsigned char*) &simple_32_array_d, sizeof(libRoot__array_1A)) == 1);
  assert(LDP_libRoot__array_1A_compare(&simple_32_array, &simple_32_array_d) == true);

  // record array
  libRoot__complex_array_1A record_array;
  libRoot__complex_array_1A record_array_d;
  unsigned char* record_buffer = malloc(sizeof(libRoot__complex_array_1A));

  memset(&record_array_d, 0x11, sizeof(libRoot__complex_array_1A));
  memset(&record_array, 0x12, sizeof(libRoot__complex_array_1A));
  memset(record_buffer, 0x13, sizeof(libRoot__complex_array_1A));

  record_array.current_size = 0;
  for(int i=0;i<libRoot__complex_array_1A_MAXSIZE;i++){
    if (i < 5){
      record_array.current_size++;
      record_array.data[i].champ1=0xAA00+i;
      record_array.data[i].champ2=0xBBBBCCCCDDDDEEEE;
      record_array.data[i].champ3=0xFFFF;
      record_array.data[i].champ4=0xEE;
    }
  }

  serialize_libRoot__complex_array_1A(&record_array, record_buffer, 10000, &added_size);
  deserialize_libRoot__complex_array_1A(&record_array_d, record_buffer, 10000);

  printf("\narray 2D uint32: %i\n", added_size);
  // printf("%i => %i\n", record_array.current_size * sizeof(libRoot__record_1A)+4, added_size);
  // print_byte((unsigned char*)&record_array.data, libRoot__complex_array_1A_MAXSIZE*sizeof(libRoot__record_1A));
  // print_byte((unsigned char*)&record_array.current_size, 4);
  // print_byte((unsigned char*)&record_array_d.data, libRoot__complex_array_1A_MAXSIZE*sizeof(libRoot__record_1A));
  // print_byte((unsigned char*)&record_array_d.current_size, 4);
  assert(LDP_libRoot__complex_array_1A_compare(&record_array, &record_array_d) == true);


  // 2D array
  libRoot__complex_array_2A array2D;
  libRoot__complex_array_2A array2D_d;
  unsigned char* array2A_buffer = malloc(2*sizeof(libRoot__complex_array_2A));

  memset(&array2D, 0x11, sizeof(libRoot__complex_array_2A));
  memset(array2A_buffer, 0x12, 2*sizeof(libRoot__complex_array_2A));
  memset(&array2D_d, 0x13, sizeof(libRoot__complex_array_2A));

  array2D.current_size = 0;
  for(int i=0;i<libRoot__complex_array_2A_MAXSIZE;i++){
    if (i < 3){
      array2D.current_size++;
      array2D.data[i].current_size = 10+i;
      for( int j = 0; j < 10+i; j++){
        array2D.data[i].data[j]= 0xAA0000FF+(i << 8) + (j << 16);
      }
    }
  }
  serialize_libRoot__complex_array_2A(&array2D, array2A_buffer, 10000, &added_size);
  deserialize_libRoot__complex_array_2A(&array2D_d, array2A_buffer, 10000);

  printf("\narray record: %i\n", current_size_of_libRoot__complex_array_2A(&array2D));
  // printf("%li => %i\n", array2D.current_size * sizeof(libRoot__record_1A)+4, added_size);
  // print_byte((unsigned char*)&array2D.data, libRoot__complex_array_1A_MAXSIZE*sizeof(libRoot__record_1A));
  // print_byte((unsigned char*)&array2D.current_size, 4);
  // print_byte((unsigned char*)&array2D_d.data, libRoot__complex_array_1A_MAXSIZE*sizeof(libRoot__record_1A));
  // print_byte((unsigned char*)&array2D_d.current_size, 4);
  assert(LDP_libRoot__complex_array_2A_compare(&array2D, &array2D_d) == true);


  ////////////////////////////////////////////////
  libRoot__complex_array_3A array_3A;
  libRoot__complex_array_3A array_3A_d;
  unsigned char* array_3A_buffer = malloc(sizeof(libRoot__complex_array_3A));

  memset(&array_3A, 0x66, sizeof(libRoot__complex_array_3A));
  memset(array_3A_buffer, 0x12, sizeof(libRoot__complex_array_3A));
  memset(&array_3A_d, 0x88, sizeof(libRoot__complex_array_3A));

  array_3A.current_size = 0;
  for(int i=0;i<libRoot__complex_array_3A_MAXSIZE;i++){
    if (i < 3){
      array_3A.current_size++;
      array_3A.data[i].loco = 0xAAAA;
      if (i%2 == 0){
        array_3A.data[i].select = 1;
        array_3A.data[i].u_select.wagon2= 0xBBBB00000000FFFF+((i+5) << 24);
      }else{
        array_3A.data[i].select = 0;
        array_3A.data[i].u_select.wagon1= 0x7777;
      }
    }
  }

  serialize_libRoot__complex_array_3A(&array_3A, array_3A_buffer, 10000, &added_size);
  deserialize_libRoot__complex_array_3A(&array_3A_d, array_3A_buffer, 10000);

  printf("\narray variante record: %i\n", added_size);
  // printf("%i %i\n", array_3A.current_size, array_3A_d.current_size);
  // print_byte((unsigned char*)&array_3A.data, libRoot__complex_array_3A_MAXSIZE*sizeof(libRoot__var_record));
  // printf("\n");
  // print_byte((unsigned char*)&array_3A_d.data, libRoot__complex_array_3A_MAXSIZE*sizeof(libRoot__var_record));
  assert(LDP_libRoot__complex_array_3A_compare(&array_3A, &array_3A_d) == true);

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

int event_received = 0;
void myDemoPong_AM__event_received__received(myDemoPong_AM__context* context, const libRoot__level1A__simple1B param1, const ECOA__uint32 param2, const libRoot__array_1A* param3)
{
  /* @TODO TODO - To be implemented */
    LDP_myDemoPong_AM__log_trace(context , "event C");
    event_received++;
    if (event_received == 2){
      LDP_myDemoPong_AM__log_info(context ,"SUCCESS");
      ldp_kill_platform((ldp_module_context*)context->platform_hook);
    }

}

void myDemoPong_AM__received_req__request_received(myDemoPong_AM__context* context,
    const ECOA__uint32 ID,
    const libRoot__level1A__simple1B in_param1,
    const ECOA__uint32 in_param2,
    const libRoot__array_1A* in_param3)
{
    assert(LDP_myDemoPong_AM__response_send__received_req(context, ID ,
                                               in_param1,
                                               in_param2,
                                               in_param3, ECOA__TRUE) == ECOA__return_status_OK);

}

