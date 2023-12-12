# Create imported target cunit
add_library(cunit SHARED IMPORTED)

file(GLOB_RECURSE CUNIT_LIB "${CUNIT_ROOT_PATH}/lib*/libcunit.so")

set_target_properties(cunit PROPERTIES
  INTERFACE_INCLUDE_DIRECTORIES "${CUNIT_ROOT_PATH}/include"
  IMPORTED_LOCATION "${CUNIT_LIB}"
)

