/* Generated by PARSEC */
/* Module User Context Header for module myWriter_mod */
#if !defined(_MYWRITER_MOD_USER_CONTEXT_H)
#define _MYWRITER_MOD_USER_CONTEXT_H

#if defined(__cplusplus)
extern "C" {
#endif

/*
 * @file myWriter_mod_user_context.h
 */

#include "ECOA.h"
#include "VD_lib.h"
/* Module User Context Structure */
typedef struct
{
    /*********** START USER-WRITTEN USER ***********/
VD_lib__vector_data old_vector;
int nb_write;
    /*********** START USER-WRITTEN USER ***********/
} myWriter_mod_user_context;


/* Warm start Module Context structure */
typedef struct
{
    /************* START USER-WRITTEN CODE *************/

    /*************** END USER-WRITTEN CODE *************/
} myWriter_mod_warm_start_context;

#if defined(__cplusplus)
}
#endif

#endif  /* _myWRITER_MOD_USER_CONTEXT_H */
