"""
A minimal restful interface for ZED
Grab RGB*2+Depth*2 images
"""


import pyzed.camera as zcam
import pyzed.defines as sl
import pyzed.types as tp
import pyzed.core as core
import cv2
import os
import sys

import numpy as np
import time
import subprocess

from CameraBase import CameraCalibration, CameraBase
from pytypes import override

class Restful_ZED(CameraBase):

    def __init__(self, write2disk=False):

        self.write2dist = write2disk

        # Create a PyZEDCamera object
        self.zed = zcam.PyZEDCamera()

        # Create a PyInitParameters object and set configuration parameters
        init_params = zcam.PyInitParameters()
        # init_params.camera_resolution = sl.PyRESOLUTION.PyRESOLUTION_HD1080  # Use HD1080 video mode
        init_params.camera_resolution = sl.PyRESOLUTION.PyRESOLUTION_HD720
        # init_params.camera_fps = 10  # 30 is default

        # init_params.enable_right_side_measure = True

        init_params.depth_mode = sl.PyDEPTH_MODE.PyDEPTH_MODE_QUALITY

        init_params.coordinate_units = sl.PyUNIT.PyUNIT_MILLIMETER
        init_params.depth_minimum_distance = 300 # 300mm, 30cm

        # If the matched points are too small, we can embrace this to add more points in depth image
        self.runtime_parameters = zcam.PyRuntimeParameters()
        # runtime_parameters.sensing_mode = sl.PySENSING_MODE.PySENSING_MODE_FILL


        if self.write2dist:
            self.work_dir = os.path.split(os.path.realpath(__file__))[0] + "/Restful_ZED/" + time.strftime("%Y%m%d_%H%M", time.localtime())
            print("Work Dir:{}".format(self.work_dir))
            if not os.path.exists(self.work_dir):
                os.mkdir(self.work_dir)

            self._serve_the_images()

        self._start(init_params) # where to start the camera is not so clear


        self.image_mat = core.PyMat() # the image mat, useful for all capturing

        self.im_num = 0

        self.left_file = ""
        self.right_file = ""
        self.left_depth_file = ""
        self.left_depth_show_file = ""


        K1, K2 = self.get_camera_parameters()
        K1 = np.array(K1).astype(np.float32).reshape(3, 3)
        K2 = np.array(K2).astype(np.float32).reshape(3, 3)

        super(Restful_ZED, self).__init__(cameraCalibration = CameraCalibration(leftK=K1, rightK=K2))

        print("Init done")

    def _start(self, init_params):
        # Open the camera
        if self.available():
            return True

        err = self.zed.open(init_params)
        if err != tp.PyERROR_CODE.PySUCCESS:
            print("We failed to open the ZED camera, exit!")
            # exit(1)
            return False

        return True

    def _serve_the_images(self):
        """
        https://eli.thegreenplace.net/2017/interacting-with-a-long-running-child-process-in-python/
        """
        print("Going to serve the images ...")

        PORT = 8001
        web_dir = os.path.join(self.work_dir)
        os.chdir(web_dir)

        self.proc = subprocess.Popen(['python', '-u', '-m', 'http.server', str(PORT)],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)

        print("serving files at port", PORT)

    def available(self):
        return self.zed.is_zed_connected() and self.zed.is_opened()

    def stop(self):
        self.zed.close()

        if self.write2dist:
            print("Going to terminate file server")
            self.proc.terminate()
            try:
                outs, _ = self.proc.communicate(timeout=0.2)
                # We'll see it exiting with -15 which means killed by SIGTERM
                print('== subprocess exited with rc =', self.proc.returncode)
                print(outs.decode('utf-8'))
            except subprocess.TimeoutExpired:
                print('subprocess did not terminate in time')
                return False

        return True


    def get_camera_parameters(self):
        info = core.PyCameraInformation(self.zed, self.zed.get_resolution())
        print("serial num:{}".format(info.serial_number))
        print("firmware_version:{}".format(info.firmware_version))
        py_calib = info.calibration_parameters
        print("R\n:{}".format(py_calib.R))
        print("t\n:{}".format(py_calib.T))

        cam_1 = py_calib.left_cam
        K1 = [cam_1.fx, 0, cam_1.cx,  0, cam_1.fy, cam_1.cy, 0, 0, 1]
        print("K left:{}".format(K1))

        cam_2 = py_calib.right_cam
        K2 = [cam_2.fx, 0, cam_2.cx, 0, cam_2.fy, cam_2.cy, 0, 0, 1]
        print("K right:{}".format(K2))

        return K1, K2

    def _assign_image_names(self, grab_ok=True):

        if not grab_ok:
            self.left_file = ""
            self.right_file = ""
            self.left_depth_file = ""
            self.left_depth_show_file = ""
            return

        time_str = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        self.file_name_no_suffix = "{save_dir}/{time_str}_{im_num}".format(save_dir=self.work_dir,
                                                                                 time_str=time_str, im_num=self.im_num)

        # self.left_file = self.file_name_no_suffix + '.jpg'
        # self.right_file = self.file_name_no_suffix + '_right.jpg'
        self.left_file = self.file_name_no_suffix + '.png'
        self.right_file = self.file_name_no_suffix + '_right.png'
        self.left_depth_file = self.file_name_no_suffix + '_depth.png'
        self.left_depth_view_file = self.file_name_no_suffix + "_depth_view.png"

    def _get_images_names(self):
        # return [self.left_file, self.right_file, self.left_depth_file]
        return {"left_file":self.left_file, "right_file":self.right_file, "left_depth_file":self.left_depth_file}


    def grab_rgb_and_depth(self, pre_grab=False): # it seem that the first grab is somewhat wrong, grab twice to make sure it is ok

        # Grab once, a PyRuntimeParameters object must be given to grab()
        if not self.zed.grab(self.runtime_parameters) == tp.PyERROR_CODE.PySUCCESS:
            print("Seems we failed to grab images")
            self._assign_image_names(False)
            return self._get_images_names()

        time.sleep(0.5)  # make sure will have enough time for new capturing

        if pre_grab == False:
            return

        self.im_num += 1
        self._assign_image_names(True)

        print("Going to retrieve images: {} ...".format(self.file_name_no_suffix))

        self.zed.retrieve_image(self.image_mat, sl.PyVIEW.PyVIEW_LEFT)
        im_left = self.image_mat.get_data()

        self.zed.retrieve_image(self.image_mat, sl.PyVIEW.PyVIEW_RIGHT)
        im_right = self.image_mat.get_data()

        self.zed.retrieve_image(self.image_mat, sl.PyVIEW.PyVIEW_DEPTH)
        im_depth_view = self.image_mat.get_data()

        self.zed.retrieve_measure(self.image_mat, sl.PyMEASURE.PyMEASURE_DEPTH)
        # zcam.save_mat_depth_as(self.image_mat, sl.PyDEPTH_FORMAT.PyDEPTH_FORMAT_PNG, self.left_depth_file[:-4] + '_zed.png')
        im_measure = np.uint16(self.image_mat.get_data())


        if self.write2dist:
            cv2.imwrite(self.left_file, im_left)
            cv2.imwrite(self.right_file, im_right)
            cv2.imwrite(self.left_depth_view_file, im_depth_view)
            cv2.imwrite(self.left_depth_file, im_measure)




        print("Get images done")
        return self._get_images_names(), im_left, im_measure

    def run(self):
        pass


    @override
    def open(self) -> bool:
        return self._start(self.runtime_parameters)

    @override
    def close(self) -> bool:
        return self.stop()

    @override
    def getImage(self) -> (np.ndarray, np.ndarray):
        self.grab_rgb_and_depth(pre_grab=True) # grab first
        im_names, rgb_image, depth_image = self.grab_rgb_and_depth()
        return rgb_image, depth_image

    @override
    def getParameters(self) -> dict:
        return {}

    @override
    def setParameters(self, params : dict) -> bool:
        return False


def test_grab(write2disk=False):
    R_ZED = Restful_ZED(write2disk)

    R_ZED.open()

    for i in range(1):
        R_ZED.grab_rgb_and_depth()

    R_ZED.close()


def test_info():
    R_ZED = Restful_ZED()

    R_ZED.open()

    R_ZED.get_camera_parameters()

    time.sleep(2)

    R_ZED.close()



if __name__ == "__main__":

    test_grab(write2disk=False)
    # test_grab(write2disk=True)
    # test_info()
