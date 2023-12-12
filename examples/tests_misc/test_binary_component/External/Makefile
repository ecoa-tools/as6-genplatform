CC=gcc
CXX=g++
CFLAGS= 
CXXFLAGS=

BIN_DIR =../4-ComponentImplementations/myConstellation/bin

all: $(BIN_DIR)/satellite_C.o $(BIN_DIR)/satellite_Cpp.o

$(BIN_DIR)/satellite_C.o: $(BIN_DIR) satellite_C/satellite_C.c
	$(CC) -g -std=c99 -DECOA_64BIT_SUPPORT $(CFLAGS) -o $(BIN_DIR)/satellite_C.o -Itypes/ -I satellite_C/ -c satellite_C/satellite_C.c

$(BIN_DIR)/satellite_Cpp.o: $(BIN_DIR) satellite_Cpp/satellite_Cpp.cpp
	$(CXX) -g -std=c++11 -DECOA_64BIT_SUPPORT $(CXXFLAGS) -o $(BIN_DIR)/satellite_Cpp.o -Itypes/ -I satellite_Cpp/ -c satellite_Cpp/satellite_Cpp.cpp

$(BIN_DIR):
	@mkdir $(BIN_DIR)

clean:
	@echo "Cleaning $(BIN_DIR)"
	@rm -rf $(BIN_DIR)
