/* Generated by PARSEC */
/* Tests of the Module Implementation myJunior_Other_impl */

#include "ECOA.h"
#include "myJunior_Other_impl.h"

#include "ECOA.h"
#include "libmarx.h"

int main(int argc, char *argv[])
{
	myJunior_Other_impl__context context;
	ECOA__uint32 ID;
	myJunior_Other_impl__INITIALIZE__received(&context);
	myJunior_Other_impl__START__received(&context);
	myJunior_Other_impl__STOP__received(&context);
	myJunior_Other_impl__SHUTDOWN__received(&context);

	ECOA__uint32 param;
	myJunior_Other_impl__TheFeedback__received(&context, param);

	myJunior_Other_impl__result__received(&context, param);

    return 0;
}
