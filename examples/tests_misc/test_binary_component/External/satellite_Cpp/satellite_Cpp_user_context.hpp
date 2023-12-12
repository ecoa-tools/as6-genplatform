#if !defined(_SATELLITE_CPP_USER_CONTEXT_HPP)
#define _SATELLITE_CPP_USER_CONTEXT_HPP

/*Standaard types*/
#include <ECOA.hpp>

/*Additionnaly created types*/
#include "ECOA.hpp"
#include "myLib.hpp"

/*Container types*/
#include "satellite_Cpp_container_types.hpp"

namespace satellite_Cpp
{

    typedef struct
    {
        myLib::position position;
        myLib::array_data data;
    } user_context;

    //Warm start Module Context structure example
    typedef struct
    {
        /* declare the Warm Start Module Context data here */

    } warm_start_context;

} /* satellite_Cpp */

#endif /* SATELLITE_CPP_USER_CONTEXT_HPP */