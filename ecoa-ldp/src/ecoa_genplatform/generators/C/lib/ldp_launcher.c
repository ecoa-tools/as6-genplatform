/**
* @file ldp_launcher.c
* @brief ECOA launcher
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include <apr.h>
#include <apr_thread_cond.h>
#include <apr_poll.h>
#include <apr_errno.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <unistd.h>

#include "ldp_thread.h"
#include "ldp_launcher.h"

#include "ldp_fine_grain_deployment.h"
#include "ldp_fifo_manager.h"
#include "ldp_network.h"


static char seconds[12] = "s";
static char miliseconds[12] = "ms";
static char minutes[12] = "m";
static char minutes2[12] = "min";

static char opstart[12] = "Start";
static char opinit[12] = "Initialize";
static char opshutdown[12] = "Shutdown";
static char opstop[12] = "Stop";
static char opwait[12] = "Wait";

static char PDtype[12] = "*PD";
static char all_ref[12] = "*";

static void log_wait_request(int duration, char durationunit[12], ldp_logger_platform* logger_PF){
    /**
 * @brief      Displays that a Wait Request is executed.
 */
    if (duration>=0) {
        ldp_log_PF_log_var(ECOA_LOG_INFO_PF, "INFO", logger_PF,
                        	 "[Launcher_Thread] Wait request (%i %s)",duration,durationunit);
    }
    else {
        ldp_log_PF_log_var(ECOA_LOG_INFO_PF, "INFO", logger_PF,
		                     "[Launcher_Thread] Wait request (%i %s) : No wait executed",duration,durationunit);
    }
}

static bool wait_for(int duration, char durationunit[12], ldp_logger_platform* logger_PF){
    /**
 * @brief      Waits for the requested time to wait using apr_sleep.
 *
 *
 * @param  duration   int corresponding to the expected duration of wait
 * @param  durationunit      unit of the value to wait. Shall be "s", "ms", "m" or "min"
 * @param  logger_PF size ldp logger platform
 */
    if (strncmp (durationunit, miliseconds, 12) == 0){
        log_wait_request(duration, durationunit, logger_PF);
        apr_sleep(1000*duration);
        return true;
    }
    else if (strncmp(durationunit, seconds, 12) == 0){
        log_wait_request(duration, durationunit, logger_PF);
        apr_sleep(1000000*duration);
        return true;
    }
    else if ((strncmp (durationunit, minutes, 12) == 0) || (strncmp(durationunit, minutes2, 12) == 0) ){
        log_wait_request(duration, durationunit, logger_PF);
        apr_sleep(60000000*duration);
        return true;
    }
    else{
        return false;
    }
}

static int32_t find_id_of_mod(char* compname, char* modname, ldp_id_identifier_struct* my_id_identifier){
        /**
 * @brief      Finds and returns the ID of the (unique) module (if existing) who characteristics are given in parameters
 *
 *
 * @param  compname   name of the component of the module to find
 * @param  module      name of the module to find
 * @param  my_id_identifier struct containing all the information about deployed modules

 * @return  the ID of the module if found, -1 if the module was not found.
 */
    uint16_t nb_of_elements = my_id_identifier->size;
    for (int i=0; i<nb_of_elements; i++){

        if ((strcmp(compname, my_id_identifier->descriptors_array[i]->comp_name) == 0) &&
            (strcmp(modname, my_id_identifier->descriptors_array[i]->mod_name) == 0)){
                return my_id_identifier->descriptors_array[i]->id;
        }
    }
    return -1;
}

static ldp_status_t write_msg_params(ldp_logger_platform* logger_PF,
                                    ldp_interface_ctx* interface_ctx,
                                    uint16_t msg_ID,
                                    uint32_t OP_ID,
                                    uint16_t dest_mod_ID)
        /**
 * @brief      Sends message of type given in parameters to destination module given in parameters
 *
 *
 * @param  logger_PF   ldp logger platform
 * @param  interface_ctx   ldp_interface_ctx*
 * @param  msg_ID   Synchronisation message (LDP_ID_SYNC if further details))
 * @param  OP_ID  Operation ID
 * @param  dest_mod_ID   ID of the destination module

 * @return  LDP_SUCCESS if it worked correctly. Other status if not.
 */
{
    unsigned char msg[LDP_HEADER_TCP_SIZE + sizeof(uint32_t) + sizeof(uint16_t)];

    msg[LDP_HEADER_TCP_SIZE]= dest_mod_ID & 0xFF;
    msg[LDP_HEADER_TCP_SIZE+1]= (dest_mod_ID>>8) & 0xFF;

    msg[LDP_HEADER_TCP_SIZE+2]= OP_ID & 0xFF;
    msg[LDP_HEADER_TCP_SIZE+3]= (OP_ID>>8) & 0xFF;
    msg[LDP_HEADER_TCP_SIZE+4]= (OP_ID>>16) & 0xFF;
    msg[LDP_HEADER_TCP_SIZE+5]= (OP_ID>>24) & 0xFF;

    ldp_written_IP_header((char*)msg, sizeof(uint32_t) + sizeof(uint16_t), msg_ID);

    net_data_w data_w;
#if USE_UDP_PROTO
    data_w.module_id = 0x01;
#endif
    ldp_status_t ret=ldp_IP_write(interface_ctx, (char*)msg, LDP_HEADER_TCP_SIZE
        +sizeof(uint32_t) + sizeof(uint16_t) , &data_w);
    if(ret != LDP_SUCCESS){
        ldp_log_PF_log_var(ECOA_LOG_ERROR_PF, "ERROR", logger_PF,
                        	 "*[MAIN] cannot send message to client. msg = %i", msg_ID);
    }
    return ret;
}

