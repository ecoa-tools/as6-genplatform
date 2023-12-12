#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <assert.h>
#include <signal.h>
#include <unistd.h>
#include <inttypes.h>

#include <apr.h>
#include <apr_network_io.h>
#include <apr_errno.h>
#include <apr_strings.h>
#include <apr_poll.h>
#include <apr_thread_proc.h>

#define PD_PING_PD_ID 0
#define PD_PONG_PD_ID 1
#define PD_FINISH_PD_ID 2

#define NB_OF_RUN 5

static apr_proc_t proc[4];
static apr_procattr_t* procattr[4];
static char* prog_names[4];
static char** prog_argv[4];
static apr_pool_t* mem_pool;

void test_restart(int* start_order_array, int array_size, const char* str)
{
	int exitcode;
	apr_exit_why_e exitwhy;
	apr_status_t ret;

	for(int i=0; i<NB_OF_RUN;i++){
		printf("\n%s %i\n", str, i);

// -----------------------------------------------------------------------------
		for(int id=0; id<array_size; id++)
		{
			if (id>0) {
				apr_sleep(10000*(rand()%100));
			}

			ret= apr_proc_create(&proc[start_order_array[id]], prog_names[start_order_array[id]],
				(const char**)prog_argv[start_order_array[id]],NULL, procattr[start_order_array[id]], mem_pool);
			assert(ret == APR_SUCCESS);
		}
// -----------------------------------------------------------------------------
		for(int id=0; id<array_size; id++)
		{
			ret= apr_proc_wait(&proc[id], &exitcode, &exitwhy, APR_WAIT);
			assert(ret  == APR_CHILD_DONE);
			assert(exitwhy == APR_PROC_SIGNAL);
		}
	}
}

int main(int argc, char** argv){
	apr_status_t ret = apr_initialize();
	assert(ret==APR_SUCCESS);

	apr_pool_create(&mem_pool,NULL);

	for(int i=0;i<3;i++){
		prog_argv[i]=calloc(5,sizeof(char*));
		prog_argv[i][1] = calloc(9,sizeof(char*));
		prog_argv[i][2] = calloc(9,sizeof(char*));
		prog_argv[i][3] = calloc(9,sizeof(char*));
		prog_argv[i][4] = NULL;
		ret = apr_procattr_create(&procattr[i], mem_pool);
		assert(ret == APR_SUCCESS);
	}

	prog_names[PD_PING_PD_ID]="PD_Ping_PD";
	prog_names[PD_PONG_PD_ID]="PD_Pong_PD";
	prog_names[PD_FINISH_PD_ID]="PD_Finish_PD";

	const char ** argv_PL=calloc(2,sizeof(char*));
	argv_PL[0] = "platform";
	argv_PL[1] = NULL;
	ret = apr_procattr_create(&procattr[3], mem_pool);
	assert(ret == APR_SUCCESS);
	ret =  apr_procattr_cmdtype_set (procattr[3],APR_PROGRAM_ENV);
	assert(ret  == APR_SUCCESS);
	ret =  apr_proc_create(&proc[3], "platform", argv_PL,NULL, procattr[3], mem_pool);
	assert(ret == APR_SUCCESS);
	apr_sleep(1000*1000*2); // wait for the end of the first run

	for(int i=0;i<3;i++){
		prog_argv[i][0]=prog_names[i];
		sprintf(prog_argv[i][1], "0");
		sprintf(prog_argv[i][2], "0");
		sprintf(prog_argv[i][3], "0");
		assert( apr_procattr_cmdtype_set (procattr[i],APR_PROGRAM_ENV) == APR_SUCCESS);
	}

	// Test restart combinations
	test_restart((int []){PD_PING_PD_ID,PD_PONG_PD_ID,PD_FINISH_PD_ID}, 3, "================= kill ping[0], pong[1] and finish[2]. change order. run");
	test_restart((int []){PD_PING_PD_ID,PD_FINISH_PD_ID,PD_PONG_PD_ID}, 3, "================= kill ping[0], finish[2] and pong[1]. change order. run");

	test_restart((int []){PD_PONG_PD_ID,PD_FINISH_PD_ID,PD_PING_PD_ID}, 3, "================= kill pong[1], finish[2] and ping[0]. change order. run");
	test_restart((int []){PD_PONG_PD_ID,PD_PING_PD_ID,PD_FINISH_PD_ID}, 3, "================= kill pong[1], ping[0] and finish[2]. change order. run");

	test_restart((int []){PD_FINISH_PD_ID,PD_PING_PD_ID,PD_PONG_PD_ID}, 3, "================= kill finish[2], ping[0] and pong[1]. change order. run");
	test_restart((int []){PD_FINISH_PD_ID,PD_PONG_PD_ID,PD_PING_PD_ID}, 3, "================= kill finish[2], pong[1] and ping[0]. change order. run");

	int exitcode;
	apr_exit_why_e exitwhy;
	ret = apr_proc_kill(&proc[3],APR_KILL_AFTER_TIMEOUT);
	assert(ret == APR_SUCCESS);
	apr_proc_wait(&proc[3], &exitcode, &exitwhy, APR_WAIT);
	printf("end\n");

	return 0;
}
