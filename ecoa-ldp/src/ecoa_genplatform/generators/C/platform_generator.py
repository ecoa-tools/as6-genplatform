# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from ..version_header_generator import generate_ldp_version_header_cmake, generate_ldp_version_header_warning
from collections import OrderedDict
from ..force_generation import file_need_generation


######################################
##### generate_main
######################################
def generate_main(multi_node, output_directory, libraries,
                  force_flag, protections_domains, fine_grain_deployment, PF_links, current_platform):
    c_filename = os.path.join(output_directory, 'main.c')

    if not file_need_generation(c_filename,
                            force_flag,
                            "    main.c already exists"):
        return

    fd = open(c_filename, 'w')

    # header
    text = generate_ldp_version_header_warning()

    text += "\
#include <stdio.h>\n\
#include <stdlib.h>\n\
#include <time.h>\n\
#include <string.h>\n\
#include <assert.h>\n\
#include <unistd.h>\n\
#include <inttypes.h>\n\
\n\
#include <apr.h>\n\
#include <apr_network_io.h>\n\
#include <apr_errno.h>\n\
#include <apr_strings.h>\n\
#include <apr_poll.h>\n\
#include <apr_thread_proc.h>\n"

    if not multi_node:
        text += "#include <apr_signal.h>\n"

    text += "\n#include \"ldp_network.h\"\n\
#include \"route.h\"\n\
#include \"ldp_time_manager.h\"\n\
#include \"ldp_log_platform.h\"\n\
#include \"ldp_fine_grain_deployment.h\"\n"

    text += "#include \"main_tools.h\"\n"
    text +="#include \"" + current_platform.name + "_fault_handler.h\"\n\n"

    text += "static apr_pool_t* mem_pool = NULL;\n\
static ldp_logger_platform platform_logger;\n\
static ldp_fault_handler_context fault_handler_context;\n\
static ldp_Main_ctx* Main_ctx = NULL;\n"

    if not multi_node:
        text += "static ldp_process_infos PD_processes[" + str(len(protections_domains)) + "] = {{ .proc = {0},\n\
                                                .prog_names = 0,\n\
                                                .proc_exit_infos = {0}}};\n\n"
        text += "void sigproc(int sig){\n\
        char log_msg[1024];\n\
        for (int i=0;i<Main_ctx->PD_number;i++) {\n\
            snprintf(log_msg, sizeof(log_msg),\n\
                     \"=== Process %s (pid=%d) is dead (exitcode=%d exitwhy=KILL BY SIGNAL(%d))\",\n\
                     PD_processes[i].prog_names, PD_processes[i].proc.pid, sig, sig);\n\
            ldp_log_PF_log(ECOA_LOG_INFO_PF, \"INFO\", &platform_logger, log_msg);\n\
        }\n\
        kill(getpid(),SIGTERM);\n\
    }\n\
    \n"

        text += "void check_ended_process(int exitcode, apr_exit_why_e exitwhy, apr_proc_t p){\n\
    for(int i=0; i<Main_ctx->PD_number; ++i) {\n\
        if(PD_processes[i].proc.pid == p.pid) {\n\
            PD_processes[i].proc.pid = -1;\n\
            PD_processes[i].proc_exit_infos.pid = p.pid;\n\
            PD_processes[i].proc_exit_infos.exitwhy = exitwhy;\n\
            PD_processes[i].proc_exit_infos.exitcode = exitcode;\n\
            break;\n\
        }\n\
    }\n\
}\n\n\
#ifdef SIGCHLD\n\
void sigchild_handler(int sig)\n\
{\n\
    UNUSED(sig);\n\
	int exitcode;\n\
	apr_exit_why_e exitwhy;\n\
	apr_proc_t p;\n\
	if(apr_proc_wait_all_procs(&p, &exitcode, &exitwhy, APR_NOWAIT, mem_pool) == APR_CHILD_DONE) {\n\
        if (exitwhy != APR_PROC_EXIT) {\n\
 	      ECOA__asset_id    l_asset_id   = p.pid;\n\
	      ECOA__asset_type  l_asset_type = ECOA__asset_type_PROTECTION_DOMAIN;\n\
	      ECOA__error_type  l_error_type = ECOA__UINT32_MAX;\n\
	      ECOA__uint32      l_error_code = 1;\n\
          for(int i=0; i<Main_ctx->PD_number; ++i) {\n\
            if(PD_processes[i].proc.pid == p.pid) {\n\
               PD_processes[i].state = PROCESS_STOPPED;\n\
               break;\n\
            }\n\
          }\n\
  	      switch(exitcode){\n\
		    case SIGSEGV:\n\
              l_error_type = ECOA__error_type_MEMORY_VIOLATION;\n\
              break;\n\
		    case  SIGFPE:\n\
              l_error_type = ECOA__error_type_NUMERICAL_ERROR;\n\
              break;\n\
		    case SIGILL:\n\
              l_error_type = ECOA__error_type_ILLEGAL_INSTRUCTION;\n\
              break;\n\
		    case SIGBUS:\n\
              l_error_type = ECOA__error_type_STACK_OVERFLOW;\n\
              break;\n\
            default:\n\
              // signal not handled by fault handler\n\
              check_ended_process(exitcode, exitwhy, p);\n\
              return;\n\
	      }\n\
          ldp_fault_error_notification(Main_ctx, l_asset_id, l_asset_type, l_error_type, l_error_code);\n\
        }\n\
        check_ended_process(exitcode, exitwhy, p);\n\
    }\n\
	apr_signal(SIGCHLD, sigchild_handler);\n\
}\n\
#endif\n\
\n\
int log_process_exit_status(void) {\n\
	char log_msg[1024];\n\
    int ret=0;\n\
	for (int i=0;i<Main_ctx->PD_number;i++) {\n\
			ldp_process_exit_infos infos = PD_processes[i].proc_exit_infos;\n\
			if (infos.pid > 0){\n\
					const char* strwhy = \"???\";\n\
					if(infos.exitwhy==APR_PROC_SIGNAL) {\n\
							strwhy=\"KILL BY SIGNAL\";\n\
							ret=-1;\n\
					} else if(infos.exitwhy==APR_PROC_EXIT) {\n\
							strwhy=\"NO ERROR\";\n\
					} else if (infos.exitwhy==(APR_PROC_SIGNAL|APR_PROC_SIGNAL_CORE)) {\n\
							strwhy=\"CORE DUMP\";\n\
							ret=-1;\n\
					}\n\
					snprintf(log_msg, sizeof(log_msg), \"=== Process %s (pid=%d) is dead (exitcode=%d exitwhy=%s(%d))\",\n\
					PD_processes[i].prog_names, infos.pid, infos.exitcode, strwhy, infos.exitwhy);\n\
					ldp_log_PF_log(ECOA_LOG_INFO_PF, \"INFO\", &platform_logger, log_msg);\n\
			}\n\
	}\n\
    return ret;\n\
}\n\
\n"
    print(text, file=fd)

    # main function
    text = "int main(void){\n"

    text += "    supervision_struct superv_tools = supervision_tools_h;\n"
    text += "   ldp_status_t ret;\n"

    text += "   // logger\n"
    text += "   platform_logger.config_filename = \"log_main_PF.properties\";\n"
    text += "   ldp_log_init((ldp_logger*)(&platform_logger));\n"
    text += "   ldp_log_PF_initialize(&platform_logger, \"main_PF\");\n"

    text += "   platform_logger.pd_name = \"main_PD\";\n"
    text += "   platform_logger.node_name = \"main_node\";\n"
    text += "   platform_logger.level_mask=0xffff;\n"
    text += "   char log_msg[1024];\n"
    text += "   snprintf(log_msg, 1024,\"=== main started\");\n"
    text += "   ldp_log_PF_log(ECOA_LOG_INFO_PF,\"INFO\", &platform_logger,log_msg);\n\n"
    text += generate_technical_cpu_affinity(fine_grain_deployment)

    text += "	ret=apr_initialize();\n"
    text += "	assert(ret==APR_SUCCESS);\n"
    text += "	apr_pool_create(&mem_pool,NULL);\n\n"

    if not multi_node:
        text += "	apr_signal(SIGINT,sigproc);\n"
        text += "#ifdef SIGCHLD\n"
        text += "	apr_signal(SIGCHLD, sigchild_handler);\n"
        text += "#endif\n\n"

    text += "    ldp_Main_ctx ctx = {.mem_pool = mem_pool,\n"
    text += "                      .PD_number = " + str(len(protections_domains)) + ",\n"
    text += "                      .logger_PF = &platform_logger,\n"
    text += "                      .fault_handler_context = &fault_handler_context,\n"
    text += "                      .fault_handler_function_ptr = &" + str(current_platform.name) + "__error_notification,\n"
    text += "                      .fault_handler_error_id = 0,\n"
    text += "                      .superv_tools = & superv_tools,\n"
    text += "                      .nb_init_clients = 0,\n"
    text += "                      .nb_ready_clients = 0,\n"
    if current_platform != None:
        # if any platform are define : dont care about platform ID. There is no ELI communication
        text += "                      .ELI_platform_ID = ELI_PF_" + str(current_platform.name) + "\n"
    text += "                     };\n"
    text += "    Main_ctx = &ctx;\n\n"

    if not multi_node:
        # create protection domain process
        text += "	// prepare arguments for each process\n"
        text += "	// arguments : [program name, component's name, NULL]\n"
        text += "	for(int i=0;i<Main_ctx->PD_number;i++){\n"
        text += "		PD_processes[i].prog_argv=calloc(2,sizeof(char*));\n"
        text += "		PD_processes[i].prog_argv[1] = NULL;\n"
        text += "		PD_processes[i].state = PROCESS_STOPPED;\n"
        text += "		PD_processes[i].pending_action = false;\n"
        text += "		ret = apr_procattr_create(&PD_processes[i].procattr, mem_pool);\n"
        text += "		if (ret != APR_SUCCESS) {\n\
           ldp_fault_error_notification(Main_ctx, i, ECOA__asset_type_COMPONENT, \
ECOA__error_type_INITIALISATION_PROBLEM, 11);\n\
        }\n"
        text += "		assert(ret== APR_SUCCESS);\n"

        text += "	}\n\n"

    text += "    " + str(current_platform.name) + "__initialize_user_context(&(ctx.fault_handler_context)->user);\n"
    text += "    ctx.fault_handler_context->platform_hook = (struct {platform_name}__platform_hook *)&ctx;\n".format(platform_name=str(current_platform.name))

    if not multi_node:
        text += "    ctx.pd_processes_array = (ldp_process_infos *)PD_processes;\n"
        for index, pd in enumerate(protections_domains.values()):
            text += "    PD_processes[" + str(index) + "].prog_names=\"./PD_" + pd.get_name() + "\";\n"

    text += "    ctx.interface_ctx_array = calloc(" + str(len(protections_domains) + len(PF_links)) + ", sizeof(ldp_interface_ctx));\n"
    # IP connection insdie PF
    for i, (pd_name, pd) in enumerate(protections_domains.items()):
        text += "    ctx.interface_ctx_array[" + str(
            i) + "].info_r= (ldp_tcp_info){" + pd_name + "_port," + pd_name + "_addr, 1, false};\n"

    # find reading ELI mcast socket
    read_binding = OrderedDict()  # binding_file -> set of PF_link_ID
    PF_link_num = 0
    for pf_link_id, pf_link in PF_links.items():
        # check if PF_link is connected with current PF
        if current_platform.name in [pf_link.source_platform, pf_link.target_platform]:
            binding_filename = pf_link.link_binding.filename
            PF_link_num += 1
            if binding_filename not in read_binding:
                read_binding[binding_filename] = set()
            read_binding[binding_filename].add(pf_link_id)

    # find connected platforms
    connected_PF = OrderedDict()  # connected_PF_name => list(PF_link_ID)
    for pf_link_id, pf_link in PF_links.items():
        # check if PF_link is connected with current PF
        if current_platform.name == pf_link.source_platform:
            connected_PF_name = pf_link.target_platform
        elif current_platform.name == pf_link.target_platform:
            connected_PF_name = pf_link.source_platform

        if connected_PF_name not in connected_PF:
            connected_PF[connected_PF_name] = []
        connected_PF[connected_PF_name].append(pf_link_id)

    template_ELI_read_socket = "\
    ctx.mcast_reader_interface[#INDEX#].type = LDP_ELI_MCAST;\n\
    ctx.mcast_reader_interface[#INDEX#].info_r = (ldp_tcp_info) {#LINK_NAME#_read_port,\n\
                                            #LINK_NAME#_read_addr,\n\
                                            #NUM_BUFFER#, false};\n"

    text += "    ctx.mcast_reader_interface_num = " + str(len(read_binding)) + "; \n"
    if len(read_binding) > 0:
        text += "    ctx.mcast_reader_interface = calloc(" + str(len(read_binding)) + ", " \
                                                                                      "sizeof(ldp_interface_ctx));\n"
    for l_index, pf_link_IDs in enumerate(read_binding.values()):
        # chose the ID name of the first PF_link_ID (because all PF_links have the same values of address and port)
        text += template_ELI_read_socket.replace("#INDEX#", str(l_index)) \
            .replace("#LINK_NAME#", list(pf_link_IDs)[0]) \
            .replace("#NUM_BUFFER#", str(0))

    template_ELI_sender_socket = "\
    ctx.mcast_sender_interface[#INDEX#].type = LDP_ELI_MCAST;\n\
    ctx.mcast_sender_interface[#INDEX#].inter.mcast.UDP_current_PF_ID = #LINK_NAME#_sent_PF_ID;\n\
    ctx.mcast_sender_interface[#INDEX#].info_r = (ldp_tcp_info) {#LINK_NAME#_sent_port,\n\
                                            #LINK_NAME#_sent_addr,\n\
                                            #NUM_BUFFER#, false};\n"

    text += "    ctx.mcast_sender_interface_num = " + str(PF_link_num) + ";\n"
    if PF_link_num > 0:
        text += "    ctx.mcast_sender_interface = calloc(" + str(PF_link_num) + ", sizeof(ldp_interface_ctx));\n"
    index = 0
    sent_interface_index = OrderedDict()
    for pf_links in read_binding.values():
        for pf_link_ID in pf_links:
            text += template_ELI_sender_socket.replace("#INDEX#", str(index)) \
                .replace("#LINK_NAME#", pf_link_ID) \
                .replace("#NUM_BUFFER#", str(0))
            sent_interface_index[pf_link_ID] = index
            index += 1

    template_PF_info = "\
    ctx.connected_platforms[#INDEX#].ELI_platform_ID = ELI_PF_#PF_ID#;\n\
    ctx.connected_platforms[#INDEX#].state = ELI_PF_DOWN;\n\
    ctx.connected_platforms[#INDEX#].sending_interface = &ctx.mcast_sender_interface[#SENT_INTERFACE_ID#];\n"

    text += "    // connected platform information\n"
    text += "    ctx.connected_platform_num = " + str(len(connected_PF)) + ";\n"
    if len(connected_PF) > 0:
        text += "    ctx.connected_platforms = calloc(" + str(len(connected_PF)) + ", sizeof(ldp_platform_info));\n"
    for pf_index, pf_name in enumerate(connected_PF.keys()):
        # chose the first available link for Platform mess
        pf_msg_link_id = connected_PF[pf_name][0]
        text += template_PF_info.replace("#INDEX#", str(pf_index)) \
            .replace("#PF_ID#", pf_name) \
            .replace("#SENT_INTERFACE_ID#", str(sent_interface_index[pf_msg_link_id]))

    text += "\n"
    if not multi_node:
        ## Protection Domains processes:
        text += "\n	for(int i=0;i<Main_ctx->PD_number;i++){\n"
        text += "		PD_processes[i].prog_argv[0]=PD_processes[i].prog_names;\n"
        text += "		ret=apr_procattr_cmdtype_set (PD_processes[i].procattr,APR_PROGRAM_ENV);\n"
        text += "		if (ret != APR_SUCCESS) {\n\
           ldp_fault_error_notification(Main_ctx, i, ECOA__asset_type_COMPONENT, \
ECOA__error_type_INITIALISATION_PROBLEM, 12);\n\
        }\n"
        text += "		assert( ret == APR_SUCCESS);\n"
        text += "		ret=apr_proc_create(&PD_processes[i].proc, PD_processes[i].prog_names, " \
                "(const char**)PD_processes[i].prog_argv,NULL, PD_processes[i].procattr, mem_pool);\n"
        text += "		if (ret != APR_SUCCESS) {\n\
           ldp_fault_error_notification(Main_ctx, i, ECOA__asset_type_COMPONENT, \
ECOA__error_type_INITIALISATION_PROBLEM, 13);\n\
        }\n"
        text += "		assert( ret== APR_SUCCESS);\n"
        text += "		PD_processes[i].state = PROCESS_RUNNING;\n"
        text += "		snprintf(log_msg, 1024,\"=== Create process %s (pid=%d)\", PD_processes[i].prog_names, " \
                "PD_processes[i].proc.pid);\n"
        text += "		ldp_log_PF_log(ECOA_LOG_INFO_PF,\"INFO\", &platform_logger,log_msg);\n"
        text += "	}\n"

    print(text, file=fd)

    # end main function

    text = "    ldp_start_father_server(&ctx, ctx.interface_ctx_array, 0);\n"

    if not multi_node:
        text += "    for(int i=0; i< Main_ctx->PD_number; i++){\n"
        text += "        if(PD_processes[i].proc.pid>0) {\n"
        text += "            int exitcode;\n"
        text += "            apr_exit_why_e exitwhy;\n"
        text += "            if(apr_proc_wait(&PD_processes[i].proc, &exitcode, &exitwhy, APR_WAIT) " \
                "== APR_CHILD_DONE) {\n"
        text += "                PD_processes[i].state = PROCESS_STOPPED;\n"
        text += "                check_ended_process(exitcode, exitwhy, PD_processes[i].proc);\n"
        text += "            }\n"
        text += "        }\n"
        text += "    }\n"

        text += "    int ret_status=log_process_exit_status();\n"
    else:
        text += "    int ret_status=0;\n"
    text += "    // clean\n"
    text += "    ldp_log_PF_deinitialize(&platform_logger);\n"
    if not multi_node:
        text += "    for (int i=0;i<Main_ctx->PD_number;i++){\n"
        text += "        free(PD_processes[i].prog_argv);\n"
        text += "    }\n"
    text += "    free(ctx.interface_ctx_array);\n"
    text += "    apr_terminate();\n"

    text += "    UNUSED(ret);\n"
    text += "    return ret_status;\n"
    text += "}\n"
    print(text, file=fd)
    fd.close()


