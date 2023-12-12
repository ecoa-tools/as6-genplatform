/* Generated by PARSEC */
/* Module Implementation for satellite_Cpp*/

#include "ECOA.hpp"
#include "satellite_Cpp.hpp"


#include "ECOA.hpp"
#include "myLib.hpp"
#include <assert.h>
#include <stdarg.h>
#include <stdio.h>


namespace satellite_Cpp
{

static void print_log(Container* c, const char *format, ...){
    va_list vl;
    ECOA::log log;

    va_start(vl, format);
    vsnprintf(log.data, ECOA::LOG_MAXSIZE, format, vl);
    va_end( vl);

    c->log_trace(log);
}

/* Entry points for lifecycle operations */

void Module::INITIALIZE__received(){
    /* @TODO TODO - To be implemented */
}

void Module::START__received(){
    ECOA::uint32 sat_num;
    container->get_satellite_num_value(sat_num);

    user.position.x=sat_num;
    user.position.y=1;
    user.position.z=2;

    for(int i=0; i<myLib::array_data_MAXSIZE; i++){
        user.data[i] = sat_num+i;
    }

    print_log(container, "user ctx (cpp) : %i", sizeof(user));
}

void Module::STOP__received(){
    /* @TODO TODO - To be implemented */
}

void Module::SHUTDOWN__received(){
    /* @TODO TODO - To be implemented */
}

void Module::satellite_position__request_received(const ECOA::uint32 ID){
    ECOA::uint32 sat_num;
    container->get_satellite_num_value(sat_num);

    print_log(container, "satellite %i received a position request", sat_num);

    assert(container->satellite_position__response_send(ID,
                                                        user.position,
                                                        sat_num) == ECOA::return_status::OK);

    container->send_data__send(user.data, sat_num);
}


/* Fault Handling API , linked to another namespace (fault_handler_impl_name) */

extern "C" {

    Module* satellite_Cpp__new_instance()
    {
        return new Module();
    }
}

} /* namespace satellite_Cpp */