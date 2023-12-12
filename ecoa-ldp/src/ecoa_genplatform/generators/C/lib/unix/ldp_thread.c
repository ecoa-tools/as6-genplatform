/**
* @file ldp_thread.c
* @brief ECOA ldp thread functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifndef _GNU_SOURCE
#define _GNU_SOURCE /* Needed for pthread_setname_np and syscall */
#endif

#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>
#include <sched.h>
#include <sys/syscall.h>
#include "ldp_thread.h"
#include "ldp_status_error.h"
#include "ldp_structures.h"
#include "ldp_fine_grain_deployment.h"

struct ecoa_thread_args_t {
	apr_thread_start_t func;
	int policy;
	int priority;
	int niceness;
	cpu_set_t cpu_affinity_mask;
	const char* thread_name;
	void * data;
	ldp_logger_platform* logger;
};

static void SigXCPUHandler(int n)
{
	/* If a RT thread consume too much CPU, then abort all */
	UNUSED(n);
	abort();
}

static void * thread_routine (apr_thread_t* thread, void * data)
{
	const struct rlimit rttime_limit = {
		1000000, /* soft limit 1s */
		2000000  /* hard limit 2s */
	};
	struct ecoa_thread_args_t* args = (struct ecoa_thread_args_t*)data;
	struct sched_param param;

	int tid = syscall(SYS_gettid);
	int ret_val;
	pthread_t current_thread = pthread_self();

	/* Set thread name */
	if(args->thread_name!=NULL){
		// restrict thread name to only 15 bytes + '\0'
		char tmp_name[16];
		strncpy(tmp_name, args->thread_name, 15);
		tmp_name[15]='\0';
		ret_val = pthread_setname_np(current_thread, tmp_name);
		if (ret_val != 0){
			ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARNING",args->logger, "impossible to set thread name %s (errno=%i)",args->thread_name, ret_val);
		}
	}

	/* Set scheduling priority */
	/* Set Scheduling policy */
// OD BEGIN
	param.sched_priority = args->priority;
// OD END
	ret_val = pthread_setschedparam(current_thread, args->policy, &param);
	if (ret_val != 0){
		ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARNING",args->logger, "impossible to set scheduler (priority=%d::policy=%d): %s(errno=%i)", param.sched_priority, args->policy, args->thread_name, ret_val);
	}

	/* Set cpu affinity */
	pthread_setaffinity_np(current_thread,
                               sizeof(cpu_set_t),
                               &args->cpu_affinity_mask);

	/* Set niceness */
	setpriority(PRIO_PROCESS, tid, args->niceness);

	switch(args->policy) {
	case SCHED_RR:
	case SCHED_FIFO:
		/* Protected system against insane RT thread */
		setrlimit(RLIMIT_RTTIME, &rttime_limit);
		signal(SIGXCPU, SigXCPUHandler);

		break;
	case SCHED_OTHER:
	default:
		break;
	}

	log_thread_deployment_properties(args->logger);

	/* Run */
	return args->func(thread, args->data);
}


static int prio_ecoa_to_unix(int sched_policy, int ecoa_priority)
{
	int unix_priority;

	int pmin = sched_get_priority_min(sched_policy);
	int pmax = sched_get_priority_max(sched_policy);

	switch(sched_policy) {
	case SCHED_RR:
	case SCHED_FIFO:
	// case SCHED_DEADLINE:
		/* We don't want to compete with kernel: */
		pmax -= 10;
		/* for ecoa, priority 0 means the highest priority
		 * for unix, RT priority 1 means the lowest priority */
		unix_priority = pmax - ecoa_priority;
		if(unix_priority<pmin){
			unix_priority = pmin;
        }
		if(unix_priority>pmax){
			unix_priority = pmax;
        }
		break;
	case SCHED_OTHER:
	case SCHED_IDLE:
	case SCHED_BATCH:
	default:
		/* Here priority is niceness */
		/* for unix, higher niceness means lowest priority */
		unix_priority = -20+ecoa_priority;
		if(unix_priority<-20){
            unix_priority = -20;
        }
		if(unix_priority>19){
            unix_priority = 19;
        }
		break;
	}

	return unix_priority;
}

ldp_status_t ldp_thread_create(apr_thread_t **new,
                                apr_threadattr_t *attr,
                                apr_thread_start_t func,
                                void *data, ldp_thread_properties* properties,
                                apr_pool_t *pool)
{
	apr_status_t status;
	struct ecoa_thread_args_t* args;

	args = (struct ecoa_thread_args_t*)apr_pcalloc(pool, sizeof(struct ecoa_thread_args_t));

	args->func = func;
	args->data = data;

	if(properties->priority<0) {
		args->policy = SCHED_OTHER;
		args->niceness = prio_ecoa_to_unix(args->policy, -properties->priority);
		args->priority = 0;
	}
	else {
		switch(properties->policy){
			case SCHED_FIFO:
			case SCHED_RR:
			// case SCHED_DEADLINE:
				args->policy = properties->policy;
				args->priority = prio_ecoa_to_unix(args->policy, properties->priority);
				args->niceness = 0;
				break;
			case SCHED_OTHER:
			case SCHED_IDLE:
			case SCHED_BATCH:
				args->policy = properties->policy;
				args->priority = 0;
				args->niceness = prio_ecoa_to_unix(args->policy, properties->priority);
				break;
			default:
				args->policy = SCHED_OTHER;
				args->priority = 0;
				args->niceness = prio_ecoa_to_unix(args->policy, properties->priority);
				break;
		}
	}
	args->thread_name = properties->thread_name;
	args->cpu_affinity_mask = properties->cpu_affinity_mask;
	args->logger = properties->logger;

	status = apr_thread_create(new, attr, thread_routine, args, pool);

	return status;
}

