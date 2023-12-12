/* Done by Florian using Jinja */

#if !defined(_MYCOMPREADER_MOD_USER_CONTEXT_HPP)
#define _MYCOMPREADER_MOD_USER_CONTEXT_HPP

/*Standaard types*/
#include <ECOA.hpp>

/*Additionnaly created types*/
#include "VD_lib.hpp"

/*Container types*/
#include "myCompReader_mod_container_types.hpp"

namespace myCompReader_mod
{

// User Module Context structure example
typedef struct
{
 //declare the User Module Context "local" date here
 ECOA::int8 vector0_read;
 ECOA::int8 vector1_read;

} user_context;

//Warm start Module Context structure example
typedef struct
{

} warm_start_context;

} /* myCompReader_mod */

#endif /* MYCOMPREADER_MOD_USER_CONTEXT_HPP */