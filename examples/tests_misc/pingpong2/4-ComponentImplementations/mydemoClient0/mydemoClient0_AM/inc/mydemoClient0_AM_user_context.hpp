/* Done by Florian using Jinja */

#if !defined(_MYDEMOCLIENT0_AM_USER_CONTEXT_HPP)
#define _MYDEMOCLIENT0_AM_USER_CONTEXT_HPP

/*Standaard types*/
#include <ECOA.hpp>

/*Additionnaly created types*/
#include "mylib.hpp"

/*Container types*/
/* #include "mydemoClient0_AM_container_types.h" */

namespace mydemoClient0_AM
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

} /* mydemoClient0_AM */

#endif /* MYDEMOCLIENT0_AM_USER_CONTEXT_HPP */