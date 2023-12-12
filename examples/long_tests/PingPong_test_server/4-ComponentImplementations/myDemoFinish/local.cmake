#message(WARNING  ${CMAKE_CURRENT_LIST_DIR}/test_restart.c)

if(PIKEOS_POSIX)
  message(WARNING  "test_restart not built on Posix (no multi process available) !!!")
else()
add_executable(test_restart ${CMAKE_CURRENT_LIST_DIR}/test_restart.c)
target_include_directories(test_restart PUBLIC ${APR_INCLUDE_DIR})
target_link_libraries(test_restart ecoa)
target_link_libraries(test_restart apr-1)
if(LOG_USE_LTTNG)
	target_link_libraries(test_restart lttng-ust)
else(LOG_USE_LTTNG)
	target_link_libraries(test_restart log4cplus::log4cplus)
endif(LOG_USE_LTTNG)
target_link_libraries(test_restart ${CMAKE_THREAD_LIBS_INIT})
target_link_libraries(test_restart rt m)

add_custom_target(run_test
    COMMAND ./test_restart
    DEPENDS test_restart platform PD_Ping_PD PD_Pong_PD PD_Finish_PD
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)
endif()
