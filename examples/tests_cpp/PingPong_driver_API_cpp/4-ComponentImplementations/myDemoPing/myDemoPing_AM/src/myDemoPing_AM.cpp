/* Generated by PARSEC */
/* Module Implementation for myDemoPing_AM*/

#include <assert.h>
#include "ECOA.hpp"


#include "pingpong.hpp"

#include "myDemoPing_External_Interface.h"
#include "apr_time.h"
#include "ldp_mod_container_util.h"
#include <stdio.h>
#include "myDemoPing_AM.hpp"

namespace myDemoPing_AM
{

/* Entry points for lifecycle operations */

void Module::INITIALIZE__received(){
	/* @TODO TODO - To be implemented */
}

void Module::START__received(){
  apr_sleep(200000);
  myDemoPing__Start_extern(60223, 31415);

  ECOA__duration delayDuration;
  delayDuration.seconds = 1;
  delayDuration.nanoseconds = 0;
  myDemoPing__Set_trigger_extern(&delayDuration, 60223, 31415);
  myDemoPing__Set_trigger_extern(&delayDuration, 60223, 31415);
}

void Module::STOP__received(){
	/* @TODO TODO - To be implemented */
}

void Module::SHUTDOWN__received(){
	/* @TODO TODO - To be implemented */
}

void Module::Start_test__received(const ECOA::uint32 param1, const ECOA::uint16 param2){
  //print_log(context, "Send Ping");
  assert(param1 == 60223);
  assert(param2 == 31415);
  container->Ping__send();
}

int count =0;
void Module::Pong__received(){
  //print_log(context, "Pong received !!");
  count++;

  if(count >= 3){

  //print_log(context, "\033[1;32m SUCCESS  \033[0m");
  //fflush(stdout);
  //ldp_kill_platform((ldp_module_context*)context->platform_hook);
  	container->Ping__send();
  }
}


/* Fault Handling API , linked to another namespace (fault_handler_impl_name) */

extern "C" {

	Module* myDemoPing_AM__new_instance()
	{
		return new Module();
	}
}

} /* namespace myDemoPing_AM */
