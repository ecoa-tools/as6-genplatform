#if !defined(_myDemoPing_AM_USER_CONTEXT_H)
#define _myDemoPing_AM_USER_CONTEXT_H
#if defined(__cplusplus)
extern "C" {  
#endif

/* @file myDemoPing_AM_user_context.h
 */

/* User Module Context structure */
typedef struct
{
   /************* START USER-WRITTEN CODE *************/
	ECOA__uint32 check_nb;
	int nb_run;
   /*************** END USER-WRITTEN CODE *************/
} myDemoPing_AM_user_context;


/* Warm start Module Context structure */
typedef struct
{
   /************* START USER-WRITTEN CODE *************/

   /*************** END USER-WRITTEN CODE *************/
} myDemoPing_AM_warm_start_context;

#if defined(__cplusplus)
} 
#endif
#endif  /* _myDemoPing_AM_USER_CONTEXT_H */
