DEPS=$(PWD)/install-bin

all: $(DEPS) $(DEPS)/lib/libapr-1.so $(DEPS)/lib/liblog4cplus.so $(DEPS)/lib/libzlog.so $(DEPS)/lib/libcunit.so

$(DEPS):
	@mkdir -p $(DEPS)

$(DEPS)/lib/libapr-1.so:
	tar xfz apr-1.6.2.tar.gz
	(cd apr-1.6.2 && ./configure --prefix=$(DEPS))
	make -C apr-1.6.2 all install && rm -rf apr-1.6.2

$(DEPS)/lib/liblog4cplus.so:
	tar xfj log4cplus-2.0.0.tar.bz2
	(cd log4cplus-2.0.0 && ./configure --prefix=$(DEPS))
	make -C log4cplus-2.0.0 all install && rm -rf log4cplus-2.0.0

$(DEPS)/lib/libzlog.so:
	tar xfz zlog-1.2.16.tar.gz
	make -C zlog-1.2.16 PREFIX=$(DEPS) all install && rm -rf zlog-1.2.16

$(DEPS)/lib/libcunit.so:
	tar xfj CUnit-2.1-3.tar.bz2
	(cd CUnit-2.1-3 && ./bootstrap && ./configure --prefix=$(DEPS))
	make -C CUnit-2.1-3 all install && rm -rf CUnit-2.1-3

clean:
	rm -rf $(DEPS)
