/**
* @file ldp_VD.h
* @brief ECOA Versioned Data
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifndef LDP_VD_H_
#define LDP_VD_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "apr.h"
#include "apr_thread_mutex.h"
#include <stdbool.h>
#include "ldp_status_error.h"
#include "ECOA.h"
#include "ldp_structures.h"
#include "ldp_request_response.h"

typedef struct ldp_module_context_t ldp_module_context; //!< define in ldp_structures.h
typedef struct ldp_PDomain_ctx_t ldp_PDomain_ctx;//!< define in ldp_structures.h

//! reader type of Versioned data repository
typedef enum ldp_VD_reader_nature{
    MODULE,        //!< Module inside the Protection Domain
    REPOSITORY_VD, //!< An other VD repository inside the Protection Domain
    LOCAL_SOCKET,  //!< A socket in the Platform (ie: VD repository in an other Protection Domain)
    EXTERN_SOCKET, //!< A socket connected with an other Platform
    UNKOWN
}ldp_VD_reader_nature;

//! Possible state of a VD copies
typedef enum ldp_VD_copies_state{
    FREE, //!< no reader and no writter
    USED  //!< is used by readers or/and writters
}ldp_VD_copies_state;

//! Option for the behaviour of a writter
typedef enum ldp_VD_written_mng_mode{
    WRITE_ONLY, //!< writer takes a written access that doesn't contain a copy of the data but inconsistant data
    READ_WRITE  //!< writer takes a written access that contains a copy of the last published data
}ldp_VD_written_mng_mode;

//! Option for the behavoiur of a VD repository
typedef enum ldp_VD_repository_mode{
    CONTROLLED,  //!< normal behaviour of VD: reader/writter can access VD safety
    UNCONTROLLED //!< the access to the data is concurrent. Only one copy of the data
}ldp_VD_repository_mode;

/**
 * Contains a copy of data for written access
 */
typedef struct ldp_VD_copy{
    unsigned char* data;//!< copy of data
    int data_size;     //!< size of data. use ?
    int num_readers;   //!< current number of readers that are fing a copy of this data
    ldp_VD_copies_state state;//!< indicate if this structure is used
    bool to_be_release;//!< indicate if this structure need to be released by the last reader
}ldp_VD_copy;

/**
 * Contains a copy of data for a read access
 */
typedef struct ldp_VD_read_copy{
    unsigned char* data;         //!< copy of the data
    ldp_VD_copies_state state; //!< indicate if this structure is used
    int data_size;               //!< size of data. use?
}ldp_VD_read_copy;

/**
 * handle information about a reader that need to be notifyied or update after a publication
 */
typedef struct ldp_VD_reader{
    ldp_VD_reader_nature nature; //!< nature of the reader
    void* reader_ptr;      //!< module context, socket or repository_VD
    uint32_t operation_id; //!< operation ID
    bool mod_op_activating;//!< activating operation. Only used for MODULE readers
    int mod_op_index;      //!< operation index. Only used for MODULE readers
} ldp_VD_reader;


typedef uint32_t (*serialize_data)(char* dest, char* src); //!< type of a function pointer to serialize data in a buffer

/**
 * Structure that handle a repository of a Versioned Data
 */
typedef struct ldp_repository_VD{
    ldp_VD_reader* readers;//!< array of readers to notify (modules, socket, other repository, ...)
    ldp_VD_copy* VD_copies;//!< array of possible copy for writters or for new publication
    int num_readers;         //!< number of readers in readers array
    int num_VD_copies;       //!< number of possible copy in VD_copies array
    int data_size;           //!< size of data
    int stamp;               //!< stamp of the last published copy. incremented at each publication
    ldp_VD_copy* repository_ptr;//!< pointer to the last published data in VD_copies array
    apr_thread_mutex_t* mutex; //!< mutex
    ldp_VD_repository_mode mode; //!< access mode of the repository (controlled/uncontrolled)

    serialize_data serial_data_fct; //!< function pointer to use to serialize data
}ldp_repository_VD;

