#if !defined(_myReceiverCom_AM_AM_USER_CONTEXT_H)
#define _myReceiverCom_AM_AM_USER_CONTEXT_H
#if defined(__cplusplus)
extern "C" {  
#endif

/* @file myReceiverCom_AM_AM_user_context.h
 */

/* User Module Context structure */
typedef struct
{
   /************* START USER-WRITTEN CODE *************/
	
	int nb_ping;
   /*************** END USER-WRITTEN CODE *************/
} myReceiverCom_AM_AM_user_context;


/* Warm start Module Context structure */
typedef struct
{
   /************* START USER-WRITTEN CODE *************/

   /*************** END USER-WRITTEN CODE *************/
} myReceiverCom_AM_AM_warm_start_context;

#if defined(__cplusplus)
} 
#endif
#endif  /* _myReceiverCom_AM_AM_USER_CONTEXT_H */
