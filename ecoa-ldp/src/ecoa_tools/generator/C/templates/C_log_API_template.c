
/*********** Log related API *************/
void #PREFIXE#_#MODULE_IMPL_NAME#__log_trace(#MODULE_IMPL_NAME#__context *context, char *str)
{
    ECOA__log log;
    #PREFIXE#_#MODULE_IMPL_NAME#__concat(context, &log, str);
    #MODULE_IMPL_NAME#_container__log_trace(context, log);
}

void #PREFIXE#_#MODULE_IMPL_NAME#__log_debug(#MODULE_IMPL_NAME#__context *context, char *str)
{
    ECOA__log log;
    #PREFIXE#_#MODULE_IMPL_NAME#__concat(context, &log, str);
    #MODULE_IMPL_NAME#_container__log_debug(context, log);
}

void #PREFIXE#_#MODULE_IMPL_NAME#__log_info(#MODULE_IMPL_NAME#__context *context, char *str)
{
    ECOA__log log;
    #PREFIXE#_#MODULE_IMPL_NAME#__concat(context, &log, str);
    #MODULE_IMPL_NAME#_container__log_info(context, log);
}

void #PREFIXE#_#MODULE_IMPL_NAME#__log_warning(#MODULE_IMPL_NAME#__context *context, char *str)
{
    ECOA__log log;
    #PREFIXE#_#MODULE_IMPL_NAME#__concat(context, &log, str);
    #MODULE_IMPL_NAME#_container__log_warning(context, log);
}

void #PREFIXE#_#MODULE_IMPL_NAME#__raise_error(#MODULE_IMPL_NAME#__context* context, char *str, const ECOA__error_code error_code)
{
    ECOA__log log;
    #PREFIXE#_#MODULE_IMPL_NAME#__concat(context, &log, str);
    #MODULE_IMPL_NAME#_container__raise_error(context, log , error_code);
}

void #PREFIXE#_#MODULE_IMPL_NAME#__raise_fatal_error(#MODULE_IMPL_NAME#__context* context, char *str, const ECOA__error_code error_code)
{
    ECOA__log log;
    #PREFIXE#_#MODULE_IMPL_NAME#__concat(context, &log, str);
    #MODULE_IMPL_NAME#_container__raise_fatal_error(context, log, error_code);
}
