/* Generated by PARSEC */
/* Module Header satellite_Cpp */

#if !defined(_satellite_Cpp_HPP)
#define _satellite_Cpp_HPP


#include "ECOA.hpp"
#include "satellite_Cpp_container.hpp"
#include "satellite_Cpp_container_types.hpp"
#include "satellite_Cpp_user_context.hpp"
#include "ECOA.hpp"
#include "myLib.hpp"

namespace satellite_Cpp
{

class Module
{
    public:

        /* Entry points for lifecycle operations */

        void INITIALIZE__received();

        void START__received();

        void STOP__received();

        void SHUTDOWN__received();

        // warm_start_context warm_start;

        void satellite_position__request_received(const ECOA::uint32 ID);

        Container* container;

        user_context user;

}; /* Class Module */

extern "C" {
    Module* satellite_Cpp__new_instance();
}

} /* namespace satellite_Cpp */

#endif  /* _SATELLITE_CPP_HPP */