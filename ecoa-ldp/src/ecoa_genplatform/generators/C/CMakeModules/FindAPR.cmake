# Find APR install path

if (APR_ROOT_PATH)

	find_program( APR_CONFIG_EXECUTABLE  "apr-1-config"
		          HINTS ${APR_ROOT_PATH}
		          PATH_SUFFIXES bin)

else (APR_ROOT_PATH)
	find_program( APR_CONFIG_EXECUTABLE  "apr-1-config"
		          HINTS ENV APR_ROOT_PATH
		          PATH_SUFFIXES bin)

endif(APR_ROOT_PATH)

set ( APR_INCLUDE_DIR "" CACHE PATH "Path to APR header files" )
set ( APR_INCLUDE_FLAGS "" CACHE STRING "APR include flags" )
set ( APR_LIB_DIR "" CACHE PATH "Path to APR library" )
set ( APR_LIB_FLAGS "" CACHE STRING "APR include flags" )

if (APR_CONFIG_EXECUTABLE)
	execute_process(COMMAND ${APR_CONFIG_EXECUTABLE} "--includedir"
	                OUTPUT_VARIABLE APR_INCLUDE_DIR)
	execute_process(COMMAND ${APR_CONFIG_EXECUTABLE} "--includes"
	                OUTPUT_VARIABLE APR_INCLUDE_FLAGS)
	execute_process(COMMAND ${APR_CONFIG_EXECUTABLE} "--prefix"
	                OUTPUT_VARIABLE _apr_prefix_dir)
	execute_process(COMMAND ${APR_CONFIG_EXECUTABLE} "--link-ld"
	                OUTPUT_VARIABLE APR_LIB_FLAGS)

	if(APR_INCLUDE_DIR)
		string(REGEX REPLACE "[ \r\n]" "" APR_INCLUDE_DIR "${APR_INCLUDE_DIR}")
		set ( APR_INCLUDE_DIR ${APR_INCLUDE_DIR} CACHE PATH "Path to APR header files" FORCE )
	endif(APR_INCLUDE_DIR)

	if(APR_INCLUDE_FLAGS)
		string(REGEX REPLACE "[\r\n]" "" APR_INCLUDE_FLAGS "${APR_INCLUDE_FLAGS}")
		set ( APR_INCLUDE_FLAGS ${APR_INCLUDE_FLAGS} CACHE STRING "APR include flags" FORCE )
	endif(APR_INCLUDE_FLAGS)

	if (_apr_prefix_dir)
		string(REGEX REPLACE "[ \r\n]" "" _apr_prefix_dir "${_apr_prefix_dir}")
		set ( APR_LIB_DIR "${_apr_prefix_dir}/lib" CACHE PATH "Path to APR library" FORCE )
	endif (_apr_prefix_dir)

	if(APR_LIB_FLAGS)
		string(REGEX REPLACE "[\r\n]" "" APR_LIB_FLAGS "${APR_LIB_FLAGS}")
		set ( APR_LIB_FLAGS ${APR_LIB_FLAGS} CACHE STRING "APR include flags" FORCE )
	endif(APR_LIB_FLAGS)

endif (APR_CONFIG_EXECUTABLE)

IF (APR_INCLUDE_DIR)
	SET(APR_FOUND TRUE)
ELSE (APR_INCLUDE_DIR)
	SET(APR_FOUND FALSE)
ENDIF (APR_INCLUDE_DIR)

MARK_AS_ADVANCED( APR_FOUND )

