
/********** Time related API *************/
ECOA__return_status #PREFIXE#_#MODULE_IMPL_NAME#__get_absolute_system_time(
        #MODULE_IMPL_NAME#__context *context,
        ECOA__global_time *absolute_system_time) {
    ECOA__return_status return_status;

    return_status = #MODULE_IMPL_NAME#_container__get_absolute_system_time(context, absolute_system_time);

    if(return_status == ECOA__return_status_CLOCK_UNSYNCHRONIZED) {
        #PREFIXE#_#MODULE_IMPL_NAME#__log_warning(context, "Clock Unsynchronized when get_absolute_system_time");
    } else if(return_status != ECOA__return_status_OK) {
        #PREFIXE#_#MODULE_IMPL_NAME#__log_warning(context, "Unknown error when get_absolute_system_time");
    }
    return return_status;
}

ECOA__return_status #PREFIXE#_#MODULE_IMPL_NAME#__get_relative_local_time(
        #MODULE_IMPL_NAME#__context *context,
        ECOA__hr_time *relative_local_time) {
    ECOA__return_status return_status;
    return_status = ECOA__return_status_OK;

    #MODULE_IMPL_NAME#_container__get_relative_local_time(context, relative_local_time);

    return return_status;
}

ECOA__return_status #PREFIXE#_#MODULE_IMPL_NAME#__get_UTC_time(
        #MODULE_IMPL_NAME#__context *context,
        ECOA__global_time *utc_time) {
    ECOA__return_status return_status;

    return_status = #MODULE_IMPL_NAME#_container__get_UTC_time(context, utc_time);

    if(return_status == ECOA__return_status_CLOCK_UNSYNCHRONIZED) {
        #PREFIXE#_#MODULE_IMPL_NAME#__log_warning(context, "Clock Unsynchronized when get_UTC_time");
    } else if(return_status != ECOA__return_status_OK) {
        #PREFIXE#_#MODULE_IMPL_NAME#__log_warning(context, "Unknown error when get_UTC_time");
    }
    return return_status;
}

ECOA__return_status #PREFIXE#_#MODULE_IMPL_NAME#__get_relative_local_time_resolution(
        #MODULE_IMPL_NAME#__context *context,
        ECOA__duration *relative_local_time_resolution){

    ECOA__return_status return_status;
    return_status = ECOA__return_status_OK;
    #MODULE_IMPL_NAME#_container__get_relative_local_time_resolution(context, relative_local_time_resolution);

    return return_status;
}

ECOA__return_status #PREFIXE#_#MODULE_IMPL_NAME#__get_UTC_time_resolution(
        #MODULE_IMPL_NAME#__context *context,
        ECOA__duration *utc_time_resolution) {

    ECOA__return_status return_status;
    return_status = ECOA__return_status_OK;
    #MODULE_IMPL_NAME#_container__get_UTC_time_resolution(context, utc_time_resolution);

    return return_status;
}

ECOA__return_status #PREFIXE#_#MODULE_IMPL_NAME#__get_absolute_system_time_resolution(
        #MODULE_IMPL_NAME#__context *context,
        ECOA__duration *absolute_system_time_resolution) {

    ECOA__return_status return_status;
    return_status = ECOA__return_status_OK;
    #MODULE_IMPL_NAME#_container__get_absolute_system_time_resolution(context, absolute_system_time_resolution);

    return return_status;
}