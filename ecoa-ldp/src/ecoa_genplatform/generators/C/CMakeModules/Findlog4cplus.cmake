# Create imported target log4cplus::log4cplus
add_library(log4cplus::log4cplus SHARED IMPORTED)

file(GLOB_RECURSE LOG4CPLUS_LIB "${log4cplus_ROOT_PATH}/lib*/liblog4cplus.so")

set_target_properties(log4cplus::log4cplus PROPERTIES
  INTERFACE_INCLUDE_DIRECTORIES "${log4cplus_ROOT_PATH}/include"
  IMPORTED_LOCATION "${LOG4CPLUS_LIB}"
  INTERFACE_LINK_LIBRARIES "-lpthread;/usr/lib64/librt.so;/usr/lib64/libnsl.so"
)

