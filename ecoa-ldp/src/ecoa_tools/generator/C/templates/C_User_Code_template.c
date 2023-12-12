static ECOA__log error_log = {
	sizeof("Error in log_warning")+1,
	"Error in log_warning"
};

void #PREFIXE#_#MODULE_IMPL_NAME#__concat(#MODULE_IMPL_NAME#__context *context,
		ECOA__log *log, char *str) {
	char *module_name = "#MODULE_IMPL_NAME#: ";
	int module_name_length;
        ECOA__error_code error_code = 0;

	module_name_length = strnlen(module_name, ECOA__LOG_MAXSIZE);

#if defined(__STDC_LIB_EXT1__)
	errno_t result;

	result = strncpy_s((char *)log->data, ECOA__LOG_MAXSIZE, module_name, ECOA__LOG_MAXSIZE - 1);
	if (result != 0) {
		#MODULE_IMPL_NAME#_container__raise_error(context, error_log,error_code);
	}

	result = strncpy_s(((char *)log->data) + module_name_length, ECOA__LOG_MAXSIZE - module_name_length, str, ECOA__LOG_MAXSIZE - module_name_length - 1);
	if (result != 0) {
		#MODULE_IMPL_NAME#_container__raise_error(context, error_log,error_code);
	}
#else
	char *returned_string;

	returned_string = strncpy((char *) log->data, module_name,
			ECOA__LOG_MAXSIZE);
	if (returned_string != (char *) log->data) {
		#MODULE_IMPL_NAME#_container__raise_error(context, error_log,error_code);
	}

	returned_string = strncpy(((char *) log->data) + module_name_length, str,
			ECOA__LOG_MAXSIZE - module_name_length);
	if (returned_string != ((char *) log->data) + module_name_length) {
		#MODULE_IMPL_NAME#_container__raise_error(context, error_log,error_code);
	}
#endif

	log->current_size = strnlen((char *) log->data, ECOA__LOG_MAXSIZE);

}
