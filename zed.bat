set ZED_DIR=C:\Program Files (x86)\ZED SDK\

set ZED_SDK_ROOT_DIR=%ZED_DIR%
set OpenCV_DIR=%ZED_DIR%\dependencies\opencv_3.1.0
set ZED_INCLUDE_DIRS=%ZED_DIR%\include
set ZED_LIBRARIES_64=sl_zed64.lib;sl_core64.lib;sl_scanning64.lib
set ZED_LIBRARY_DIR=%ZED_DIR%\lib


set path=%path%;%ZED_DIR%\bin;%ZED_DIR%\dependencies\freeglut_2.8\x64;%ZED_DIR%\dependencies\glew-1.12.0\x64;%OpenCV_DIR%\x64\vc14\bin;