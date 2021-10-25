cmake_minimum_required(VERSION 3.16)
project(test1)

set(CMAKE_CXX_STANDARD 11)

set(libConchCV main.cpp )
include_directories(./)

# ADD_DEFINITIONS(
# -O3 -g -W -Wall -Wl,-rpath=./)

add_library(ConchCV ${libConchCV})
#add_library(ConchCV HPS3DUser_IF.c)
link_directories(./)
add_executable(test1 main.cpp HPS3DUser_IF.h HPS3DUser_IF.c HPS3DBase_IF.h)

target_link_libraries(${PROJECT_NAME} HPS3DSDK)