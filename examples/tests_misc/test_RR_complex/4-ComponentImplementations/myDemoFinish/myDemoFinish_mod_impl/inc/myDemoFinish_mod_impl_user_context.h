/* Generated by PARSEC */
/* Module User Context Header for module myDemoFinish_mod_impl */
#if !defined(_MYDEMOFINISH_MOD_IMPL_USER_CONTEXT_H)
#define _MYDEMOFINISH_MOD_IMPL_USER_CONTEXT_H

#if defined(__cplusplus)
extern "C" {
#endif

/*
 * @file myDemoFinish_mod_impl_user_context.h
 */

#include "pingpong.h"
/* Module User Context Structure */
typedef struct
{
    /*********** START USER-WRITTEN USER ***********/
	int finish_num;
    /*********** START USER-WRITTEN USER ***********/
} myDemoFinish_mod_impl_user_context;


/* Warm start Module Context structure */
typedef struct
{
    /************* START USER-WRITTEN CODE *************/

    /*************** END USER-WRITTEN CODE *************/
} myDemoFinish_mod_impl_warm_start_context;

#if defined(__cplusplus)
}
#endif

#endif  /* _MYDEMOFINISH_MOD_IMPL_USER_CONTEXT_H */