/**
 * Module manager of a Versioned Data in read access
 */
typedef struct ldp_VD_reader_mng{
    // TODO: improve with a list ?
    ldp_VD_read_copy* VD_data_copies;//!< array of read access
    int num_copies;                    //!< size of read accesses array
    int num_used_copies;               //!< current number of used read access
    ldp_repository_VD* repo_VD;      //!< pointer to the VD repository
}ldp_VD_reader_mng;

/**
 * Module manager of Versioned Data in written access
 */
typedef struct ldp_VD_writter_mng{
    // TODO: improve with a list ?
    ldp_VD_copy** VD_copies_ptr;//!< array of pointer to written access in VD_repository
    int num_copies;               //!< size of written accesses array
    int num_used_copies;          //!< current number of used written access
    ldp_repository_VD* repo_VD; //!< pointer to the VD repository
    ldp_VD_written_mng_mode mode; //!< access mode of the VD (write_only/read_write))
}ldp_VD_writter_mng;

/**
 * redefinition of an ECOA handle structure.
 */
typedef struct ldp_VD_handle{
    unsigned char* data;//!< pointer to the local copy of the data
    uint32_t  stamp;    //!<counter of the last update of that version of the data
    // platform hool
    int VD_copy_index;  //!< [platform hook] index of the used copy in manager
}ldp_VD_handle;

/**
 * @brief      Create repository: set static members and allocate memory
 *
 * @param      repo           The VD repository to create
 * @param[in]  num_readers    The number of readers
 * @param[in]  num_VD_copies  The number of VD copies in written access
 * @param[in]  data_size      The data size
 * @param[in]  mode           access mode of the repository
 * @param      mp             APR memory pool
 */
void ldp_create_repository(ldp_repository_VD* repo, int num_readers, int num_VD_copies, int data_size, ldp_VD_repository_mode mode, apr_pool_t* mp);
/**
 * @brief      Create repository: set static members and allocate memory
 *
 * @param      writter_mng  The writter manager to create
 * @param      repo_VD      The pointer to the attached VD repository
 * @param[in]  num_copies   The number copies in written access
 * @param[in]  mode         Access mode of a written VD
 */
void ldp_create_writter_mng(ldp_VD_writter_mng* writter_mng, ldp_repository_VD* repo_VD, int num_copies, ldp_VD_written_mng_mode mode);
/** * @brief      Create repository: set static members and allocate memory
 *
 * @param      reader_mng  The reader manager to create
 * @param      repo_VD      The pointer to the attached VD repository
 * @param[in]  num_copies  The number copies in read access
 */
void ldp_create_reader_mng(ldp_VD_reader_mng* reader_mng, ldp_repository_VD* repo_VD, int num_copies);

/**
 * @brief      Initialize structure members with default values
 * @param      repo  The VD repository
 */
void ldp_init_repository(ldp_repository_VD* repo);
/**
 * @brief      Initialize structure members with default values
 * @param      writter_mng  The writter manager
 */
void ldp_init_writter_mng(ldp_VD_writter_mng* writter_mng);
/**
 * @brief      Initialize structure members with default values
 * @param      reader_mng  The reader manager
 */
void ldp_init_reader_mng(ldp_VD_reader_mng* reader_mng);


void ldp_destroy_repository(ldp_repository_VD* repo, apr_pool_t* mp);
void ldp_destroy_writter_mng(ldp_VD_writter_mng* writter_mng);
void ldp_destroy_reader_mng(ldp_VD_reader_mng* reader_mng);


ldp_status_t ldp_get_written_access(ldp_VD_writter_mng* writter_mng, ldp_VD_handle* handle);
ldp_status_t ldp_publish_written_access(ldp_module_context* ctx, ldp_VD_writter_mng* writter_mng, ldp_VD_handle* handle);
ldp_status_t ldp_cancel_written_access(ldp_VD_writter_mng* writter_mng, ldp_VD_handle* handle);

