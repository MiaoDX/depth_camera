project(zedsimplegrabber)

SET(execName grabber)

CMAKE_MINIMUM_REQUIRED(VERSION 2.8)

set(CMAKE_CXX_FLAGS "-std=c++11 -g -O3")

SET(VERSION_REQ_CUDA "8.0")

#find_package(ZED REQUIRED)

##For Jetson, OpenCV4Tegra is based on OpenCV2.4
#exec_program(uname ARGS -p OUTPUT_VARIABLE CMAKE_SYSTEM_NAME2)

#set(CUDA_USE_STATIC_CUDA_RUNTIME OFF)

find_package(OpenCV REQUIRED)

IF(WIN32) # Windows
    if (CMAKE_CL_64)  
        SET(ZED_INCLUDE_DIRS $ENV{ZED_INCLUDE_DIRS})
        SET(ZED_LIBRARIES $ENV{ZED_LIBRARIES_64})
        SET(ZED_LIBRARY_DIR $ENV{ZED_LIBRARY_DIR})
    else()
        message(FATAL_ERROR "You've selected the 32bit version of ${CMAKE_GENERATOR}. \n Please delete the cache (file->Delete Cache) and use the 64bit version. (${CMAKE_GENERATOR} Win64)")
    endif()
ELSE() # Linux
    find_package(ZED REQUIRED)
    add_definitions(-Wno-format-extra-args)
    SET(SPECIAL_OS_LIBS "pthread" "X11")
ENDIF(WIN32)



find_package(CUDA ${VERSION_REQ_CUDA} REQUIRED)
include_directories(${CUDA_INCLUDE_DIRS})
include_directories(${ZED_INCLUDE_DIRS})
include_directories(${OpenCV_INCLUDE_DIRS})
include_directories(${PROJECT_BINARY_DIR}/include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

link_directories(${ZED_LIBRARY_DIR})
link_directories(${OpenCV_LIBRARY_DIRS})
link_directories(${CUDA_LIBRARY_DIRS})

SET(SRC_FOLDER src)
SET(EXECUTABLE_OUTPUT_PATH ../bin)

#FILE(GLOB_RECURSE SRC_FILES "${SRC_FOLDER}/*.cpp")
FILE(GLOB_RECURSE SRC_FILES "${SRC_FOLDER}/main.cpp" "${SRC_FOLDER}/ImageGrabber.cpp" "${SRC_FOLDER}/mosaic.cpp")

add_executable(${execName} ${SRC_FILES})

#add_definitions(-std=c++0x -g -O3)

TARGET_LINK_LIBRARIES( ${execName}
                         -lm -lpthread ${ZED_LIBRARIES}
                        ${OpenCV_LIBRARIES}
			${CUDA_CUDA_LIBRARY} ${CUDA_CUDART_LIBRARY} ${CUDA_npp_LIBRARY} 
                        )


#set(SOURCE_FILES src/main.cpp)
add_executable(${PROJECT_NAME} src/main2.cpp)
set_target_properties(${PROJECT_NAME} PROPERTIES VS_DOTNET_TARGET_FRAMEWORK_VERSION "v4.6")
set_target_properties(${PROJECT_NAME} PROPERTIES VS_DOTNET_REFERENCES "System")
set_target_properties(${PROJECT_NAME} PROPERTIES COMPILE_FLAGS "/clr /EHa")
string(REGEX REPLACE "/RTC(su|[1su])" "" CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")
string(REGEX REPLACE "/RTC(su|[1su])" "" CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG}")

TARGET_LINK_LIBRARIES(myproject)