/*
 *  Zed Camera Grabber (ZCG)
 *  Copyright 2016 Andrea Pennisi
 *
 *  This file is part of ZCG and it is distributed under the terms of the
 *  GNU Lesser General Public License (Lesser GPL)
 *
 *
 *
 *  ZCG is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU Lesser General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  AT is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU Lesser General Public License for more details.
 *
 *  You should have received a copy of the GNU Lesser General Public License
 *  along with ZCG.  If not, see <http://www.gnu.org/licenses/>.
 *
 *
 *  ZCG has been written by Andrea Pennisi
 *
 *  Please, report suggestions/comments/bugs to
 *  andrea.pennisi@gmail.com
 *
 */

#include "ImageGrabber.h"

using namespace ZedGrabber;

ImageGrabber::ImageGrabber(const RESOLUTION& resolution, const int& confidence, const int& exposure)
    : ConfidenceIdx(confidence)
{
    // zedCamera = std::shared_ptr<sl::Camera>(new sl::Camera());
    zedCamera = std::make_shared<sl::Camera> ();


    // Set configuration parameters
    InitParameters init_params;
    init_params.camera_resolution = resolution;
    init_params.depth_mode = DEPTH_MODE_PERFORMANCE;
    init_params.coordinate_units = UNIT_METER;

    // Open the camera
    ERROR_CODE err = zedCamera->open ( init_params );
    if ( err != SUCCESS ) {
        printf ( "%s\n", errorCode2str ( err ).c_str () );
        zedCamera->close ();
        exit ( -1 );; // Quit if an error occurred
    }

    width = zedCamera->getResolution().width;
    height = zedCamera->getResolution ().height;

    zedCamera->retrieveMeasure ( _depth, MEASURE_DEPTH ); // Get the pointer


    // the depth is limited to 20. METERS as define in zed::init()
    // zedCamera->setDepthClampValue(10000);

    //Jetson only. Execute the calling thread on core 2
    //sl::zed::Camera::sticktoCPUCore(4);

    // sl::zed::ZED_SELF_CALIBRATION_STATUS old_self_calibration_status = sl::zed::SELF_CALIBRATION_NOT_CALLED;
    zedCamera->setCameraSettings(sl::CAMERA_SETTINGS_EXPOSURE, exposure);

    // Set runtime parameters after opening the camera
    runtime_parameters.sensing_mode = SENSING_MODE_STANDARD;


    // To share data between sl::Mat and cv::Mat, use slMat2cvMat()
    // Only the headers and pointer to the sl::Mat are copied, not the data itself
    _image_zed = Mat ( zedCamera->getResolution (), MAT_TYPE_8U_C4 );
    m_frame = slMat2cvMat ( _image_zed );

    _depth_image_zed = Mat ( zedCamera->getResolution (), MAT_TYPE_8U_C4 );
    m_depth = slMat2cvMat ( _depth_image_zed );

    // m_frame = cv::Mat::zeros(height, width, CV_8UC4);
    // m_depth = cv::Mat::zeros(height, width, CV_8UC4);    
}

bool ImageGrabber::finish()
{
  return true;
}

/**
* Conversion function between sl::Mat and cv::Mat
**/
cv::Mat ImageGrabber::slMat2cvMat ( Mat& input ) {
    // Mapping between MAT_TYPE and CV_TYPE
    int cv_type = -1;
    switch ( input.getDataType () ) {
    case MAT_TYPE_32F_C1: cv_type = CV_32FC1; break;
    case MAT_TYPE_32F_C2: cv_type = CV_32FC2; break;
    case MAT_TYPE_32F_C3: cv_type = CV_32FC3; break;
    case MAT_TYPE_32F_C4: cv_type = CV_32FC4; break;
    case MAT_TYPE_8U_C1: cv_type = CV_8UC1; break;
    case MAT_TYPE_8U_C2: cv_type = CV_8UC2; break;
    case MAT_TYPE_8U_C3: cv_type = CV_8UC3; break;
    case MAT_TYPE_8U_C4: cv_type = CV_8UC4; break;
    default: break;
    }

    // Since cv::Mat data requires a uchar* pointer, we get the uchar1 pointer from sl::Mat (getPtr<T>())
    // cv::Mat and sl::Mat will share a single memory structure
    return cv::Mat ( input.getHeight (), input.getWidth (), cv_type, input.getPtr<sl::uchar1> ( MEM_CPU ) );
}


bool ImageGrabber::getData()
{
    // DisparityMap filtering
    zedCamera->setConfidenceThreshold(ConfidenceIdx);

    //bool res = zedCamera->grab(dm_type);
	  

    if(/*!res*/ zedCamera->grab( runtime_parameters) == SUCCESS )
    {
        zedCamera->retrieveMeasure ( _depth, MEASURE_DEPTH );
        zedCamera->retrieveImage ( _image_zed, VIEW_LEFT);
        zedCamera->retrieveImage ( _depth_image_zed, VIEW_DEPTH );

        cv::Mat depth32bit = slMat2cvMat ( _depth );
        depth32bit.convertTo(m_depth16bit, CV_16UC1);
    }

    return true;
}
