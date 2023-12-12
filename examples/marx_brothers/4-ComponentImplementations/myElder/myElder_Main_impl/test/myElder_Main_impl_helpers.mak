all: helpers

helpers:
	gcc -g -Wall -o helpers_test myElder_Main_impl_helpers.c myElder_Main_impl_test_container.c myElder_Main_impl_helpers_test.c -I ../inc -I ../inc-gen/ -I ../../../../0-Types/inc-gen/ -DECOA_64BIT_SUPPORT

clean:
	rm -f helpers_test
