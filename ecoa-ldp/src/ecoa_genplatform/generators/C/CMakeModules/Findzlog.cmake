# Create imported target zlog
add_library(zlog SHARED IMPORTED)

file(GLOB_RECURSE ZLOG_LIB "${ZLOG_ROOT_PATH}/lib*/libzlog.so")

set_target_properties(zlog PROPERTIES
  INTERFACE_INCLUDE_DIRECTORIES "${ZLOG_ROOT_PATH}/include"
  IMPORTED_LOCATION "${ZLOG_LIB}"
)

