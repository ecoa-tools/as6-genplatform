/* Generated by PARSEC */
/* Module Implementation for mydemoClient0_AM
Done by Florian using Jinja */

#include "ECOA.hpp"
#include "mydemoClient0_AM.hpp"


#include "mylib.hpp"


namespace mydemoClient0_AM
{

/* Entry points for lifecycle operations */void Module::INITIALIZE__received(){
/* @TODO TODO - To be implemented */
}
void Module::START__received(){
/* @TODO TODO - To be implemented */
}
void Module::STOP__received(){
/* @TODO TODO - To be implemented */
}
void Module::SHUTDOWN__received(){
/* @TODO TODO - To be implemented */
}

	
		
Module::Module(Container* c)
: container(c)
{}


/* Fault Handling API , linked to another namespace (fault_handler_impl_name) */

extern "C" {
	
	Module* mydemoClient0_AM__new_instance(Container* container)
	{
		return new Module(container);
	}
}

} /* ????? */

} /* namespace mydemoClient0_AM */
