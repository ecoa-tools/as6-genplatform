/* Generated by PARSEC */
/* Module Implementation myDemoPong_mod1_impl */

#include "ECOA.h"

#include "pingpong.h"
#include <apr_time.h>
#include <assert.h>
#include "myDemoPong_mod1_impl.h"
/* Entry points for lifecycle operations */
void myDemoPong_mod1_impl__INITIALIZE__received(myDemoPong_mod1_impl__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoPong_mod1_impl__REINITIALIZE__received(myDemoPong_mod1_impl__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoPong_mod1_impl__START__received(myDemoPong_mod1_impl__context* context)
{

}

void myDemoPong_mod1_impl__STOP__received(myDemoPong_mod1_impl__context* context)
{
  /* @TODO TODO - To be implemented */
}

void myDemoPong_mod1_impl__SHUTDOWN__received(myDemoPong_mod1_impl__context* context)
{
  /* @TODO TODO - To be implemented */
}

int nb=0;
void myDemoPong_mod1_impl__Ping1__request_received(myDemoPong_mod1_impl__context* context, const ECOA__uint32 ID, const pingpong__T_2D_Position* Ping_Position, const ECOA__uint32 Ping_Target)
{
  printf("received ping %i\n", nb++);
  if(nb == 1)
  	apr_sleep(1*1000*1000);
  assert(nb < 9);
  myDemoPong_mod1_impl_container__Ping2__response_send(context, ID, Ping_Position, Ping_Target);
}

void myDemoPong_mod1_impl__Ping2__request_received(myDemoPong_mod1_impl__context* context, const ECOA__uint32 ID, const pingpong__T_2D_Position* Ping_Position, const ECOA__uint32 Ping_Target)
{
  printf("received ping2 : will never response\n");
}

