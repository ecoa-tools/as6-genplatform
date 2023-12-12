/*
 * @file myLib.hpp
 * This is data-type declaration file
 * This file is generated by the ECOA tools and shall not be modified
 */


#include "ECOA.hpp"

#if !defined(_myLib_HPP)
#define _myLib_HPP
#if defined(__cplusplus)
extern "C" {
#endif /* __cplusplus */

namespace myLib{


/* Type array_data */
const ECOA::uint32 array_data_MAXSIZE =20;
typedef ECOA::uint32 array_data[array_data_MAXSIZE];

/* Type position */
typedef struct
{
  ECOA::uint32 x;
  ECOA::uint32 y;
  ECOA::uint32 z;
} position; /* example */

} /* myLib */ 
#if defined(__cplusplus)
}
#endif /* __cplusplus */

#endif /* _myLib_HPP */
