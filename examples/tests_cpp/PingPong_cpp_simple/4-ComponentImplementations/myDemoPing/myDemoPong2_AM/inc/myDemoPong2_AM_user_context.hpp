/* Done by Florian using Jinja */

#if !defined(_MYDEMOPONG2_AM_USER_CONTEXT_HPP)
#define _MYDEMOPONG2_AM_USER_CONTEXT_HPP

/*Standaard types*/
#include <ECOA.hpp>

/*Additionnaly created types*/
#include "mylib.hpp"

/*Container types*/
#include "myDemoPong2_AM_container_types.hpp"

namespace myDemoPong2_AM
{

// User Module Context structure example
typedef struct
{
} user_context;

//Warm start Module Context structure example
typedef struct
{
	/* declare the Warm Start Module Context data here */
} warm_start_context;

} /* myDemoPong2_AM */

#endif /* MYDEMOPONG2_AM_USER_CONTEXT_HPP */