ldp_status_t ldp_get_read_access(ldp_VD_reader_mng* reader_mng, ldp_VD_handle* handle);
ldp_status_t ldp_release_read_access(ldp_VD_reader_mng* reader_mng, ldp_VD_handle* handle);

/**
 * @brief      update a repository. This function is used when a local repository writes in this repository after a publication
 *  - writting new data in a free VD copy
 *  - update repository_ptr
 *
 * @param      repo      The VD repository
 * @param      new_data  The new data
 *
 * @return     ECOA__return_status_RESOURCE_NOT_AVAILABLE or ECOA__return_status_OK
 */
ldp_status_t ldp_update_repository(ldp_repository_VD* repo, unsigned char* new_data);

/**
 * @brief      notify reader modules and publish data in reader repositories
 *
 * @param      PD_ctx  The protection domain context
 * @param      repo    The VD repository that have been updated
 *
 * @return     the number of notifyed readers
 */
int ldp_notify_local_readers(ldp_PDomain_ctx* PD_ctx, ldp_repository_VD* repo);

/**
 * @brief      send published data to reader sockets
 *
 * @param      ctx   The current module context
 * @param      repo  The VD repository
 */
void ldp_notifyed_socket_readers(ldp_module_context* ctx, ldp_repository_VD* repo);

/**
 * @brief      Reset handle by setting structure to default value
 *
 * @param      handle  The handle
 */
void ldp_reset_handle(ldp_VD_handle* handle);

/**
 * @brief      Gets a writter VD copy available in the repository VD.
 *             The copy is not initialized with the last published data.
 *
 * @param      repo  The VD repository
 *
 * @return     The written vd copy or NULL
 */
ldp_VD_copy* ldp_get_written_VD_copy(ldp_repository_VD* repo);

/**
 * @brief      Release a VD copy in the VD repository if there is no reading operation on it.
 *
 * @param      copy  The VD copy in the VD repository
 */
void ldp_release_written_VD_copy(ldp_VD_copy* copy);

/**
 * @brief      Copy the repository pointer (the last published data)
 *
 * @param      repo           The VD repository
 * @param      data_dest      The data destination
 * @param[in]  is_mutex_lock  Indicates if mutex need to be lock at the beginning
 *
 * @return     ECOA__return_status_DATA_NOT_INITIALIZED if no data has already been written or
 *             ECOA__return_status_OK
 */
ldp_status_t ldp_copy_VD_data(ldp_repository_VD* repo, unsigned char* data_dest, bool is_mutex_lock);

/**
 * @brief      change repository pointer to a new copy (after a publish operation).
 *             Free the old pointer or mark it "to_be_released".
 *
 * @param      repo     The VD repository
 * @param      new_ptr  The pointer of the new copy that is publishing/ It will be the new repository pointer
 */
void ldp_move_repository_ptr(ldp_repository_VD* repo, ldp_VD_copy* new_ptr);

/**
 * @brief      push data to every external readers (in an other Platform)
 *
 * @param      PD_ctx       The Protection Domain context
 * @param      repo         The VD repository
 * @param[in]  other_PF_ID  The other Platform ID that has pulled for VD update
 * @param[in]  VD_ID        The VD operation ID. (0XFFFFFFFF: push without restriction, other value: push only the VD with the same operation ID)
 *
 * @return     ECOA___TRUE if there is something to push, ECOA__FALSE if not (invalid VD_ID, no readers, ...)
 */
ECOA__boolean8 ldp_push_VD_ELI(ldp_PDomain_ctx* PD_ctx,
                                ldp_repository_VD* repo,
                                ECOA__uint32 other_PF_ID,
                                ECOA__uint32 VD_ID);

#ifdef __cplusplus
}
#endif

#endif /* LDP_VD_H_ */
