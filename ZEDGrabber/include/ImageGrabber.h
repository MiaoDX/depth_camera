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

#ifndef _IMAGEGRABBER_H_
#define _IMAGEGRABBER_H_

#include "Grabber.h"

//ZED Includes
//#include <zed/Camera.hpp>
//#include <zed/utils/GlobalDefine.hpp>

#include <sl/Camera.hpp>
//#include <sl/utils/GlobalDefine.hpp>

// 
//C++
#include <iostream>
#include <memory>
#include <chrono>
#include <thread>
#include <mutex>
#include <future>
#include <functional>
#include <queue>
#include <fstream>
#include "mycvmat.h"

namespace ZedGrabber {
  
    using namespace sl;
    using namespace std::chrono;

    class ImageGrabber : public Grabber
    {
        public:
            ImageGrabber (const RESOLUTION& resolution=sl::RESOLUTION_HD720, const int& confidence=70, const int& exposure=40);
            ImageGrabber () { ; }
            virtual bool getData();
            virtual bool finish();
        private:
            std::shared_ptr<sl::Camera> zedCamera;
            RuntimeParameters runtime_parameters;
            std::string name_;
            sl::Mat _depth;
            sl::Mat _image_zed;
            sl::Mat _depth_image_zed;

            int ConfidenceIdx;
	private:
      cv::Mat slMat2cvMat ( Mat& input );
    };
}

#endif
