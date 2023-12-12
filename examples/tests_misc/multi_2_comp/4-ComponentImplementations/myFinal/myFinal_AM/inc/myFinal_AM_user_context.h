#if !defined(_myFinal_AM_USER_CONTEXT_H)
#define _myFinal_AM_USER_CONTEXT_H
#if defined(__cplusplus)
extern "C" {  
#endif

/* @file myFinal_AM_user_context.h
 */

/* User Module Context structure */
typedef struct
{
   /************* START USER-WRITTEN CODE *************/
	int nb;
	int run_nb;
   /*************** END USER-WRITTEN CODE *************/
} myFinal_AM_user_context;


/* Warm start Module Context structure */
typedef struct
{
   /************* START USER-WRITTEN CODE *************/

   /*************** END USER-WRITTEN CODE *************/
} myFinal_AM_warm_start_context;

#if defined(__cplusplus)
} 
#endif
#endif  /* _myFinal_AM_USER_CONTEXT_H */
