/* Generated by PARSEC */
/* Module User Context Header for module myCompWritter_mod */
#if !defined(_MYCOMPWRITTER_MOD_USER_CONTEXT_H)
#define _MYCOMPWRITTER_MOD_USER_CONTEXT_H

#if defined(__cplusplus)
extern "C" {
#endif

/*
 * @file myCompWritter_mod_user_context.h
 */

#include "VD_lib.h"
/* Module User Context Structure */
typedef struct
{
    /*********** START USER-WRITTEN USER ***********/
    ECOA__uint32 mod_id;
    VD_lib__vector_data saved_vector;

    /*********** START USER-WRITTEN USER ***********/
} myCompWritter_mod_user_context;


/* Warm start Module Context structure */
typedef struct
{
    /************* START USER-WRITTEN CODE *************/

    /*************** END USER-WRITTEN CODE *************/
} myCompWritter_mod_warm_start_context;

#if defined(__cplusplus)
}
#endif

#endif  /* _MYCOMPWRITTER_MOD_USER_CONTEXT_H */
