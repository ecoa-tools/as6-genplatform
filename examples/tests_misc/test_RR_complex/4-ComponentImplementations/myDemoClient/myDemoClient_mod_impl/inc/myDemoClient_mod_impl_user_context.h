/* Generated by PARSEC */
/* Module User Context Header for module myDemoClient_mod_impl */
#if !defined(_MYDEMOCLIENT_MOD_IMPL_USER_CONTEXT_H)
#define _MYDEMOCLIENT_MOD_IMPL_USER_CONTEXT_H

#if defined(__cplusplus)
extern "C" {
#endif

/*
 * @file myDemoClient_mod_impl_user_context.h
 */

#include "pingpong.h"
/* Module User Context Structure */
typedef struct
{
    /*********** START USER-WRITTEN USER ***********/

	int response_num;
    /*********** START USER-WRITTEN USER ***********/
} myDemoClient_mod_impl_user_context;


/* Warm start Module Context structure */
typedef struct
{
    /************* START USER-WRITTEN CODE *************/

    /*************** END USER-WRITTEN CODE *************/
} myDemoClient_mod_impl_warm_start_context;

#if defined(__cplusplus)
}
#endif

#endif  /* _MYDEMOCLIENT_MOD_IMPL_USER_CONTEXT_H */