def generate_main_tools(output_directory, component_implementations, libraries,
                        force_flag, protections_domains):
    h_filename = os.path.join(output_directory, 'main_tools.h')

    if not file_need_generation(h_filename,
                            force_flag,
                            "    main_tools.h already exists"):
        return

    fd = open(h_filename, 'w')

    text = generate_ldp_version_header_warning()
    text += "\
#ifndef _MAIN_TOOLS_H\n\
#define _MAIN_TOOLS_H\n\
#include \"ldp_structures.h\"\n"
    print(text, file=fd)
    #     text += "#include \"main_tools.h\"\n"

    #     for library in libraries:
    #         text += "#include \"" + library + ".h\"\n"
    #     text += "\n\""

    nb_of_deployed_modules = 0
    table_of_modules = []
    for pd in protections_domains.values():
        for mod in sorted(pd.deployed_modules):
            nb_of_deployed_modules += 1
            table_of_modules.append(
                [str(pd.name), str(mod.component_name), str(mod.name), str(mod.id + len(protections_domains))])

    text = ""
    count = 0
    for mod_description in table_of_modules:
        text += "static ldp_id_descriptor descriptor" + str(count) + "={" + "{0},{1},{2},{3}".format(
            c2str(mod_description[0]), c2str(mod_description[1]), c2str(mod_description[2]),
            mod_description[3]) + "};\n"
        count += 1
    print(text, file=fd)

    text = "static ldp_id_descriptor* descriptors_array[" + str(nb_of_deployed_modules) + "] = {\n"
    for count in range(nb_of_deployed_modules):
        text += "                                             &descriptor" + str(count) + ",\n"
    text += "                                            };\n"

    print(text, file=fd)

    text = ""
    text += "static ldp_id_identifier_struct my_id_identifier_val = "
    text += "{" + str(nb_of_deployed_modules) + ", descriptors_array};\n\n"

    comp_impl_dir = os.path.join(list(component_implementations.values())[0][0].impl_directory, "..")
    comp_impl_dir = os.path.normpath(os.path.realpath(comp_impl_dir))
    launcher_dir = "."
    text += "static supervision_struct supervision_tools_h = {\n"
    text += ".ldp_id_identifier = &my_id_identifier_val,\n"
    text += ".path_to_launcher_t = \"" + str(launcher_dir) + "/launcher.txt\"\n"

    text += "};\n"
    print(text, file=fd)

    print("#endif /* _MAIN_TOOLS_H */\n", file=fd)
    fd.close()

