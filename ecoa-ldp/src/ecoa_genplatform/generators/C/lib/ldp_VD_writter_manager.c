/**
* @file ldp_VD_writter_manager.c
* @brief ECOA VD writer
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

void ldp_init_writter_mng(ldp_VD_writter_mng* writter_mng){
	if (writter_mng->repo_VD != NULL && writter_mng->repo_VD->mode == CONTROLLED){
		for (int i=0; i<writter_mng->num_copies; i++){
			writter_mng->VD_copies_ptr[i] = NULL;
		}
	}else{
		writter_mng->VD_copies_ptr = NULL;
	}
	writter_mng->num_used_copies=0;
}

void ldp_create_writter_mng(ldp_VD_writter_mng* writter_mng, ldp_repository_VD* repo_VD,
								 int num_copies, ldp_VD_written_mng_mode mode){
	writter_mng->repo_VD = repo_VD;
	writter_mng->num_copies = num_copies;
	if (repo_VD != NULL && repo_VD->mode == CONTROLLED){
		writter_mng->VD_copies_ptr = calloc(writter_mng->num_copies, sizeof(ldp_VD_copy*));
	}
	writter_mng->mode = mode;
}
void ldp_destroy_writter_mng(ldp_VD_writter_mng* writter_mng){
	free(writter_mng->VD_copies_ptr);
	writter_mng->num_copies=0;
}

/**
 * @brief      Find a free written access in writter manager
 *
 * @param      writter_mng  The writter VD manager
 *
 * @return     the index of the free access
 */
static int find_written_access_index_controlled(ldp_VD_writter_mng* writter_mng){
	int VD_copy_ptr_index=-1;
	// find access
	if (writter_mng->num_used_copies < writter_mng->num_copies){
		for (int i=0; i<writter_mng->num_copies; i++){
			if(writter_mng->VD_copies_ptr[i] == NULL){
				VD_copy_ptr_index=i;
				writter_mng->num_used_copies++;
				break;
			}
		}
	}
	return VD_copy_ptr_index;
}

/**
 * @brief      send notification message to local readers and send published data to socket-readers
 *
 * @param      ctx   The module context
 * @param      repo  The VD repository
 */
static void notify_readers(ldp_module_context* ctx,ldp_repository_VD* repo){
	if (repo->num_readers == 0 || ctx == NULL) {
		return;
    }

	int notified_readers = ldp_notify_local_readers(ctx->component_ctx, repo);
	if(notified_readers < repo->num_readers){
		// readers on sockets should be notifyed
		ldp_notifyed_socket_readers(ctx, repo);
	}
}

/**
 * @brief      Release a written access: release copy in VD repository and reset handle
 *
 * @param      writter_mng  The writter VD manager
 * @param      handle       The handle containing the pointer to the copy to release
 */
static void release_written_access(ldp_VD_writter_mng* writter_mng, ldp_VD_handle* handle){
	if(writter_mng->repo_VD->mode == CONTROLLED){
		writter_mng->VD_copies_ptr[handle->VD_copy_index] = NULL;
	}
	writter_mng->num_used_copies--;

	ldp_reset_handle(handle);
}

