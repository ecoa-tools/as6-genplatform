/**
* @file ldp_pinfo.h
* @brief ECOA pinfo functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifdef __cplusplus
extern "C" {
#endif

#ifndef _LDP_PINFO_H
#define _LDP_PINFO_H
#include <stdio.h>
#include "ECOA.h"
#include "ldp_log_platform.h"

//! structure for one pinfo file
typedef struct ldp_pinfo_struct{
	char* filename;//!< file name. relative or absolute path
	FILE* fp; //!< file stream
}ldp_pinfo_struct;

//! structure for pinfo files manager for a module
typedef struct ldp_pinfo_manager{
	int pinfo_num; //!< number if pinfo file
	ldp_pinfo_struct* pinfo_array; //!< array of pinfo_strucut
}ldp_pinfo_manager;

/**
 * @brief      Initialize ldp_pinfo_manager.(open files)
 *
 * @param      pinfo_mg  The pinfo manager
 * @param      logger    The logger
 */
void ldp_init_pinfo_manager(ldp_pinfo_manager* pinfo_mg, ldp_logger_platform* logger);

/**
 * @brief      Destroye ldp_Pinfo_manager: close files and clean memory in pinfo_array
 *
 * @param      pinfo_mg  The pinfo manager
 */
void ldp_destroy_pinfo_manager(ldp_pinfo_manager* pinfo_mg);

/**
 * @brief      pinfo read function
 *
 * @param      ldp_pinfo_struct  The ldp pinfo structure
 * @param      mem_addr            The memory address to write
 * @param[in]  in_size             number of byte to read
 * @param      out_size            number of read byte
 *
 * @return     ECOA__return_status_RESOURCE_NOT_AVAILABLE, ECOA__return_status_INVALID_PARAMETER, ECOA__return_status_OK
 */
ECOA__return_status ldp_pinfo_read(ldp_pinfo_struct* ldp_pinfo_struct, ECOA__byte* mem_addr, ECOA__uint32 in_size, ECOA__uint32* out_size);

/**
 * @brief      pinfo seak function
 *
 * @param      ldp_pinfo_struct  The ldp pinfo structure
 * @param[in]  byte_to_add         The byte to add
 * @param      new_position        The new position
 * @param[in]  origin              The origin flag
 *
 * @return     ECOA__return_status_INVALID_PARAMETER, ECOA__return_status_OK
 */
ECOA__return_status ldp_pinfo_seek(ldp_pinfo_struct* ldp_pinfo_struct, ECOA__int32 byte_to_add, ECOA__uint32* new_position, ECOA__seek_whence_type origin);


#endif /* _LDP_PINFO_H */
#ifdef __cplusplus
}
#endif
