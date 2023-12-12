/* Generated by PARSEC */
/* Helpers for the Module Implementation myElder_Main_impl */

#if !defined(MYELDER_MAIN_IMPL_HELPERS)
#define MYELDER_MAIN_IMPL_HELPERS
#include "ECOA.h"
#include "myElder_Main_impl.h"

#include "ECOA.h"
#include "libmarx.h"

#if defined(__cplusplus)
extern "C" {
#endif

extern const char* MYELDER_MAIN_IMPL;

void myElder_Main_impl_log_info(myElder_Main_impl__context* context, char *msg, ...);
void myElder_Main_impl_log(myElder_Main_impl__context* context, char *msg, ...);


void myElder_Main_impl__request_transaction_1(myElder_Main_impl__context* context, libmarx__T_Data* input, libmarx__T_Data* output);

void myElder_Main_impl__request_transaction_2(myElder_Main_impl__context* context, libmarx__T_Data* input, libmarx__T_Data* output);

void myElder_Main_impl__get_information(myElder_Main_impl__context* context, libmarx__T_Data* data);

#if defined(__cplusplus)
}
#endif
#endif /* MYELDER_MAIN_IMPL_HELPERS */