ldp_status_t ldp_get_written_access(ldp_VD_writter_mng* writter_mng, ldp_VD_handle* handle){
	ldp_status_t ret = ECOA__return_status_OK;
	// check handle
	if (handle == NULL){
		return ECOA__return_status_INVALID_HANDLE;
	}

	ldp_repository_VD* VD_repo = writter_mng->repo_VD;

	if (VD_repo->mode == CONTROLLED){
		// find access
		int VD_copy_ptr_index = find_written_access_index_controlled(writter_mng);
		if (VD_copy_ptr_index == -1){
			return ECOA__return_status_RESOURCE_NOT_AVAILABLE;
		}

		//copy data
		apr_thread_mutex_lock(VD_repo->mutex);
		ldp_VD_copy* copy_ptr = ldp_get_written_VD_copy(VD_repo);

		if (copy_ptr == NULL){
			// no written_copy available in the repository.
			// due to too many written_copy in "to_be_released" state
			// need to wait some readers to finish copying operation
			apr_thread_mutex_unlock(VD_repo->mutex);
			ret = ECOA__return_status_RESOURCE_NOT_AVAILABLE;
			// reset
			writter_mng->VD_copies_ptr[VD_copy_ptr_index] = NULL;
			writter_mng->num_used_copies--;
			ldp_reset_handle(handle);
		}else{
			// make copy only in read-write mode:
			if(writter_mng->mode == READ_WRITE){
				ret = ldp_copy_VD_data(VD_repo, copy_ptr->data, true);
			}else{
				// WRITE_ONLY mode
				if(VD_repo->repository_ptr == NULL){
					ret = ECOA__return_status_DATA_NOT_INITIALIZED;
				}else{
					ret = ECOA__return_status_OK;
				}
				apr_thread_mutex_unlock(VD_repo->mutex);
			}

			// fill handle
			handle->VD_copy_index = VD_copy_ptr_index;
			handle->stamp = VD_repo->stamp;
			handle->data = copy_ptr->data;
			writter_mng->VD_copies_ptr[VD_copy_ptr_index]=copy_ptr;
		}
	}else{
		// Not controlled
		if (writter_mng->num_used_copies < writter_mng->num_copies){
			// fill handle
			handle->VD_copy_index = 0;
			handle->stamp = VD_repo->stamp;
			handle->data = VD_repo->repository_ptr->data;
			writter_mng->num_used_copies++;
		}else{
			ret = ECOA__return_status_RESOURCE_NOT_AVAILABLE;
			ldp_reset_handle(handle);
		}
	}

	return ret;
}


ldp_status_t ldp_publish_written_access(ldp_module_context* ctx, ldp_VD_writter_mng* writter_mng, ldp_VD_handle* handle){
	ldp_status_t ret = ECOA__return_status_OK;
	// check handle
	if (handle == NULL || handle->VD_copy_index == -1){
		return ECOA__return_status_INVALID_HANDLE;
	}

	ldp_repository_VD* VD_repo = writter_mng->repo_VD;

	if(VD_repo->mode == CONTROLLED){
		//controlled mode
		ldp_VD_copy* new_VD_ptr = writter_mng->VD_copies_ptr[handle->VD_copy_index];
		apr_thread_mutex_lock(VD_repo->mutex);
		ldp_move_repository_ptr(VD_repo, new_VD_ptr);

		// add a reader to make data available during notifying
		// writter could be considered as a reader during notifying operation.
		// Is decremented by 'ldp_release_written_VD_copy'
		new_VD_ptr->num_readers++;
		apr_thread_mutex_unlock(VD_repo->mutex);

		// notify readers
		notify_readers(ctx, VD_repo);

		apr_thread_mutex_lock(VD_repo->mutex);
		ldp_release_written_VD_copy(new_VD_ptr); // decremented num_readers
		apr_thread_mutex_unlock(VD_repo->mutex);
	}else{
		// Not controlled mode
		VD_repo->stamp++;

		// notify readers
		notify_readers(ctx, VD_repo);
	}
	// Release written access
	release_written_access(writter_mng, handle);

	return ret;

}

ldp_status_t ldp_cancel_written_access(ldp_VD_writter_mng* writter_mng, ldp_VD_handle* handle){
	ldp_status_t ret = ECOA__return_status_OK;

	// check handle
	if (handle != NULL && handle->VD_copy_index != -1){
		if(writter_mng->repo_VD->mode == CONTROLLED){
			// Controlled mode : release VD_copy in repository
			ldp_VD_copy* copy = writter_mng->VD_copies_ptr[handle->VD_copy_index];
			copy->state = FREE;
		}else{
			// not controlled mode : nothing to do
		}

		// Release written access
		release_written_access(writter_mng, handle);

	}else{
		ret = ECOA__return_status_INVALID_HANDLE;
	}

	return ret;
}