static ldp_status_t send_to_client(ldp_logger_platform* logger_PF,
                                        ldp_interface_ctx* interface_ctx_array,
                                        int client_num,
                                        uint16_t msg_ID,
                                        uint32_t OP_ID,
                                        uint16_t dest_mod_ID)
        /**
 * @brief      Requests the function write_msg_params to send the given message on each interface.

 @return  LDP_SUCCESS if it worked correctly, LDP_ERROR otherwise.
 */
{
    ldp_status_t ret= LDP_SUCCESS;
    for(int i=0;i<client_num;i++){
        if(write_msg_params(logger_PF, &interface_ctx_array[i],msg_ID, OP_ID, dest_mod_ID) != LDP_SUCCESS){
            ret = LDP_ERROR;
        }
    }
    return ret;
}

static void send_op_to_dest(uint32_t ID_dest, char optype[12], ldp_logger_platform* logger_PF,
                            ldp_interface_ctx* interface_ctx_array, int client_num)
{
            /**
 * @brief      Calls send_to_client to send the right messages.
 *
 *
 * @param  ID_dest   ID of the destination module
 * @param  optype   The type of the operation (full name)
 * @param  logger_PF ldp logger platform,
 * @param  interface_ctx_array
 * @param  client_num   Number of clients

 * @return  LDP_SUCCESS if it worked correctly, LDP_ERROR otherwise.
 */
    if ( strncmp (optype, opstart, 12) == 0) {
                send_to_client(logger_PF,
                                interface_ctx_array,
                                client_num,
                                LDP_ID_SYNC,
                                LDP_ID_START_life,
                                ID_dest);

    }
    else if ( strncmp (optype, opinit, 12) == 0) {
        send_to_client(logger_PF,
                        interface_ctx_array,
                        client_num,
                        LDP_ID_SYNC,
                        LDP_ID_INITIALIZE_life,
                        ID_dest);
    }
    else if ( strncmp (optype, opshutdown, 12) == 0) {
        send_to_client(logger_PF,
                        interface_ctx_array,
                        client_num,
                        LDP_ID_SYNC,
                        LDP_ID_SHUTDOWN_life,
                        ID_dest);
    }
    else if ( strncmp (optype, opstop, 12) == 0) {
        send_to_client(logger_PF,
                        interface_ctx_array,
                        client_num,
                        LDP_ID_SYNC,
                        LDP_ID_STOP_life,
                        ID_dest);
    }
	else {
	//for sonarqube
	}
}

static bool emptyline(char line[512]){
            /**
 * @brief      Checks whether the given line is a blank line or not
 *             (blank line meaning only spaces or tabs  and line return).
 *
 *
 * @param  line   The line to analyse

 * @return  true if the line is a blank line. false if it is not.
 */
    int j = 0;
    while (line[j]== ' '){
        j+=1;
    }
    if  ((line[j] == '\n') || (line[j] == '\r')){
        return true;
    }
    return false;
}

