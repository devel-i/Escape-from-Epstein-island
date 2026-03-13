cmake_minimum_required(VERSION 3.16)
project(escape_island_c C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

find_package(raylib REQUIRED)

add_executable(escape_island main.c)
target_link_libraries(escape_island PRIVATE raylib)

if (WIN32)
  target_link_libraries(escape_island PRIVATE winmm gdi32 opengl32)
endif()
