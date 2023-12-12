#include "machine1_fault_handler.h"

void machine1__error_notification (
  machine1__context* context, 
  ECOA__error_id error_id,
  const ECOA__timestamp *timestamp,
  ECOA__asset_id asset_id,
  ECOA__asset_type asset_type,
  ECOA__error_type error_type)
{
  ECOA__log log;

  log.current_size = snprintf ((char*)log.data, ECOA__LOG_MAXSIZE, "in FAULT HANDLER user code, count=%d", error_id);
  machine1_container__log_info(context, log);

  if (context->last_timestamp.seconds != 0)
  {
    log.current_size = snprintf ((char*)log.data, ECOA__LOG_MAXSIZE, "%d seconds since last fault",
      timestamp->seconds - context->last_timestamp.seconds);
    machine1_container__log_info(context, log);
  }

//  if (asset_type == ECOA__asset_type_PROTECTION_DOMAIN) {
//    log.current_size = snprintf ((char*)log.data, ECOA__LOG_MAXSIZE, "FAULT HANDLER: restarting protection domain %d ...", asset_id);
//    machine1_container__log_info(context, log);
//    machine1_container__recovery_action (context, 
//      ECOA__recovery_action_type_WARM_RESTART, 
//      asset_id, asset_type);
//  }

  context->last_timestamp = *timestamp;
}