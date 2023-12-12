/**
* @file ldp_VD_reader_manager.c
* @brief ECOA VD reader
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include <stdlib.h>
#include "ldp_VD.h"
#include "ECOA.h"
#include "ldp_status_error.h"
#include "ldp_structures.h"

void ldp_init_reader_mng(ldp_VD_reader_mng* reader_mng){
	if (reader_mng->repo_VD != NULL && reader_mng->repo_VD->mode == CONTROLLED){
		for (int i=0; i<reader_mng->num_copies; i++){
			reader_mng->VD_data_copies[i].state = FREE;
			memset(reader_mng->VD_data_copies[i].data, 0,reader_mng->repo_VD->data_size);
		}
	}else{
		reader_mng->VD_data_copies = NULL;
	}
	reader_mng->num_used_copies=0;
}

void ldp_create_reader_mng(ldp_VD_reader_mng* reader_mng, ldp_repository_VD* repo_VD, int num_copies){
	reader_mng->repo_VD = repo_VD;
	reader_mng->num_copies = num_copies;

	if (repo_VD != NULL && repo_VD->mode == CONTROLLED){
		reader_mng->VD_data_copies = calloc(reader_mng->num_copies,sizeof(ldp_VD_read_copy));
		for(int i=0; i<reader_mng->num_copies; i++){
			reader_mng->VD_data_copies[i].data = malloc(repo_VD->data_size);
		}
	}else{
		// nothing to do: data will be a pointer to the repository data
		reader_mng->VD_data_copies = NULL;
	}
}

void ldp_destroy_reader_mng(ldp_VD_reader_mng* reader_mng){
	if(reader_mng->repo_VD != NULL && reader_mng->repo_VD->mode == CONTROLLED){
		for(int i=0; i<reader_mng->num_copies; i++){
			free(reader_mng->VD_data_copies[i].data);
		}
	}
	free(reader_mng->VD_data_copies);
	reader_mng->num_copies=0;
}

static ldp_status_t get_read_access_NoControl(ldp_VD_reader_mng* reader_mng,
												ldp_VD_handle* handle){
	ldp_status_t ret;
	ldp_repository_VD* VD_repo = reader_mng->repo_VD;

	if(reader_mng->num_used_copies >= reader_mng->num_copies){
		ret = ECOA__return_status_RESOURCE_NOT_AVAILABLE;
		ldp_reset_handle(handle);
	}else{
		ret = ECOA__return_status_OK;
		reader_mng->num_used_copies++;
		handle->data = VD_repo->repository_ptr->data;
		handle->VD_copy_index = 0;
		handle->stamp = VD_repo->stamp;

	}

	return ret;
}

static ldp_status_t get_read_access_Control(ldp_VD_reader_mng* reader_mng,
											  ldp_VD_handle* handle){
	ldp_status_t ret;
	ldp_repository_VD* VD_repo = reader_mng->repo_VD;

	// find local copy
	int local_copy_index=-1;
	if (reader_mng->num_used_copies < reader_mng->num_copies){
		for(int i=0; i<reader_mng->num_copies; i++){
			if(reader_mng->VD_data_copies[i].state == FREE){
				local_copy_index = i;
				reader_mng->VD_data_copies[i].state = USED;
				reader_mng->num_used_copies++;
				break;
			}
		}
	}else{
		ldp_reset_handle(handle);
		return ECOA__return_status_RESOURCE_NOT_AVAILABLE;
	}

	// copy data
	ldp_VD_read_copy* copy_ptr = &reader_mng->VD_data_copies[local_copy_index];
	ret = ldp_copy_VD_data(VD_repo, copy_ptr->data, false);

	// fill handle
	handle->VD_copy_index = local_copy_index;
	if (ret == ECOA__return_status_DATA_NOT_INITIALIZED){
		ret = ECOA__return_status_NO_DATA;
		ldp_reset_handle(handle);
	}else{
		handle->data = copy_ptr->data;
		handle->stamp = VD_repo->stamp;
	}

	return ret;
}

ldp_status_t ldp_get_read_access(ldp_VD_reader_mng* reader_mng, ldp_VD_handle* handle){
	ldp_status_t ret = ECOA__return_status_OK;
	ldp_repository_VD* VD_repo = reader_mng->repo_VD;

	// check handle
	if (handle == NULL){
		return ECOA__return_status_INVALID_HANDLE;
	}

	// check reader_mng
	if(VD_repo != NULL && VD_repo->repository_ptr != NULL){
		if (VD_repo->mode == CONTROLLED){
			ret = get_read_access_Control(reader_mng, handle);
		}else{
			ret = get_read_access_NoControl(reader_mng, handle);
		}
	}else{
		// nothing to read
		ldp_reset_handle(handle);
		ret = ECOA__return_status_NO_DATA;
	}

	return ret;
}

ldp_status_t ldp_release_read_access(ldp_VD_reader_mng* reader_mng, ldp_VD_handle* handle){
	ldp_status_t ret;

	// check handle
	if (handle != NULL && handle->VD_copy_index != -1){
		ret = ECOA__return_status_OK;

		if (reader_mng->repo_VD->mode == CONTROLLED){
			reader_mng->VD_data_copies[handle->VD_copy_index].state = FREE;
		}else{
			// nothing to do
		}
		reader_mng->num_used_copies--;

		// reset handle;
		ldp_reset_handle(handle);
	}else{
		ret = ECOA__return_status_INVALID_HANDLE;
	}

	return ret;
}

