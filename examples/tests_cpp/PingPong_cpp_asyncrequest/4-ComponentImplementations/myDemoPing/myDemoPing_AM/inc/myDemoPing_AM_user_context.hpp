/* Done by Florian using Jinja */

#if !defined(_MYDEMOPING_AM_USER_CONTEXT_HPP)
#define _MYDEMOPING_AM_USER_CONTEXT_HPP

/*Standaard types*/
#include <ECOA.hpp>

/*Additionnaly created types*/
#include "mylib.hpp"

/*Container types*/
#include "myDemoPing_AM_container_types.hpp"

namespace myDemoPing_AM
{

typedef struct
{
	ECOA::uint8 nb_pong_received;
	ECOA::boolean8 async0_response_received;
	ECOA::boolean8 async1_response_received;

	ECOA::boolean8 pong2_received;
	ECOA::boolean8 pong3_received;
	ECOA::boolean8 pong_received;

} user_context;
//Warm start Module Context structure example
typedef struct
{
	/* declare the Warm Start Module Context data here */

} warm_start_context;

} /* myDemoPing_AM */

#endif /* MYDEMOPING_AM_USER_CONTEXT_HPP */