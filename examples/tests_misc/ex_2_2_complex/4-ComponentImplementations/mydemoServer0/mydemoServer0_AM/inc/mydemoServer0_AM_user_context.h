#if !defined(_mydemoServer0_AM_USER_CONTEXT_H)
#define _mydemoServer0_AM_USER_CONTEXT_H
#if defined(__cplusplus)
extern "C" {  
#endif

/* @file mydemoServer0_AM_user_context.h
 */

/* User Module Context structure */
typedef struct
{
   /************* START USER-WRITTEN CODE *************/
	int nb_ping;
   /*************** END USER-WRITTEN CODE *************/
} mydemoServer0_AM_user_context;


/* Warm start Module Context structure */
typedef struct
{
   /************* START USER-WRITTEN CODE *************/

   /*************** END USER-WRITTEN CODE *************/
} mydemoServer0_AM_warm_start_context;

#if defined(__cplusplus)
} 
#endif
#endif  /* _mydemoServer0_AM_USER_CONTEXT_H */
