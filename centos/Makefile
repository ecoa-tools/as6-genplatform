#
# Dependencies 
#
ECOA_DEPS_DIR ?= /usr

LOG4CPLUS_DIR=$(ECOA_DEPS_DIR)
APR_DIR=$(ECOA_DEPS_DIR)
CUNIT_DIR=$(ECOA_DEPS_DIR)
ZLOG_DIR=$(ECOA_DEPS_DIR)

APPS_DIR=../examples
OUTPUT_DIR=app.rootfs
CUNIT_OUTPUT_DIR=$(OUTPUT_DIR)/cunit
ECOA_FRAMEWORK=ECOA Framework
ECOA_PROJECT=marx_brothers
ECOA_PROJECT_XML_NAME=$(ECOA_PROJECT)
ECOA_PROJECT_XML_DIR=$(OUTPUT_DIR)/$(ECOA_PROJECT)
ECOA_OUTPUT_DIR=$(ECOA_PROJECT_XML_DIR)/$(shell sed -n -e 's/.*<\outputDirectory>\(.*\)<\/outputDirectory>.*/\1/p' $(APPS_DIR)/$(ECOA_PROJECT)/$(ECOA_PROJECT_XML_NAME).project.xml)
ECOA_USERID=0
FMK_TESTS_DIR=../ecoa-ldp/tests/fmk_tests
ECOA_FMK_TESTS=app.fmk_tests
ECOA_CONTAINER_NAME=$(shell echo $(ECOA_PROJECT_XML_NAME) | tr '[:upper:]' '[:lower:]')
ECOA_CONTAINER_LOGS=logs

all:

#
#  Unit tests
#
bootstrap_cunit:
	@echo "Bootstrapping CUNIT $(ECOA_FRAMEWORK)"
	@mkdir -p $(CUNIT_OUTPUT_DIR) && \
	cmake3 -DLOG4CPLUS_DIR=$(LOG4CPLUS_DIR) -DAPR_DIR=$(APR_DIR) -DCUNIT_DIR=$(CUNIT_DIR) -DZLOG_DIR=$(ZLOG_DIR) \
        -DCMAKE_C_FLAGS="$(CFLAGS)" -DCMAKE_CXX_FLAGS="$(CFLAGS)" -C cmake_config.cmake -B$(CUNIT_OUTPUT_DIR) -H../cunit_tests

all_cunit: bootstrap_cunit
	@echo "Building CUNIT $(ECOA_FRAMEWORK)"
	@make --no-print-directory -C $(CUNIT_OUTPUT_DIR) all

clean_cunit:
	@echo "Cleaning CUNIT $(ECOA_FRAMEWORK)"
	@make --no-print-directory -C $(CUNIT_OUTPUT_DIR) clean

distclean_cunit:
	@echo "Dist cleaning CUNIT $(ECOA_FRAMEWORK)"
	@rm -rf $(CUNIT_OUTPUT_DIR) ../cunit_tests/CUnitAutomated-*.xml

run_cunit: all_cunit
	@echo "Running CUNIT $(ECOA_FRAMEWORK)"
	@make --no-print-directory -C $(CUNIT_OUTPUT_DIR) run

#
#  ECOA application
#
generate_ecoa:
	@echo "Generating ECOA $(ECOA_PROJECT) app" && \
	mkdir -p $(ECOA_PROJECT_XML_DIR) && \
	cp -pr $(APPS_DIR)/$(ECOA_PROJECT)/* $(ECOA_PROJECT_XML_DIR) && \
	ecoa-ldp -v3 -k ecoa-exvt -p $(ECOA_PROJECT_XML_DIR)/$(ECOA_PROJECT_XML_NAME).project.xml -u $(ECOA_USERID)

bootstrap_ecoa: generate_ecoa
	@echo "Bootstrapping ECOA $(ECOA_PROJECT) app"
	@cmake3 -DLOG4CPLUS_DIR=$(LOG4CPLUS_DIR) -DAPR_DIR=$(APR_DIR) -DZLOG_DIR=$(ZLOG_DIR) \
            -C cmake_config.cmake $(ECOA_OUTPUT_DIR)/CMakeLists.txt

all_ecoa: bootstrap_ecoa
	@echo "Building ECOA $(ECOA_PROJECT) app"
	@make --no-print-directory -C $(ECOA_OUTPUT_DIR) all

clean_ecoa:
	@echo "Cleaning ECOA $(ECOA_PROJECT) app"
	@make --no-print-directory -C $(ECOA_OUTPUT_DIR) clean

distclean_ecoa:
	@echo "Dist cleaning ECOA $(ECOA_PROJECT) app"
	@rm -rf $(ECOA_PROJECT_XML_DIR)

run_ecoa: all_ecoa
	@echo "Running ECOA $(ECOA_PROJECT) app"
	@make --no-print-directory -C $(ECOA_OUTPUT_DIR) run

build_docker: all_ecoa
	@echo "Building docker container for ECOA $(ECOA_PROJECT) app"
	@mkdir -p $(ECOA_OUTPUT_DIR)/deps && cp -rp $(ECOA_DEPS_DIR)/lib $(ECOA_OUTPUT_DIR)/deps
	@docker build -t $(ECOA_CONTAINER_NAME) --build-arg builddir=$(ECOA_OUTPUT_DIR) .

run_docker: build_docker
	@echo "Running docker container for ECOA $(ECOA_PROJECT) app"
	@mkdir -p $(ECOA_CONTAINER_LOGS)
	@docker run --network=host --rm -d -v $(PWD)/$(ECOA_CONTAINER_LOGS):/usr/local/bin/logs -u $(shell id -u ${USER}):$(shell id -g ${USER}) --name $(ECOA_CONTAINER_NAME) $(ECOA_CONTAINER_NAME)

#
#  Functionnal tests
#
run_fmk_tests:
	@echo "Running LDP Functionnal Test in $(ECOA_FMK_TESTS)"
	@mkdir -p $(ECOA_FMK_TESTS)
	@fmk-tests -i $(FMK_TESTS_DIR) -d $(APPS_DIR) -o $(ECOA_FMK_TESTS)/outputs -r $(ECOA_FMK_TESTS)/reports

clean_fmk_tests:
	@echo "Cleaning LDP $(ECOA_FMK_TESTS)"
	@rm -rf $(ECOA_FMK_TESTS)

all: all_cunit

clean: clean_cunit

distclean:
	@echo "Dist cleaning ECOA $(OUTPUT_DIR)"
	@rm -rf $(OUTPUT_DIR) ../cunit_tests/CUnitAutomated-*.xml

run: run_cunit

.PHONY: bootstrap_cunit all_cunit clean_cunit distclean_cunit run_cunit all bootstrap_ecoa all_ecoa clean_ecoa distclean_ecoa run_ecoa

