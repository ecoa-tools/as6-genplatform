/* Generated by PARSEC */
/* Module User Context Header for module myCompReader_mod */
#if !defined(_MYCOMPREADER_MOD_USER_CONTEXT_H)
#define _MYCOMPREADER_MOD_USER_CONTEXT_H

#if defined(__cplusplus)
extern "C" {
#endif

/*
 * @file myCompReader_mod_user_context.h
 */

#include "ECOA.h"
#include "VD_lib.h"
/* Module User Context Structure */
typedef struct
{
    /*********** START USER-WRITTEN USER ***********/
	int num_vector0;
	int num_vector1;
    /*********** START USER-WRITTEN USER ***********/
} myCompReader_mod_user_context;


/* Warm start Module Context structure */
typedef struct
{
    /************* START USER-WRITTEN CODE *************/

    /*************** END USER-WRITTEN CODE *************/
} myCompReader_mod_warm_start_context;

#if defined(__cplusplus)
}
#endif

#endif  /* _MYCOMPREADER_MOD_USER_CONTEXT_H */