def generate_platform_cmake(multi_node, output_directory, component_implementations, components,
                            protections_domains,
                            integration_directory, current_PF, force_flag):
    cmake_filename = os.path.join(output_directory, 'CMakeLists.txt')

    if not file_need_generation(cmake_filename,
                            force_flag,
                            "    CMakeLists.txt already exists for platform"):
        return

    fd = open(cmake_filename, 'w')
    text = generate_ldp_version_header_cmake()
    text += "cmake_minimum_required(VERSION 3.4)\n\n"
    text += "project(platform)\n\n"

    text += "###########\n"
    for pd in protections_domains.values():
        text += "add_executable(PD_" + pd.get_name() + " PD_" + pd.get_name() + ".c)\n"
        text += "target_include_directories(PD_" + pd.get_name() + " PUBLIC ${APR_INCLUDE_DIR} \n"
        for comp in pd.get_all_component_names():
            text += "    " + os.path.join("${CMAKE_CURRENT_SOURCE_DIR}", "..",
                                          components[comp].get_component_implementation()) + "\n"
        text += "    )\n"

        text += "target_link_libraries(PD_" + pd.get_name() + " "
        for comp_impl in pd.get_all_component_implementations_name(components):
            text += "lib_" + comp_impl + " "
        text += ")\n"
        text += "target_link_libraries(PD_" + pd.get_name() + " ecoa apr-1)\n"
        text += "if(${LDP_LOG_USE} STREQUAL \"lttng\")\n"
        text += "    target_link_libraries(PD_" + pd.get_name() + " lttng-ust)\n"
        text += "elseif(${LDP_LOG_USE} STREQUAL \"log4cplus\")\n"
        text += "    target_link_libraries(PD_" + pd.get_name() + " log4cplus::log4cplus)\n"
        text += "elseif(${LDP_LOG_USE} STREQUAL \"zlog\")\n"
        text += "    target_link_libraries(PD_" + pd.get_name() + " zlog)\n"
        text += "endif()\n"
        text += "target_link_libraries(PD_" + pd.get_name() + " ${CMAKE_THREAD_LIBS_INIT} rt m)\n\n"

    l_fault_handler_dir = os.path.realpath(integration_directory)
    l_fault_handler_file = "{0}/src/{1}_fault_handler.c".format(l_fault_handler_dir, current_PF.name)
    l_fault_conainer_file = "{0}/src-gen/{1}_container.c".format(l_fault_handler_dir, current_PF.name)

    text += "add_executable(platform main.c " + l_fault_handler_file + " " +l_fault_conainer_file + ")\n"
    text += "target_include_directories(platform PUBLIC ${APR_INCLUDE_DIR}\n"
    text += "                                           " + l_fault_handler_dir + "/inc-gen\n"
    text += "                                           " + l_fault_handler_dir + "/inc)\n"
    text += "if(${LDP_LOG_USE} STREQUAL \"zlog\")\n"
    text += "    file(GLOB ConfigFiles ${CMAKE_CURRENT_SOURCE_DIR}/log_properties/*.zlog)\n"
    text += "else()\n"
    text += "    file(GLOB ConfigFiles ${CMAKE_CURRENT_SOURCE_DIR}/log_properties/*.properties)\n"
    text += "endif()\n"
    text += "foreach(File ${ConfigFiles})\n"
    text += "    get_filename_component(FileBase ${File} NAME_WE)\n"
    text += "    add_custom_command(\n"
    text += "            TARGET platform POST_BUILD\n"
    text += "            COMMAND ${CMAKE_COMMAND} -E copy\n"
    text += "                    ${File}\n"
    text += "                    ${CMAKE_BINARY_DIR}/bin/${FileBase}.properties)\n"
    text += "endforeach()\n"

    text += "if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/Pinfo)\n"
    text += "    file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/Pinfo DESTINATION ${CMAKE_SOURCE_DIR}/bin)\n"
    text += "endif()\n"

    if multi_node:
        text += "if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/multi-nodes.py)\n"
        text += "    file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/multi-nodes.py DESTINATION ${CMAKE_SOURCE_DIR}/bin " \
                "FILE_PERMISSIONS OWNER_EXECUTE OWNER_WRITE OWNER_READ)\n"
        text += "endif()\n"

    text += "target_link_libraries(platform ecoa)\n"
    text += "target_link_libraries(platform apr-1)\n"
    text += "if(${LDP_LOG_USE} STREQUAL \"lttng\")\n"
    text += "	target_link_libraries(platform lttng-ust)\n"
    text += "elseif(${LDP_LOG_USE} STREQUAL \"log4cplus\")\n"
    text += "	target_link_libraries(platform log4cplus::log4cplus)\n"
    text += "elseif(${LDP_LOG_USE} STREQUAL \"zlog\")\n"
    text += "	target_link_libraries(platform zlog)\n"
    text += "endif()\n"
    text += "target_link_libraries(platform ${CMAKE_THREAD_LIBS_INIT})\n"
    text += "target_link_libraries(platform rt m)\n\n"

    text += "if (EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/local.cmake )\n"
    text += "	include(${CMAKE_CURRENT_SOURCE_DIR}/local.cmake)\n"
    text += "endif (EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/local.cmake )\n"

    print(text, file=fd)
    fd.close()


