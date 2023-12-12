/* Generated by PARSEC */
/* Module Implementation for myDemoPing_AM
Done by Florian using Jinja */

#include <assert.h>
#include "ECOA.hpp"


#include "mylib.hpp"

#include <stdio.h>
#include "ldp_fifo_manager.h"
#include "ldp_structures.h"
#include <stdio.h>
#include "myDemoPing_AM.hpp"

namespace myDemoPing_AM
{

/* Entry points for lifecycle operations */
void Module::INITIALIZE__received(){
	user.nb_pong_received = 0;
	user.async0_response_received = 0;
	user.async1_response_received = 0;

	user.pong_received;
	user.pong2_received;
	user.pong3_received;
}
void Module::START__received(){
	apr_sleep(200000);
	ECOA::return_status ret;
    ECOA::uint32 ID;
    mylib::coord coord_send1 = { .x = 1516, .y = 151617};
	mylib::t1 ping_num = 14;
    ret = container->RR_msg_async1__request_async(ID, ping_num, coord_send1);
    assert(ret.value == ECOA::return_status::OK);

    mylib::coord coord_send = { .x = 1314, .y = 131415};
    ret = container->RR_msg_async0__request_async(ID, ping_num, coord_send);
    assert(ret.value == ECOA::return_status::OK);
}
void Module::STOP__received(){
/* @TODO TODO - To be implemented */
}
void Module::SHUTDOWN__received(){
/* @TODO TODO - To be implemented */
}

int nb_tick = 0;
void Module::TriggerPingEvent__received()
{

	mylib::t1 ping_num = 14;
	mylib::coord ping_coord = { .x = 30, .y = 40};
	mylib::Test_array ping_array = { 5 , {61,62,63,64,65} };
	mylib::Test_fixed_array ping_fixedarray = {7,8,9,10,11,12,13,14,15,16,17,18};
	mylib::Test_enum ping_testenum(mylib::Test_enum::SATURDAY);

	if (nb_tick<3)
	{
		(this->container)->Ping__send(ping_coord, ping_num, ping_array, ping_fixedarray, ping_testenum);
		nb_tick += 1;
	}
	else if (user.nb_pong_received == 9 && user.async0_response_received == 1 && user.async1_response_received == 1 && user.pong_received == 1 && user.pong2_received ==1 && user.pong3_received == 1){
		mylib::t1 nombre_ping_to_kill = 999;
		(this->container)->Ping__send(ping_coord, nombre_ping_to_kill, ping_array, ping_fixedarray, ping_testenum);
	}
}





void Module::RR_msg_async0__response_received(const ECOA::uint32 ID, const ECOA::return_status status,
	const mylib::t1 nb_received, const mylib::coord& coord_received)
{
	if (coord_received.x == 1314 && coord_received.y == 131415){
		user.async0_response_received = 1;
	}else{
		assert(0);
	}
}

void Module::Pong__received(  const mylib::coord& recordwithpong, const mylib::t1 nb_pong, const mylib::Test_array& arraywithpong, const mylib::Test_fixed_array& fixedarraywithpong, const mylib::Test_enum enumwithpong)
{
	if (recordwithpong.x == 31 && recordwithpong.y == 41 && nb_pong == 15){
		user.pong_received = 1;
	}
	else if (recordwithpong.x == 32 && recordwithpong.y == 42 && nb_pong == 16){
		user.pong2_received = 1;
	}
	else if (recordwithpong.x == 33 && recordwithpong.y == 43 && nb_pong == 17){
		user.pong3_received = 1;
	}
	else{
		assert(0);
	}
	user.nb_pong_received += 1;
}



void Module::RR_msg_async1__response_received(const ECOA::uint32 ID, const ECOA::return_status status,
	const mylib::t1 nb_received, const mylib::coord& coord_received)
{
	if (coord_received.x == 1516 && coord_received.y == 151617){
		user.async1_response_received = 1;
	}else{
		assert(0);
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
