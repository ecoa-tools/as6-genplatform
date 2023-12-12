#if !defined(_Receiver_AM_USER_CONTEXT_H)
#define _Receiver_AM_USER_CONTEXT_H
#if defined(__cplusplus)
extern "C" {  
#endif

/* @file Receiver_AM_user_context.h
 */

/* User Module Context structure */
typedef struct
{
   /************* START USER-WRITTEN CODE *************/
	int nb_ping;
   /*************** END USER-WRITTEN CODE *************/
} Receiver_AM_user_context;


/* Warm start Module Context structure */
typedef struct
{
   /************* START USER-WRITTEN CODE *************/

   /*************** END USER-WRITTEN CODE *************/
} Receiver_AM_warm_start_context;

#if defined(__cplusplus)
} 
#endif
#endif  /* _Receiver_AM_USER_CONTEXT_H */
