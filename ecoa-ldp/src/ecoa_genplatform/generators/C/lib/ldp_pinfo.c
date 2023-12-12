/**
* @file ldp_pinfo.c
* @brief ECOA pinfo functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include "ldp_pinfo.h"
#include <stdio.h>
#include <stdlib.h>
#include "ECOA.h"
#include <stdbool.h>
#include "ldp_log_platform.h"

static bool is_out_of_file(FILE* fp){
	size_t current_index = ftell(fp);
	fseek(fp, 0, SEEK_END);
	size_t end_index = ftell(fp);

	bool res;
	if (current_index > end_index){
		res = true;
	}else{
		res = false;
	}
	//return to original index
	fseek(fp, current_index, SEEK_SET);
	return res;
}

static void init_pinfo_struct(ldp_pinfo_struct* pinfo_struct, ldp_logger_platform* logger){
	// open file
	FILE* fp = fopen(pinfo_struct->filename, "rb");
	if (fp == NULL){
		ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", logger,"ERROR : file %s doenot exist", pinfo_struct->filename);
	}
	pinfo_struct->fp = fp;
}

void ldp_init_pinfo_manager(ldp_pinfo_manager* pinfo_mg, ldp_logger_platform* logger){
	// init all streams
	for(int i=0; i< pinfo_mg->pinfo_num; i++){
		init_pinfo_struct(&pinfo_mg->pinfo_array[i], logger);
	}
}

void ldp_destroy_pinfo_manager(ldp_pinfo_manager* pinfo_mg){
	// close all streams
	for(int i=0; i< pinfo_mg->pinfo_num; i++){
		if(pinfo_mg->pinfo_array[i].fp != NULL){
			fclose(pinfo_mg->pinfo_array[i].fp);
			pinfo_mg->pinfo_array[i].fp = NULL;
		}
	}
	//free array
	free(pinfo_mg->pinfo_array);
}


///// PINFO API
ECOA__return_status ldp_pinfo_read(ldp_pinfo_struct* pinfo_struct, ECOA__byte* mem_addr, ECOA__uint32 in_size, ECOA__uint32* out_size){
	ECOA__return_status retval = ECOA__return_status_OK;
	ECOA__uint32 out_size_tmp = 0;

	if (mem_addr == NULL){
		retval = ECOA__return_status_INVALID_PARAMETER;
	}else{
		if (pinfo_struct->fp != NULL){
			out_size_tmp = fread(mem_addr, sizeof(unsigned char), in_size, pinfo_struct->fp);
		}else{
			retval = ECOA__return_status_RESOURCE_NOT_AVAILABLE;
		}
	}

	if (out_size != NULL){
		*out_size = out_size_tmp;
	}

	return retval;
}

ECOA__return_status ldp_pinfo_seek(ldp_pinfo_struct* pinfo_struct, ECOA__int32 byte_to_add, ECOA__uint32* new_position, ECOA__seek_whence_type origin){
	ECOA__return_status retval = ECOA__return_status_OK;

	// find the right flag
	int f_origin;
	switch (origin){
	case ECOA__seek_whence_type_SEEK_SET:
		f_origin = SEEK_SET;
		break;
	case ECOA__seek_whence_type_SEEK_CUR:
		f_origin = SEEK_CUR;
		break;
	case ECOA__seek_whence_type_SEEK_END:
		f_origin = SEEK_END;
		break;
	default:
		return ECOA__return_status_INVALID_PARAMETER;
	}


	if (pinfo_struct->fp == NULL){
		retval = ECOA__return_status_RESOURCE_NOT_AVAILABLE;
		*new_position = 0;
	}else{
		// save current file index:
		int tmp_pindex = ftell(pinfo_struct->fp);

		if(fseek(pinfo_struct->fp, byte_to_add, f_origin) == 0){
			//check if in file
			if (is_out_of_file(pinfo_struct->fp) == true){
				retval = ECOA__return_status_INVALID_PARAMETER;
			}
		}else{
			// error case, ie: negative index
			retval = ECOA__return_status_INVALID_PARAMETER;
		}

		if(retval == ECOA__return_status_INVALID_PARAMETER){
			// error : return to original index
			fseek(pinfo_struct->fp, tmp_pindex, SEEK_SET);
		}
		*new_position = ftell(pinfo_struct->fp);
	}

	return retval;

}
