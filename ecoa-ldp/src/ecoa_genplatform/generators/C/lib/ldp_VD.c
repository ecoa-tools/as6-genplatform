/**
* @file ldp_VD.c
* @brief ECOA VD
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include <stdlib.h>
#include "ECOA.h"
#include "ldp_status_error.h"
#include "ldp_mod_container_util.h"
#include "ldp_structures.h"
#include "ldp_comp_util.h"
#include "ldp_multicast.h"
#include "ldp_ELI.h"
#include "ldp_ELI_udp.h"
#include "ldp_ELI_msg_management.h"

void ldp_create_repository(ldp_repository_VD* repo, int num_readers, int num_VD_copies,
								int data_size, ldp_VD_repository_mode mode, apr_pool_t* mp){
	// set repo structure
	repo->num_readers = num_readers;
	repo->num_VD_copies = num_VD_copies;
	repo->data_size = data_size;
	repo->mode = mode;

	// allocate memory
	repo->VD_copies = calloc(repo->num_VD_copies, sizeof(ldp_VD_copy));
	for (int i=0; i<repo->num_VD_copies;i++){
		repo->VD_copies[i].data = malloc(repo->data_size);
		repo->VD_copies[i].data_size= repo->data_size;
	}
	repo->readers = calloc(repo->num_readers, sizeof(ldp_VD_reader));
	for(int i=0; i<repo->num_readers; i++){
		repo->readers[i].nature = UNKOWN;
	}
	apr_thread_mutex_create( &repo->mutex,0,mp);
}

////////////////////////////////////////////////////////////////
void ldp_init_repository(ldp_repository_VD* repo){
	// allocate memory
	for(int i=0; i<repo->num_VD_copies;i++){
		repo->VD_copies[i].num_readers = 0;
		repo->VD_copies[i].state = FREE;
		repo->VD_copies[i].to_be_release=false;
		memset(repo->VD_copies[i].data, 0, repo->VD_copies[i].data_size);
	}

	// init structures
	repo->stamp = 0;

	if(repo->mode == CONTROLLED){
		repo->repository_ptr = NULL;
	}else{
		repo->repository_ptr = &repo->VD_copies[0]; // will never change
	}
}

////////////////////////////////////////////////////////////////
void ldp_destroy_repository(ldp_repository_VD* repo, apr_pool_t* mp){

	for (int i=0; i<repo->num_VD_copies;i++){
		free(repo->VD_copies[i].data);
	}
	free(repo->VD_copies);
	free(repo->readers);
	repo->num_VD_copies=0;
	apr_thread_mutex_destroy(repo->mutex);
    UNUSED(mp);
}

////////////////////////////////////////////////////////////////

void ldp_reset_handle(ldp_VD_handle* handle){
	handle->data = NULL;
	handle->stamp = 0;
	handle->VD_copy_index = -1;
}


/**
 * @brief      serialize VD data in a buffer
 *
 * @param      repo         The VD repository
 * @param      dest_buffer  The buffer to write
 * @param      data_size    The written bytes number
 *
 * @return     ECOA__return_status_DATA_NOT_INITIALIZED or ECOA__return_status_OK
 */
static ldp_status_t ldp_serialize_VD_data(ldp_repository_VD* repo, char* dest_buffer, uint64_t* data_size){
	// find data to copy
	apr_thread_mutex_lock(repo->mutex);
	ldp_VD_copy* copy_ptr = repo->repository_ptr;
	if ( copy_ptr == NULL){
		// not initialize
		*data_size = 0;
		apr_thread_mutex_unlock(repo->mutex);
		return ECOA__return_status_DATA_NOT_INITIALIZED;
	}
	copy_ptr->num_readers++;
	apr_thread_mutex_unlock(repo->mutex);

	// make copy
	*data_size = (repo->serial_data_fct)(dest_buffer,(char*) copy_ptr->data);

	// release data if necessary
	apr_thread_mutex_lock(repo->mutex);
	ldp_release_written_VD_copy(copy_ptr);
	apr_thread_mutex_unlock(repo->mutex);

	return ECOA__return_status_OK;

}

ldp_status_t ldp_copy_VD_data(ldp_repository_VD* repo, unsigned char* data_dest, bool is_mutex_lock){

	// find data to copy
	if(!is_mutex_lock){
		apr_thread_mutex_lock(repo->mutex);
	}
	ldp_VD_copy* copy_ptr = repo->repository_ptr;
	if ( copy_ptr == NULL){
		// not initialize
		apr_thread_mutex_unlock(repo->mutex);
		return ECOA__return_status_DATA_NOT_INITIALIZED;
	}
	copy_ptr->num_readers++;
	apr_thread_mutex_unlock(repo->mutex);

	// make copy
	memcpy(data_dest, copy_ptr->data, repo->data_size);

	// release data if necessary
	apr_thread_mutex_lock(repo->mutex);
	ldp_release_written_VD_copy(copy_ptr);
	apr_thread_mutex_unlock(repo->mutex);

	return ECOA__return_status_OK;
}

