/* Generated by PARSEC */
/* Module Implementation for myDemoPing_AM_cpp*/

#include "ECOA.hpp"
#include "myDemoPing_AM_cpp.hpp"


#include "ECOA.hpp"
#include "libRoot.hpp"
#include "libRoot__level1A.hpp"

#include "assert.h"
#include <unistd.h>

namespace myDemoPing_AM_cpp
{

/* Entry points for lifecycle operations */

void Module::INITIALIZE__received(){
	/* @TODO TODO - To be implemented */
}

void Module::START__received(){
	/* @TODO TODO - To be implemented */
	libRoot::array_1A in_param3;
	libRoot::level1A::simple1B out_param1;
	ECOA::uint32 out_param2;
	libRoot::array_1A out_param3;
	ECOA::boolean8 out_bool;
	while(container->sync_req__request_sync(13, 14, in_param3, out_param1, out_param2, out_param3, out_bool) != ECOA::return_status::OK){
		sleep(1);
	}

	assert(out_param1 == 13);
	assert(out_param2 == 14);
	assert(out_bool);
	ECOA::uint32 ID;
	assert(container->async_req__request_async(ID , 14, 15, in_param3) == ECOA::return_status::OK);
}

void Module::STOP__received(){
	/* @TODO TODO - To be implemented */
}

void Module::SHUTDOWN__received(){
	/* @TODO TODO - To be implemented */
}

void Module::external_event__received(const libRoot::level1A::simple1B param1, const ECOA::uint32 param2, const libRoot::array_1A& param3){
	/* @TODO TODO - To be implemented */
}

void Module::async_req__response_received(const ECOA::uint32 ID, const ECOA::return_status status, const libRoot::level1A::simple1B out_param1, const ECOA::uint32 out_param2, const libRoot::array_1A& out_param3, const ECOA::boolean8 out_bool){
	assert(status == ECOA::return_status::OK);
	assert(out_param1 == 14);
	assert(out_param2 == 15);
	assert(!out_bool);
	container->event_sent__send(out_param1, out_param2, out_param3);
}

/* Fault Handling API , linked to another namespace (fault_handler_impl_name) */

extern "C" {

	Module* myDemoPing_AM_cpp__new_instance()
	{
		return new Module();
	}
}

} /* namespace myDemoPing_AM_cpp */