void * launch_func(apr_thread_t* t, void* args){
 /**
 * @brief      Parses the file launcher.txt and realises requested operations.
 *
 *
 * @param   t      apr_thread_t*
 * @param   args   pointer to struct of type "launching_thread_params" (needed information)

 * @return  Nothing
 */
    UNUSED(t);
    FILE *userlaunch_stream;

    char optype[12];
    char secondattr[128];
    char thirdattr[128];
    int duration;
    char durationunit[4];

    launching_thread_params* params = (launching_thread_params*)args;

    int client_num = params->client_num_t;
    char* path_to_launcher = params->path_t;

    ldp_logger_platform* logger_PF = params->logger_PF_t;
    ldp_interface_ctx* interface_ctx_array = params->interface_ctx_array_t;
    ldp_id_identifier_struct* my_id_identifier = params->ldp_id_identifier_t;
    userlaunch_stream = fopen (path_to_launcher,"r");

    char linec[512] = "";

    int linenumber = 0;
    while (fgets (linec, 512, userlaunch_stream) != NULL)
    {
        linenumber += 1;

        optype[0] = '\0';
        secondattr[0] = '\0';
        thirdattr[0] = '\0';
        duration = 0;
        durationunit[0] = '\0';

        if(!emptyline(&linec[0]))
        {
            sscanf(linec, "%s", optype);
            if ( strncmp (optype, opwait, 12) == 0)
            {
                // Wait
                sscanf(linec, "%s %i %s", optype, &duration, durationunit);
                if (!wait_for(duration, durationunit, logger_PF)){
                    ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARN", logger_PF,
					                     "[Launcher_Thread] Warning : In launcher.txt line %i: Error in Wait Request. No wait",
										 linenumber);
                }
            }
            else if ((strncmp(optype, opstart, 12)==0) || (strncmp(optype, opinit, 12)==0) ||
			         (strncmp(optype, opshutdown, 12)==0) || (strncmp(optype, opstop, 12)==0))
            {
                // One of the four known operations
                sscanf(linec, "%s %s %s", optype, secondattr, thirdattr);
                if (strncmp(secondattr, all_ref, 12) == 0)
                {
                    // Launch all modules
                    uint16_t nb_of_elements = my_id_identifier->size;
                    for (int i=0; i<nb_of_elements; i++)
                    {
                        send_op_to_dest(my_id_identifier->descriptors_array[i]->id, optype,
						                logger_PF, interface_ctx_array, client_num);
                    }
                }
                else if ((thirdattr[0] == '\0') || (secondattr[0] == '\0')){
                // Not valid
                    ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARN", logger_PF,
					                     "[Launcher_Thread] Warning : In launcher.txt line %i: Missing attributes. Line ignored. \n",
										 linenumber);
                }

                else if (strncmp(secondattr, PDtype,32) == 0)
                {
                // Launch all modules of a given protection domain
                    uint16_t nb_of_elements = my_id_identifier->size;
                    for (int i=0; i<nb_of_elements; i++)
                    {
                        if (strcmp(thirdattr, my_id_identifier->descriptors_array[i]->pd_name) == 0)
                        {
                            send_op_to_dest(my_id_identifier->descriptors_array[i]->id, optype,
							                logger_PF, interface_ctx_array, client_num);
                        }
                    }
                }
                else
                {
                // In a given component
                    if (strncmp(thirdattr, all_ref, 12) == 0)
                    {
                        // All modules the  component
                        uint16_t nb_of_elements = my_id_identifier->size;
                        for (int i=0; i<nb_of_elements; i++)
                        {
                            if (strcmp(secondattr, (my_id_identifier->descriptors_array[i])->comp_name) == 0)
                            {
                                send_op_to_dest(my_id_identifier->descriptors_array[i]->id,
								                optype, logger_PF, interface_ctx_array, client_num);
                            }
                        }
                    }
                   else {
                        // A precise module
                        int32_t ID_dest;
                        ID_dest = find_id_of_mod(secondattr, thirdattr, my_id_identifier);
                        if (ID_dest == -1){
                            ldp_log_PF_log_var(ECOA_LOG_INFO_PF, "INFO", logger_PF,
							                     "[Launcher_Thread] Warning : Module %s in component %s could not be reached.\n",
												 thirdattr,secondattr);
                        }
                        else {
                            send_op_to_dest(ID_dest, optype, logger_PF, interface_ctx_array, client_num);
                        }
                    }
                }
            }
            else
            {
                // Line to ignore
                char comment[1] = "#";
                char comment_to_print[3] = "###";
                if (strncmp(optype, comment_to_print,3) == 0){
                    //comment to display
                    ldp_log_PF_log_var(ECOA_LOG_INFO_PF, "INFO", logger_PF, "%s",linec);

                }
                else if (strncmp (optype, comment, 1) != 0)
                {
                    // Not a comment means that it is an unknown operation
                    ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARN", logger_PF,
					                     "[Launcher_Thread] Warning : In launcher.txt line %i: Unknown operation \"%s\".\n Reminder: Accepted operations are Initialize, Start, Shutdown, Stop and Wait.\n",
										 linenumber, optype);
                }
				else{
				    // Blank line
				}
            }
        }
        else {
            // Blank line
        }
    }

    ldp_log_PF_log_var(ECOA_LOG_INFO_PF, "INFO", logger_PF, "***Reached End Of File launcher.txt");

    fclose(userlaunch_stream);
    return NULL;
}



void ldp_create_launching_thread(apr_pool_t* mem_pool, launching_thread_params* params){

	apr_threadattr_t* launch_attr;
	apr_threadattr_create(&launch_attr,mem_pool);
    cpu_mask mask = ldp_create_cpu_mask(0, NULL);
    ldp_thread_properties prop = {.priority=0,
                                    .policy=LDP_SCHED_OTHER,
                                    .cpu_affinity_mask=mask,
                                    .thread_name=params->name,
                                    .logger=params->logger_PF_t};
	ldp_thread_create(params->launch_thread_ptr, launch_attr, launch_func, (void*)params, &prop, mem_pool);
}