ldp_VD_copy* ldp_get_written_VD_copy(ldp_repository_VD* repo){
	// NOT THREAD SAFE
	for(int i=0; i<repo->num_VD_copies; i++){
		if (repo->VD_copies[i].state == FREE){
			repo->VD_copies[i].state = USED;
			return &repo->VD_copies[i];
		}
	}
	return NULL;
}

void ldp_release_written_VD_copy(ldp_VD_copy* copy){
	// NOT THREAD SAFE
	// release copy if necessary
	if ((copy->to_be_release) && (copy->num_readers == 1)){
		copy->state = FREE;
		copy->to_be_release = false;
		copy->num_readers = 0;
	}else{
		copy->num_readers--;
	}
}


void ldp_move_repository_ptr(ldp_repository_VD* repo, ldp_VD_copy* new_ptr){
	// NOT THREAD SAFE
	if (repo->repository_ptr != NULL){
		// Not first write : old copy has to be released
		if(repo->repository_ptr->num_readers == 0){
			// no readers. free old copy
			repo->repository_ptr->state = FREE;
		}else{
			// indicate to readers that this old copy has to be released
			repo->repository_ptr->to_be_release = true;
		}
	}
	// update repo
	repo->repository_ptr = new_ptr;
	repo->stamp++;
}


ldp_status_t ldp_update_repository(ldp_repository_VD* repo, unsigned char* new_data){
	apr_thread_mutex_lock(repo->mutex);
	ldp_VD_copy* copy_ptr = ldp_get_written_VD_copy(repo);
	apr_thread_mutex_unlock(repo->mutex);

	if(copy_ptr == NULL){
		return ECOA__return_status_RESOURCE_NOT_AVAILABLE;
	}
	memcpy(copy_ptr->data, new_data, repo->data_size);

	apr_thread_mutex_lock(repo->mutex);
	ldp_move_repository_ptr(repo, copy_ptr);
	apr_thread_mutex_unlock(repo->mutex);

	return ECOA__return_status_OK;
}


int ldp_notify_local_readers(ldp_PDomain_ctx* PD_ctx, ldp_repository_VD* repo){
	int notified_readers = 0;
	for(int i=0; i< repo->num_readers; i++){
		if(repo->readers[i].nature == MODULE){
			ldp_module_context* mod_ctx = repo->readers[i].reader_ptr;
			// transfers message to module FIFO
			ldp_comp_notify_mod_VD(PD_ctx,
									mod_ctx,
									repo->readers[i].mod_op_index,
									repo->readers[i].mod_op_activating,
									repo->readers[i].operation_id);
			notified_readers++;
		}else if(repo->readers[i].nature == REPOSITORY_VD){
			ldp_repository_VD* reader_repo = repo->readers[i].reader_ptr;
			if(ldp_update_repository(reader_repo, repo->repository_ptr->data) == ECOA__return_status_OK){
				ldp_notify_local_readers(PD_ctx, reader_repo);
				notified_readers++;
			}else{
				//TODO print error
			}
		}else{
			//nothing to do
		}
	}
	return notified_readers;
}

/**
 * @brief      write serialized data of VD in msg_buffer
 *
 * @param      PD_ctx          The protection domain context
 * @param      msg_buffer      The buffer to write
 * @param      repo            The VD repository
 * @param      data_size       The size of serialized data
 *
 * @return     LDP_ERROR or LDP_SUCCESS
 */
static ldp_status_t ldp_VD_create_serial_msg(ldp_PDomain_ctx* PD_ctx,
											char* msg_buffer,
											ldp_repository_VD* repo,
											uint64_t* data_size){
	if (repo->repository_ptr != NULL){
		if (repo->serial_data_fct == NULL){
			ldp_log_PF_log_var(ECOA_LOG_ERROR_PF, "ERROR", PD_ctx->logger_PF,
				"[%s] Impossible to serialize a VD. function pointer is NULL", PD_ctx->name);

			return LDP_ERROR;
		}
		// serialisation
		ldp_serialize_VD_data(repo,
								msg_buffer,
								data_size);

	}else{
		// VD not initialized : send msg with size 0
		*data_size = 0;
	}
	return LDP_SUCCESS;
}


