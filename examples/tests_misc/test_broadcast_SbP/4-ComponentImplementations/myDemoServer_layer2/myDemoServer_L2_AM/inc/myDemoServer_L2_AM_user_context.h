#if !defined(_myDemoServer_L2_AM_USER_CONTEXT_H)
#define _myDemoServer_L2_AM_USER_CONTEXT_H
#if defined(__cplusplus)
extern "C" {  
#endif

/* @file myDemoServer_L2_AM_user_context.h
 */

/* User Module Context structure */
typedef struct
{
   /************* START USER-WRITTEN CODE *************/
	int nb_of_pong;
   /*************** END USER-WRITTEN CODE *************/
} myDemoServer_L2_AM_user_context;


/* Warm start Module Context structure */
typedef struct
{
   /************* START USER-WRITTEN CODE *************/

   /*************** END USER-WRITTEN CODE *************/
} myDemoServer_L2_AM_warm_start_context;

#if defined(__cplusplus)
} 
#endif
#endif  /* _myDemoServer_L2_AM_USER_CONTEXT_H */
