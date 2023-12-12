/* Done by Florian using Jinja */

#if !defined(_MYCOMPWRITER_MOD_USER_CONTEXT_HPP)
#define _MYCOMPWRITER_MOD_USER_CONTEXT_HPP

/*Standaard types*/
#include <ECOA.hpp>

/*Additionnaly created types*/
#include "VD_lib.hpp"

/*Container types*/
#include "myCompWriter_mod_container_types.hpp"

namespace myCompWriter_mod
{

// User Module Context structure example
typedef struct
{
 //declare the User Module Context "local" date here
 unsigned int myCounter;
 
} user_context;

//Warm start Module Context structure example
typedef struct
{
	/* declare the Warm Start Module Context data here */
	ECOA::boolean8 warm_start_valid;
	unsigned long myData;
} warm_start_context;

} /* myCompWriter_mod */

#endif /* MYCOMPWRITER_MOD_USER_CONTEXT_HPP */