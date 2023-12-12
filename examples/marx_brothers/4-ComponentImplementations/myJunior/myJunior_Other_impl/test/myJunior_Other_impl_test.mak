all: test

test:
	gcc -g -Wall -o test ../src/myJunior_Other_impl.c myJunior_Other_impl_test_container.c myJunior_Other_impl_test.c -I ../inc -I ../inc-gen/ -I ../../../../0-Types/inc-gen/ -DECOA_64BIT_SUPPORT

clean:
	rm -f test
