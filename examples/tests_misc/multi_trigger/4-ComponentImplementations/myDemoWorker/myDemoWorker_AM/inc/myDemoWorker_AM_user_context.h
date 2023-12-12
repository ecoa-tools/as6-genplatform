#if !defined(_myDemoWorker_AM_USER_CONTEXT_H)
#define _myDemoWorker_AM_USER_CONTEXT_H
#if defined(__cplusplus)
extern "C" {  
#endif

/* @file myDemoWorker_AM_user_context.h
 */

/* User Module Context structure */
typedef struct
{
   /************* START USER-WRITTEN CODE *************/
int trigger0;
int trigger1;
 ECOA__hr_time xxxtime;
   /*************** END USER-WRITTEN CODE *************/
} myDemoWorker_AM_user_context;


/* Warm start Module Context structure */
typedef struct
{
   /************* START USER-WRITTEN CODE *************/

   /*************** END USER-WRITTEN CODE *************/
} myDemoWorker_AM_warm_start_context;

#if defined(__cplusplus)
} 
#endif
#endif  /* _myDemoWorker_AM_USER_CONTEXT_H */
