#if !defined(_mySender_USER_CONTEXT_H)
#define _mySender_USER_CONTEXT_H
#if defined(__cplusplus)
extern "C" {  
#endif

/* @file mySender_user_context.h
 */

/* User Module Context structure */
typedef struct
{
   /************* START USER-WRITTEN CODE *************/
	ECOA__uint32 check_nb;
	int nb_run;
   /*************** END USER-WRITTEN CODE *************/
} mySender_user_context;


/* Warm start Module Context structure */
typedef struct
{
   /************* START USER-WRITTEN CODE *************/

   /*************** END USER-WRITTEN CODE *************/
} mySender_warm_start_context;

#if defined(__cplusplus)
} 
#endif
#endif  /* _mySender_USER_CONTEXT_H */
