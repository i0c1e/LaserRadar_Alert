# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.21

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Disable VCS-based implicit rules.
% : %,v

# Disable VCS-based implicit rules.
% : RCS/%

# Disable VCS-based implicit rules.
% : RCS/%,v

# Disable VCS-based implicit rules.
% : SCCS/s.%

# Disable VCS-based implicit rules.
% : s.%

.SUFFIXES: .hpux_make_needs_suffix_list

# Command-line flag to silence nested $(MAKE).
$(VERBOSE)MAKESILENT = -s

#Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/charles/code/test1

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/charles/code/test1/build

# Include any dependencies generated for this target.
include CMakeFiles/test1.dir/depend.make
# Include any dependencies generated by the compiler for this target.
include CMakeFiles/test1.dir/compiler_depend.make

# Include the progress variables for this target.
include CMakeFiles/test1.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/test1.dir/flags.make

CMakeFiles/test1.dir/main.cpp.o: CMakeFiles/test1.dir/flags.make
CMakeFiles/test1.dir/main.cpp.o: ../main.cpp
CMakeFiles/test1.dir/main.cpp.o: CMakeFiles/test1.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/charles/code/test1/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object CMakeFiles/test1.dir/main.cpp.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/test1.dir/main.cpp.o -MF CMakeFiles/test1.dir/main.cpp.o.d -o CMakeFiles/test1.dir/main.cpp.o -c /home/charles/code/test1/main.cpp

CMakeFiles/test1.dir/main.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/test1.dir/main.cpp.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/charles/code/test1/main.cpp > CMakeFiles/test1.dir/main.cpp.i

CMakeFiles/test1.dir/main.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/test1.dir/main.cpp.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/charles/code/test1/main.cpp -o CMakeFiles/test1.dir/main.cpp.s

CMakeFiles/test1.dir/HPS3DUser_IF.c.o: CMakeFiles/test1.dir/flags.make
CMakeFiles/test1.dir/HPS3DUser_IF.c.o: ../HPS3DUser_IF.c
CMakeFiles/test1.dir/HPS3DUser_IF.c.o: CMakeFiles/test1.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/charles/code/test1/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Building C object CMakeFiles/test1.dir/HPS3DUser_IF.c.o"
	/usr/bin/x86_64-pc-linux-gnu-gcc-11.1.0 $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -MD -MT CMakeFiles/test1.dir/HPS3DUser_IF.c.o -MF CMakeFiles/test1.dir/HPS3DUser_IF.c.o.d -o CMakeFiles/test1.dir/HPS3DUser_IF.c.o -c /home/charles/code/test1/HPS3DUser_IF.c

CMakeFiles/test1.dir/HPS3DUser_IF.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing C source to CMakeFiles/test1.dir/HPS3DUser_IF.c.i"
	/usr/bin/x86_64-pc-linux-gnu-gcc-11.1.0 $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -E /home/charles/code/test1/HPS3DUser_IF.c > CMakeFiles/test1.dir/HPS3DUser_IF.c.i

CMakeFiles/test1.dir/HPS3DUser_IF.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling C source to assembly CMakeFiles/test1.dir/HPS3DUser_IF.c.s"
	/usr/bin/x86_64-pc-linux-gnu-gcc-11.1.0 $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -S /home/charles/code/test1/HPS3DUser_IF.c -o CMakeFiles/test1.dir/HPS3DUser_IF.c.s

# Object files for target test1
test1_OBJECTS = \
"CMakeFiles/test1.dir/main.cpp.o" \
"CMakeFiles/test1.dir/HPS3DUser_IF.c.o"

# External object files for target test1
test1_EXTERNAL_OBJECTS =

test1: CMakeFiles/test1.dir/main.cpp.o
test1: CMakeFiles/test1.dir/HPS3DUser_IF.c.o
test1: CMakeFiles/test1.dir/build.make
test1: CMakeFiles/test1.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/home/charles/code/test1/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_3) "Linking CXX executable test1"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/test1.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/test1.dir/build: test1
.PHONY : CMakeFiles/test1.dir/build

CMakeFiles/test1.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/test1.dir/cmake_clean.cmake
.PHONY : CMakeFiles/test1.dir/clean

CMakeFiles/test1.dir/depend:
	cd /home/charles/code/test1/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/charles/code/test1 /home/charles/code/test1 /home/charles/code/test1/build /home/charles/code/test1/build /home/charles/code/test1/build/CMakeFiles/test1.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/test1.dir/depend

