/* Generated by PARSEC */
/* Module User Context Header for module myDemoReceiver_AM */
#if !defined(_MYDEMORECEIVER_AM_USER_CONTEXT_H)
#define _MYDEMORECEIVER_AM_USER_CONTEXT_H

#if defined(__cplusplus)
extern "C" {
#endif

/*
 * @file myDemoReceiver_AM_user_context.h
 */

#include "ECOA.h"
#include "lib_module.h"
/* Module User Context Structure */
typedef struct
{
    /*********** START USER-WRITTEN USER ***********/
    int event_received;
    int request_async_received;
    int request_sync_received;
    int vd_notif_received;
    /*********** START USER-WRITTEN USER ***********/
} myDemoReceiver_AM_user_context;

#if defined(__cplusplus)
}
#endif

#endif  /* _MYDEMORECEIVER_AM_USER_CONTEXT_H */
