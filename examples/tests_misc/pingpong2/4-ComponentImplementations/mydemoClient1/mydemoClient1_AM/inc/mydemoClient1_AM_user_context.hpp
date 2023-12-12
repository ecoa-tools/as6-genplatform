/* Done by Florian using Jinja */

#if !defined(_MYDEMOCLIENT1_AM_USER_CONTEXT_HPP)
#define _MYDEMOCLIENT1_AM_USER_CONTEXT_HPP

/*Standaard types*/
#include <ECOA.hpp>

/*Additionnaly created types*/
#include "mylib.hpp"

/*Container types*/
/* #include "mydemoClient1_AM_container_types.h" */

namespace mydemoClient1_AM
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

} /* mydemoClient1_AM */

#endif /* MYDEMOCLIENT1_AM_USER_CONTEXT_HPP */