void ldp_notifyed_socket_readers(ldp_module_context* ctx, ldp_repository_VD* repo){
	uint64_t external_msg_size = 0;

	// TODO : improvement: copy data only one time

	// send IP messages
	for(int i=0; i< repo->num_readers; i++){
		switch(repo->readers[i].nature){
		case LOCAL_SOCKET:
			// write message
			ldp_copy_VD_data(repo, (unsigned char*) &ctx->msg_buffer[LDP_HEADER_TCP_SIZE], false);
			ldp_written_IP_header(ctx->msg_buffer, repo->data_size, 0);
			ldp_written_IP_op_ID(ctx->msg_buffer, repo->readers[i].operation_id);

			// send message
			ldp_IP_write((ldp_interface_ctx*) repo->readers[i].reader_ptr,ctx->msg_buffer,
							LDP_HEADER_TCP_SIZE + repo->data_size, ctx->network_write_data);
			break;

		case EXTERN_SOCKET:
			if (ldp_VD_create_serial_msg(ctx->component_ctx,
											&ctx->msg_buffer[LDP_ELI_HEADER_SIZE],
											repo, &external_msg_size) == LDP_ERROR){
				break;
			}else{
				ldp_interface_ctx* socket = repo->readers[i].reader_ptr;

				// write ELI header
				ldp_ELI_header ELI_header = (ldp_ELI_header){LDP_ELI_VERSION,
																LDP_ELI_SERVICE_OP,
																ctx->component_ctx->ELI_platform_ID,
																repo->readers[i].operation_id,
																external_msg_size, 0};
				ECOA__uint32 written_bytes;
				ldp_write_ELI_header(&ELI_header, (ECOA__uint8*) ctx->msg_buffer, 0, &written_bytes);

				// message UDP
				ldp_sending_fct_ctx fct_ctx = {&socket->inter.mcast, ctx->logger_PF};
				ECOA__uint16 channel_counter = 0; // TODO: which counter using ?
				ldp_ELI_udp_msg_fragment_and_send(&fct_ctx, ldp_ELI_UDP_sending_fct,
													(unsigned char*)ctx->msg_buffer,
													external_msg_size + LDP_ELI_HEADER_SIZE,
													socket->inter.mcast.UDP_current_PF_ID,
													ctx->mod_id,
													&channel_counter);
			}
			break;

		case MODULE: // already done
		case REPOSITORY_VD: // already done
		case UNKOWN:
		default:
			break;
		}
	}
}

ECOA__boolean8 ldp_push_VD_ELI(ldp_PDomain_ctx* PD_ctx,
								ldp_repository_VD* repo,
								ECOA__uint32 other_PF_ID,
								ECOA__uint32 VD_ID){

	int retval;
	bool msg_buffer_written = false;
	uint64_t data_size = 0;
	uint64_t external_msg_size = 0;
    UNUSED(other_PF_ID);

	// find external readers : readers with the right operation ID or the first external socket reader
	ECOA__boolean8 push_something = ECOA__FALSE;
	for(int i=0; i<repo->num_readers; i++){
		if( (repo->readers[i].nature == EXTERN_SOCKET) &&
			((VD_ID == 0XFFFFFFFFU) || (VD_ID == repo->readers[i].operation_id)) ){
			push_something = ECOA__TRUE;

			// publish data
			ldp_interface_ctx* reader_inter = (ldp_interface_ctx*) repo->readers[i].reader_ptr;

			// write data in msg_buffer if it has not been done before
			if (!msg_buffer_written){
				// data must be written
				retval = ldp_VD_create_serial_msg(PD_ctx,
													&PD_ctx->msg_buffer[LDP_ELI_HEADER_SIZE],
													repo, &data_size);
				if (retval != LDP_SUCCESS){
					// error during data written
					continue;
				}
				msg_buffer_written = true;
			}
			external_msg_size = data_size;

			// write ELI header
			ECOA__uint32 written_bytes;
			ldp_ELI_header ELI_header = (ldp_ELI_header){LDP_ELI_VERSION,
									LDP_ELI_SERVICE_OP,
									PD_ctx->ELI_platform_ID,
									repo->readers[i].operation_id,
									data_size, 0};
			ldp_write_ELI_header(&ELI_header, (ECOA__uint8*) PD_ctx->msg_buffer, 0, &written_bytes);
			external_msg_size += LDP_ELI_HEADER_SIZE;

			// send UDP messages
			ldp_sending_fct_ctx fct_ctx = {&reader_inter->inter.mcast, PD_ctx->logger_PF};
			ECOA__uint16 channel_counter = 0; // TODO: which counter using ?
			ldp_ELI_udp_msg_fragment_and_send(&fct_ctx, ldp_ELI_UDP_sending_fct,
												(unsigned char*)PD_ctx->msg_buffer,
												external_msg_size,
												reader_inter->inter.mcast.UDP_current_PF_ID,
												0, /* TODO : use a protection domain ID ?*/
												&channel_counter);

			if (retval != LDP_ERROR){
            	ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", PD_ctx->logger_PF,
            							"pull VD with operation ID %i", repo->readers[i].operation_id);
			}
		}
	}

	return push_something;
}
