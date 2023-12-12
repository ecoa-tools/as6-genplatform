#if !defined(_MYDEMORECEIVER_AM_USER_CONTEXT_HPP)
#define _MYDEMORECEIVER_AM_USER_CONTEXT_HPP

/*Standaard types*/
#include <ECOA.hpp>

/*Additionnaly created types*/
#include "ECOA.hpp"
#include "lib_module.hpp"

/*Container types*/
#include "myDemoReceiver_AM_container_types.hpp"

namespace myDemoReceiver_AM
{

	typedef struct
	{
    int event_received;
    int request_async_received;
    int request_sync_received;
    int vd_notif_received;
	} user_context;


} /* myDemoReceiver_AM */

#endif /* MYDEMORECEIVER_AM_USER_CONTEXT_HPP */