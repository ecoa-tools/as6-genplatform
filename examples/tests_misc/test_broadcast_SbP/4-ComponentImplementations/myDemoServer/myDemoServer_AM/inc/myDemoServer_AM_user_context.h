#if !defined(_myDemoServer_AM_USER_CONTEXT_H)
#define _myDemoServer_AM_USER_CONTEXT_H
#if defined(__cplusplus)
extern "C" {  
#endif

/* @file myDemoServer_AM_user_context.h
 */

/* User Module Context structure */
typedef struct
{
   /************* START USER-WRITTEN CODE *************/
	int ping_received;
   /*************** END USER-WRITTEN CODE *************/
} myDemoServer_AM_user_context;


/* Warm start Module Context structure */
typedef struct
{
   /************* START USER-WRITTEN CODE *************/

   /*************** END USER-WRITTEN CODE *************/
} myDemoServer_AM_warm_start_context;

#if defined(__cplusplus)
} 
#endif
#endif  /* _myDemoServer_AM_USER_CONTEXT_H */
