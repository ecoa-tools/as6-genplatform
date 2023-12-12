/* Generated by PARSEC */
/* Module Implementation for myDemoPong_AM_cpp
Done by Florian using Jinja */

#include <assert.h>
#include "ECOA.hpp"


#include "lib.hpp"
#include "ldp_mod_container_util.h"
#include "pingpong.hpp"
#include "pingpong2.hpp"
#include "myDemoPong_AM_cpp.hpp"



namespace myDemoPong_AM_cpp
{

/* Entry points for lifecycle operations */
void Module::INITIALIZE__received(){
/* @TODO TODO - To be implemented */
}

void Module::START__received(){  // check constant property
  ECOA::uint16 cst_value;
  container->get_p_constant_value(cst_value);
  assert(cst_value == lib::magic_number);

  // check enum property
  lib::Test_enum enum_val;
  container->get_p_enum_value(enum_val);
  assert(enum_val.value == lib::Test_enum::SATURDAY);

  // check fixed array property
  lib::Test_fixed_array fixed_array_val;
  container->get_p_fixed_array_value(fixed_array_val );
  for (unsigned int i=0; i<10; i++){
    if (i != 9){
      assert(fixed_array_val[i] == i);
    }else{
      assert(fixed_array_val[i] == lib::magic_number);
    }
  }

  // check array property
  lib::Test_array array_val;
  container->get_p_array_value(array_val);
  assert(array_val.current_size == 3);
  for(unsigned int i=0; i<array_val.current_size;i++){
    assert(array_val.data[i]=i+1);
  }

  // check fixed complex array
  lib::Test_fixed_array f_array_compl_val;
  container->get_p_fixed_array_complex_value(f_array_compl_val );
  lib::Test_fixed_array f_array_compl_val2 = {0,1,2,777,777,777,777,777,9,lib::magic_number};
  for(int i=0; i<10;i++)
    assert(f_array_compl_val[i] == f_array_compl_val2[i]);

  // check matrix
  lib::Test_matrix_fixed_array maxtrix_val;
  container->get_p_fixed_array_matrix_value(maxtrix_val);
  lib::Test_fixed_array tmp2 = {1,4,4,4,4,3,3,3,0,0};
  for(int i=0; i<10;i++)
    assert(maxtrix_val[0][i] == tmp2[i]);

  for (unsigned int i=1; i<lib::Test_matrix_fixed_array_MAXSIZE; i++){
    assert(maxtrix_val[i][0] == 5);
    for (unsigned int j=1; j<lib::Test_fixed_array_MAXSIZE; j++){
      assert(maxtrix_val[i][j]=1);
    }
  }

  // check enum array
  lib::Test_enum_array enume_array_val;
  container->get_p_enum_array_value( enume_array_val);
  lib::Test_enum_array enume_array_tmp = {lib::Test_enum(lib::Test_enum::SUNDAY), lib::Test_enum(lib::Test_enum::SATURDAY), lib::Test_enum(lib::Test_enum::SATURDAY), lib::Test_enum(lib::Test_enum::SUNDAY), lib::Test_enum(lib::Test_enum::SUNDAY)};
  for (unsigned int i=1; i<lib::Test_matrix_fixed_array_MAXSIZE; i++){
    assert(enume_array_val[i].value == enume_array_tmp[i].value);
  }

  // check string
  lib::Test_array_char char_array_val;
  container->get_p_array_string_value( char_array_val);
  assert(char_array_val.current_size == 8);
  assert(strncmp (char_array_val.data, "\"LDP\"A", char_array_val.current_size) == 0);

  lib::Test_fixed_array_char char_f_array_val;
  container->get_p_fixed_array_string_value( char_f_array_val);
  assert(strncmp (char_f_array_val, "A\"LDP\"AA", lib::Test_fixed_array_char_MAXSIZE) == 0);

  // check ascii
  lib::Test_array_char array_ascii_val;
  container->get_p_array_ascii_value( array_ascii_val);
  assert(array_ascii_val.current_size == 3);
  assert(strncmp (array_ascii_val.data, "ABC", 3) == 0);

  lib::Test_fixed_array_char f_array_ascii_val;
  container->get_p_fixed_array_ascii_value( f_array_ascii_val);
  for ( int i=0; i< 10 ; i++){
    assert(f_array_ascii_val[i]== 0x41+i);
  }

  // check char8 matrix
  lib::Test_fixed_matrix_char fixed_matrix_ascii_val;
  container->get_p_fixed_matrix_ascii_value( fixed_matrix_ascii_val);
  assert(strncmp (fixed_matrix_ascii_val[0], "AAAAAAAAAA", lib::Test_matrix_fixed_array_MAXSIZE) == 0);
  for(unsigned int i=1; i<lib::Test_fixed_matrix_char_MAXSIZE;i++){
    assert(strncmp (fixed_matrix_ascii_val[i], "ABCDEFGHIJ",lib::Test_matrix_fixed_array_MAXSIZE) == 0);
  }


  lib::Test_matrix_char matrix_ascii_val;
  container->get_p_matrix_ascii_value( matrix_ascii_val);
  assert(matrix_ascii_val.current_size == 4);
  assert(matrix_ascii_val.data[0].current_size == 2);
  assert(strncmp (matrix_ascii_val.data[0].data, "AB", 2) == 0);
  assert(matrix_ascii_val.data[1].current_size == 2);
  assert(strncmp (matrix_ascii_val.data[1].data, "AB", 2) == 0);

  assert(matrix_ascii_val.data[2].current_size == 4);
  assert(strncmp (matrix_ascii_val.data[2].data, "AAAA", 4) == 0);
  assert(matrix_ascii_val.data[3].current_size == 4);
  assert(strncmp (matrix_ascii_val.data[3].data, "AAAA", 4) == 0);

}
void Module::STOP__received(){
/* @TODO TODO - To be implemented */
}
void Module::SHUTDOWN__received(){
/* @TODO TODO - To be implemented */
}

void Module::Ping__received()
{
/* @TODO TODO - To be implemented */
}



/* Fault Handling API , linked to another namespace (fault_handler_impl_name) */

extern "C" {

	Module* myDemoPong_AM_cpp__new_instance()
	{
		return new Module();
	}
}

} /* namespace myDemoPong_AM_cpp */
