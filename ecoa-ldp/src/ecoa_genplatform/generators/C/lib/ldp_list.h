/**
* @file ldp_list.h
* @brief ECOA ldp list
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifdef __cplusplus
extern "C" {
#endif

#ifndef _LDP_LIST_H
#define _LDP_LIST_H
#include "ldp_status_error.h"

//! element of a list
struct ldp_node_t{
	void* data; //!< pointer to element data
	struct ldp_node_t* next; //!< next element in list
	struct ldp_node_t* prev; //!< previous element in list
};

//! list node structure
typedef struct ldp_node_t ldp_node;

//! structure for list
typedef struct ldp_list{
	int max_size; //!< maximum elements in list
	int current_size; //!< current number of elements in list
	int data_size; //!< size of data in nodes

	ldp_node* node_array; //!< array of list used or unused element. This array is used to keep access to all list element
	ldp_node* unused_list_tail; //!< point to the tail of unused element list
	ldp_node* used_list_tail;//!< point to the tail of used element list
}ldp_list;

/**
 * @brief      Initialize the list.
 * Allocate memory, initialize pointers to create a double linked list of unused elements
 *
 * @param      list       list structure
 * @param[in]  size       number of element in the list
 * @param[in]  data_size  size of an element
 */
void ldp_init_list(ldp_list* list, int size, int data_size);

/**
 * @brief      Find the first element unused in the list.
 *      - remove first element of unused list
 *      - add it in the tail of used list
 *
 * @param      list  The list
 *
 * @return the found element
 */
ldp_node* ldp_add_last(ldp_list* list);

/**
 * @brief     	Remove the first element of used_list
 *
 * @param      list      The list structurs
 * @param      old_data  The pointer that contains the return data of this element
 *
 * @return     LDP_SUCCESS or LDP_ERROR
 */
ldp_status_t ldp_remove_first_node(ldp_list* list, void** old_data);

/**
 * @brief      Remove the old_node from the used_list and add it in the unused list
 *
 * @param      list      The list
 * @param      old_node  The old node to remove
 *
 * @return     LDP_ERROR in case of failure (list empty) or LDP_SUCCESS
 */
ldp_status_t ldp_remove_node(ldp_list* list, ldp_node* old_node);

/**
 * @brief      Clean list: mode all nodes from used_list to unsued list
 *
 * @param      list  The list
 */
void ldp_clean_list(ldp_list* list);

/**
 * @brief      destroy list and free memory
 *
 * @param      list  The list
 */
void ldp_destroy_list(ldp_list* list);
#endif /* _LDP_LIST_H */
#ifdef __cplusplus
}
#endif
