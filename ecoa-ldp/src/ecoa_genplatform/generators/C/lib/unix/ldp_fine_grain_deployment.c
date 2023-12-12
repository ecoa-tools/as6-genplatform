/**
* @file ldp_fine_grain_deployment.c
* @brief ECOA fine grain deployement functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#define _GNU_SOURCE
#include <pthread.h>
#include <sched.h>
#include <sys/types.h>
#include <sys/resource.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <stdio.h>

#include "ldp_fine_grain_deployment.h"
#include "ldp_log_platform.h"


cpu_mask ldp_create_cpu_mask(int nb_cpu, int* cpu_ids){
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    for(int i=0; i <nb_cpu; i++){
        CPU_SET(cpu_ids[i], &cpuset);
    }
    return cpuset;
}

cpu_mask ldp_create_cpu_mask_full(void){
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    for(int i=0; i <sizeof(cpu_set_t); i++){
        CPU_SET(i, &cpuset);
    }
    return cpuset;
}

ldp_status_t ldp_set_proc_affinty(cpu_set_t mask){
    int ret = sched_setaffinity(getpid(), sizeof(cpu_set_t), &mask);
    if (ret == 0){
        return LDP_SUCCESS;
    }else{
        return LDP_ERROR;
    }
}

void log_thread_deployment_properties(ldp_logger_platform* logger){
    cpu_set_t cpumask;
    int sched_policy = -1;
    struct sched_param sched_param;
    int niceness = -1;
    char thread_name[16];

    pthread_t thread=pthread_self();
    int tid = syscall(SYS_gettid);

    pthread_getaffinity_np(thread,
                           sizeof(cpu_set_t),
                           &cpumask);
    pthread_getschedparam(thread, &sched_policy, &sched_param);
    niceness = getpriority(PRIO_PROCESS, tid);
    pthread_getname_np(pthread_self(), thread_name, 16);

    char cpu_mask_str[4*CPU_SETSIZE];
    for(int i=0; i<4;i++){
        if(CPU_ISSET(i, &cpumask)){
            snprintf(&cpu_mask_str[i*2],4,"|%d",i);
        }else{
            snprintf(&cpu_mask_str[i*2],4,"| ");
        }
    }

    ldp_log_PF_log_var(ECOA_LOG_INFO,
                         "INFO",
                         logger,
                         "thread_name: %s (%i) - sched_policy:%i - priority:%i - niceness:%i - cpu mask: %s",
                          thread_name,
                          tid,
                          sched_policy,
                          sched_param.sched_priority,
                          niceness,
                          cpu_mask_str);
}
