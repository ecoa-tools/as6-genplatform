/**
* @file ldp_list.c
* @brief ECOA ldp list
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include "ldp_list.h"
#include <stdlib.h>
#include <assert.h>
#include "ldp_status_error.h"


static void ldp_alloc_node_data(ldp_list* list, int data_size){
	for(int i=0; i<list->max_size;i++){
		list->node_array[i].data = calloc(1,data_size);
	}
}

void ldp_init_list(ldp_list* list, int size, int data_size){
    int new_size = size;
	if(size<=1){
		new_size = 2;
    }

	list->max_size = new_size;
	list->current_size =0;
	list->data_size = data_size;

	list->used_list_tail = NULL;

	list->node_array = calloc(new_size, sizeof(ldp_node));

	list->node_array[0].prev = NULL;
	list->node_array[0].next = &list->node_array[1];
	list->node_array[0].data = NULL;
	for(int i=1; i<new_size-1;i++){
		list->node_array[i].data = NULL;
		list->node_array[i].prev = &list->node_array[i-1];
		list->node_array[i].next = &list->node_array[i+1];
	}
	list->node_array[new_size-1].prev = &list->node_array[new_size-2];
	list->node_array[new_size-1].next = NULL;
	list->node_array[new_size-1].data = NULL;

	list->unused_list_tail = &list->node_array[new_size-1];

	// alloc data size only if necessary
	if (data_size > 0){
		ldp_alloc_node_data(list, data_size);
	}
}


ldp_node* ldp_add_last(ldp_list* list){
	if(list->current_size == list->max_size || list->unused_list_tail == NULL){
		return NULL;
    }

	list->current_size++;

	ldp_node* new_node = list->unused_list_tail;

	// remove one node from unused_list
	list->unused_list_tail= list->unused_list_tail->prev;
	if(list->unused_list_tail != NULL){
		list->unused_list_tail->next = NULL;
    }

	// add new_node in tail
	if (list->used_list_tail != NULL){
		list->used_list_tail->next = new_node;
    }

	new_node->prev = list->used_list_tail;
	new_node->next = NULL;
	list->used_list_tail = new_node;

	return new_node;
}


ldp_status_t ldp_remove_first_node(ldp_list* list, void** data){
	if(list->current_size == 0 || list->used_list_tail == NULL){
		return LDP_ERROR;
    }

	ldp_node* current_node = list->used_list_tail;
	while(current_node->prev != NULL){
		current_node = current_node->prev;
	}
	*data = current_node->data;

	// remove node
	ldp_remove_node(list, current_node);

	return LDP_SUCCESS;
}


ldp_status_t ldp_remove_node(ldp_list* list, ldp_node* old_node){
	if (list->current_size == 0 ){
		return LDP_ERROR;
    }

	// if remove tail
	if( old_node == list->used_list_tail){
		list->used_list_tail = old_node->prev;
    }

	// remove node from list
	if (old_node->next != NULL){
		old_node->next->prev = old_node->prev;
    }
	if (old_node->prev != NULL){
		old_node->prev->next = old_node->next;
    }

	// add in unused list
	old_node->prev = list->unused_list_tail;
	old_node->next = NULL;
	list->unused_list_tail = old_node;

	list->current_size--;


	return LDP_SUCCESS;
}

void ldp_clean_list(ldp_list* list){
	while(list->used_list_tail != NULL){
		ldp_remove_node(list, list->used_list_tail);
	}
}

void ldp_destroy_list(ldp_list* list){
	if (list->data_size > 0){
		for(int i=0; i<list->max_size; i++){
			free(list->node_array[i].data);
		}
	}
	free(list->node_array);
}

