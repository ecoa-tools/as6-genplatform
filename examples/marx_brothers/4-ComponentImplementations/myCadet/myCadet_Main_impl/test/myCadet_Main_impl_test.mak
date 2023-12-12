all: test

test:
	gcc -g -Wall -o test ../src/myCadet_Main_impl.c myCadet_Main_impl_test_container.c myCadet_Main_impl_test.c -I ../inc -I ../inc-gen/ -I ../../../../0-Types/inc-gen/ -DECOA_64BIT_SUPPORT

clean:
	rm -f test
