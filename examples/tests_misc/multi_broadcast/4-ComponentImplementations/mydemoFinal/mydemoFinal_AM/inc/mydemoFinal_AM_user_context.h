#if !defined(_mydemoFinal_AM_USER_CONTEXT_H)
#define _mydemoFinal_AM_USER_CONTEXT_H
#if defined(__cplusplus)
extern "C" {  
#endif

/* @file mydemoFinal_AM_user_context.h
 */

/* User Module Context structure */
typedef struct
{
   /************* START USER-WRITTEN CODE *************/
	int nb_pong;
   /*************** END USER-WRITTEN CODE *************/
} mydemoFinal_AM_user_context;


/* Warm start Module Context structure */
typedef struct
{
   /************* START USER-WRITTEN CODE *************/

   /*************** END USER-WRITTEN CODE *************/
} mydemoFinal_AM_warm_start_context;

#if defined(__cplusplus)
} 
#endif
#endif  /* _mydemoFinal_AM_USER_CONTEXT_H */
