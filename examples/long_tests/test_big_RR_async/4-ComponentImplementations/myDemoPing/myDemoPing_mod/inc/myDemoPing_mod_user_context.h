/* Generated by PARSEC */
/* Module User Context Header for module myDemoPing_mod */
#if !defined(__MYDEMOPING_MOD_USER_CONTEXT_H__)
#define __MYDEMOPING_MOD_USER_CONTEXT_H__

#if defined(__cplusplus)
extern "C" {
#endif

/*
 * @file myDemoPing_mod_user_context.h
 */

#include "lib_array.h"
/* Module User Context Structure */
typedef struct
{
  /*********** USER ***********/
  int nb_pong_received;

  ECOA__uint32 ID_RR_1k;
  ECOA__uint32 ID_RR_4k;
  ECOA__uint32 ID_RR_16k;
  ECOA__uint32 ID_RR_64k;
  ECOA__uint32 ID_RR_256k;
  ECOA__uint32 ID_RR_10m;

  /*********** USER ***********/
} myDemoPing_mod_user_context;
/* Warm start Module Context structure */
typedef struct
{
   /************* START USER-WRITTEN CODE *************/

   /*************** END USER-WRITTEN CODE *************/
} myDemoPing_mod_warm_start_context;

#if defined(__cplusplus)
}
#endif

#endif  /* __MYDEMOPING_MOD_USER_CONTEXT_H__ */
