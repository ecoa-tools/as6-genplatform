/* Generated by PARSEC */
/* Module Implementation for mydemoServer0_AM
Done by Florian using Jinja */

#include "ECOA.hpp"
#include "mydemoServer0_AM.hpp"


#include "mylib.hpp"


namespace mydemoServer0_AM
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

	
		
void Module::sPing__received()
{
/* @TODO TODO - To be implemented */
}
	
		
Module::Module(Container* c)
: container(c)
{}


/* Fault Handling API , linked to another namespace (fault_handler_impl_name) */

extern "C" {
	
	Module* mydemoServer0_AM__new_instance(Container* container)
	{
		return new Module(container);
	}
}

} /* ????? */

} /* namespace mydemoServer0_AM */
