cmake_minimum_required(VERSION 3.16)

project(DualEloRating LANGUAGES CXX)

include(FetchContent)

if (MSVC)
    # Use static MSVC runtime to align with statically linked Linux builds
    set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
endif()

set(DLIB_GIT_TAG v19.24 CACHE STRING "dlib tag to use")

FetchContent_Declare(
    dlib
    GIT_REPOSITORY https://github.com/davisking/dlib.git
    GIT_TAG        ${DLIB_GIT_TAG}
)
set(DLIB_NO_GUI_SUPPORT ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(dlib)

file(GLOB SRC CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp")

add_executable(DualEloRating ${SRC})
target_include_directories(DualEloRating PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(DualEloRating PRIVATE dlib::dlib)
target_compile_features(DualEloRating PRIVATE cxx_std_17)

if (CMAKE_SYSTEM_NAME STREQUAL "Linux")
    target_compile_options(DualEloRating PRIVATE -O2 -Wall)
    find_package(Threads REQUIRED)
    target_link_libraries(DualEloRating PRIVATE Threads::Threads)
elseif (WIN32)
    if (MINGW)
        target_compile_options(DualEloRating PRIVATE -O3 -march=native -msse4.2 -mfpmath=sse -Wall -flto)
        target_link_options(DualEloRating PRIVATE -s -flto -static -static-libgcc -static-libstdc++)
        target_link_libraries(DualEloRating PRIVATE -lwinpthread)
    elseif (MSVC)
        target_compile_options(DualEloRating PRIVATE /O2 /GL /fp:precise)
        target_link_options(DualEloRating PRIVATE /LTCG)
    endif()
elseif (APPLE)
    target_compile_options(DualEloRating PRIVATE -O3 -march=native -Wall)
endif()
