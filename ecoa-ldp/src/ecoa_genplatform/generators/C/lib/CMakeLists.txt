cmake_minimum_required(VERSION 3.4)

project(ecoa)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}")

file(GLOB ${PROJECT_NAME}_src *.c eli/*.c)

if(${LDP_LOG_USE} STREQUAL "lttng")
	list(REMOVE_ITEM ${PROJECT_NAME}_src ${CMAKE_CURRENT_LIST_DIR}/ldp_log-log4cplus.c ${CMAKE_CURRENT_LIST_DIR}/ldp_log-console.c ${CMAKE_CURRENT_LIST_DIR}/ldp_log-zlog.c)
elseif(${LDP_LOG_USE} STREQUAL "console")
	list(REMOVE_ITEM ${PROJECT_NAME}_src ${CMAKE_CURRENT_LIST_DIR}/ldp_log-log4cplus.c ${CMAKE_CURRENT_LIST_DIR}/ldp_log-lttng.c ${CMAKE_CURRENT_LIST_DIR}/ldp_log-zlog.c)
elseif(${LDP_LOG_USE} STREQUAL "zlog")
	list(REMOVE_ITEM ${PROJECT_NAME}_src ${CMAKE_CURRENT_LIST_DIR}/ldp_log-log4cplus.c ${CMAKE_CURRENT_LIST_DIR}/ldp_log-lttng.c ${CMAKE_CURRENT_LIST_DIR}/ldp_log-console.c)
else()
	list(REMOVE_ITEM ${PROJECT_NAME}_src ${CMAKE_CURRENT_LIST_DIR}/ldp_log-lttng.c ${CMAKE_CURRENT_LIST_DIR}/ldp_log-console.c ${CMAKE_CURRENT_LIST_DIR}/ldp_log-zlog.c)
endif()

if(${CMAKE_USE_UDP_PROTO})
	file(GLOB ${PROJECT_NAME}_proto_src udp/*.c)
else()
	file(GLOB ${PROJECT_NAME}_proto_src tcp/*.c)
endif()

if(UNIX)
	file(GLOB ${PROJECT_NAME}_platform_src unix/*.c)
elseif(WIN32)
	file(GLOB ${PROJECT_NAME}_platform_src win32/*.c)
else(UNIX)

endif(UNIX)

include_directories(${CMAKE_CURRENT_LIST_DIR}/../)
include_directories(${CMAKE_CURRENT_LIST_DIR}/.)
include_directories(${CMAKE_CURRENT_LIST_DIR}/eli)

if(${CMAKE_USE_UDP_PROTO})
	include_directories(${CMAKE_CURRENT_LIST_DIR}/udp)
else()
	include_directories(${CMAKE_CURRENT_LIST_DIR}/tcp)
endif()

#####################
add_library(ecoa ${LDP_LINK_TYPE} ${${PROJECT_NAME}_src} ${${PROJECT_NAME}_platform_src} ${${PROJECT_NAME}_proto_src})

target_include_directories(ecoa PRIVATE ${APR_INCLUDE_DIR})
target_include_directories(ecoa PUBLIC .)
target_include_directories(ecoa PUBLIC eli/)

if(${LDP_LOG_USE} STREQUAL "lttng")
	target_link_libraries(ecoa PRIVATE lttng-ust)
elseif(${LDP_LOG_USE} STREQUAL "log4cplus")
	target_link_libraries(ecoa PRIVATE log4cplus::log4cplus)
elseif(${LDP_LOG_USE} STREQUAL "zlog")
	target_link_libraries(ecoa PRIVATE zlog)
endif()

target_include_directories(ecoa PUBLIC ./udp)
target_include_directories(ecoa PUBLIC ./tcp)