def c2str(incoming_str):
    return "\"" + str(incoming_str) + "\""


def generate_id_identifying_struct(output_directory, protection_domains):
    return


def generate_technical_cpu_affinity(fine_grain_deployment):
    text = ""
    if fine_grain_deployment != None:
        # return text

        text += "    /* main process is deployed one of the technical nodes */"
        # chose the first computingNode
        node_name = fine_grain_deployment.technical_cores[0].node_name
        platform_name = fine_grain_deployment.technical_cores[0].platform_name
        text += "    /* chose node " + node_name + " on " + platform_name + " */\n"
        cpu_IDs = [c.core_id for c in fine_grain_deployment.technical_cores \
                   if c.platform_name == platform_name and c.node_name == node_name]
        nb_cpu = len(cpu_IDs)
        cpu_IDs_str = ",".join(cpu_IDs)

        text += "    cpu_mask cpu_mask =  ldp_create_cpu_mask(" + str(nb_cpu) + ", (int[" + str(
            nb_cpu) + "]){" + cpu_IDs_str + "});\n"
        text += "    ret = ldp_set_proc_affinty(cpu_mask);\n"
        text += "    if (ret != LDP_SUCCESS){\n"
        text += "        ldp_log_PF_log(ECOA_LOG_WARN_PF,\"WARNING\", &platform_logger,\"Enable to set CPU affinity of main process\");\n"
        text += "    }\n"
    else:
        text += "    /* chose every cores on the node */\n"
        text += "    /* No need tyo set affinity: every cores are enable by default */\n"
        text += "    cpu_mask ldp_create_cpu_mask_full(void);\n"
    text += "    log_thread_deployment_properties(&platform_logger);\n\n"
    return text
