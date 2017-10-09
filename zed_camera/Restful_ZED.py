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

class Restful_ZED(object):

    def __init__(self):
        # Create a PyZEDCamera object
        self.zed = zcam.PyZEDCamera()

        # Create a PyInitParameters object and set configuration parameters
        init_params = zcam.PyInitParameters()
        # init_params.camera_resolution = sl.PyRESOLUTION.PyRESOLUTION_HD1080  # Use HD1080 video mode
        init_params.camera_resolution = sl.PyRESOLUTION.PyRESOLUTION_HD720
        init_params.camera_fps = 10  # 30 is default

        # init_params.enable_right_side_measure = True

        init_params.depth_mode = sl.PyDEPTH_MODE.PyDEPTH_MODE_QUALITY

        init_params.coordinate_units = sl.PyUNIT.PyUNIT_MILLIMETER
        init_params.depth_minimum_distance = 300 # 300mm, 30cm

        # If the matched points are too small, we can embrace this to add more points in depth image
        self.runtime_parameters = zcam.PyRuntimeParameters()
        # runtime_parameters.sensing_mode = sl.PySENSING_MODE.PySENSING_MODE_FILL

        self.work_dir = os.path.split(os.path.realpath(__file__))[0] + "/Restful_ZED"
        if not os.path.exists(self.work_dir):
            os.mkdir(self.work_dir)

        self._start(init_params)

        self._serve_the_images()

        self.image_mat = core.PyMat() # the image mat, useful for all capturing

        self.im_num = 0

        self.left_file = ""
        self.right_file = ""
        self.left_depth_file = ""
        self.left_depth_show_file = ""


        print("Init done")

    def _start(self, init_params):
        # Open the camera
        err = self.zed.open(init_params)
        if err != tp.PyERROR_CODE.PySUCCESS:
            print("We failed to open the ZED camera, exit!")
            exit(1)


    def _serve_the_images(self):
        """
        https://eli.thegreenplace.net/2017/interacting-with-a-long-running-child-process-in-python/
        """
        print("Going to serve the images ...")


        import http.server
        import socketserver
        PORT = 8001

        web_dir = os.path.join(self.work_dir)
        os.chdir(web_dir)

        """
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print("serving files at port", PORT)

            from threading import Thread
            Thread(target=httpd.serve_forever).start()
        """
        self.proc = subprocess.Popen(['python', '-u', '-m', 'http.server', str(PORT)],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)

        print("serving files at port", PORT)

    def available(self):
        return self.zed.is_zed_connected() and self.zed.is_opened()

    def stop(self):
        self.zed.close()
        # self.httpd.shutdown()

        print("Going to terminate file server")
        self.proc.terminate()
        try:
            outs, _ = self.proc.communicate(timeout=0.2)
            # We'll see it exiting with -15 which means killed by SIGTERM
            print('== subprocess exited with rc =', self.proc.returncode)
            print(outs.decode('utf-8'))
        except subprocess.TimeoutExpired:
            print('subprocess did not terminate in time')



        pass


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

        self.left_file = self.file_name_no_suffix + '.jpg'
        self.right_file = self.file_name_no_suffix + '_right.jpg'
        self.left_depth_file = self.file_name_no_suffix + '_depth.png'
        self.left_depth_view_file = self.file_name_no_suffix + "_depth_view.png"

    def _get_images_names(self):
        # return [self.left_file, self.right_file, self.left_depth_file]
        return {"left_file":self.left_file, "right_file":self.right_file, "left_depth_file":self.left_depth_file}


    def grab_rgb_and_depth(self, save=True):

        # Grab once, a PyRuntimeParameters object must be given to grab()
        if not self.zed.grab(self.runtime_parameters) == tp.PyERROR_CODE.PySUCCESS:
            print("Seems we failed to grab images")
            self._assign_image_names(False)
            return self._get_images_names()

        time.sleep(0.5)  # make sure will have enough time for new capturing

        if save == False:
            return

        self.im_num += 1
        self._assign_image_names(True)

        print("Going to retrieve images: {} ...".format(self.file_name_no_suffix))

        self.zed.retrieve_image(self.image_mat, sl.PyVIEW.PyVIEW_LEFT)
        cv2.imwrite(self.left_file, self.image_mat.get_data())

        self.zed.retrieve_image(self.image_mat, sl.PyVIEW.PyVIEW_RIGHT)
        cv2.imwrite(self.right_file, self.image_mat.get_data())

        self.zed.retrieve_image(self.image_mat, sl.PyVIEW.PyVIEW_DEPTH)
        cv2.imwrite(self.left_depth_view_file, self.image_mat.get_data())

        
        self.zed.retrieve_measure(self.image_mat, sl.PyMEASURE.PyMEASURE_DEPTH)
        # zcam.save_mat_depth_as(self.image_mat, sl.PyDEPTH_FORMAT.PyDEPTH_FORMAT_PNG, self.left_depth_file[:-4] + '_zed.png')
        im_measure = np.uint16(self.image_mat.get_data())
        cv2.imwrite(self.left_depth_file, im_measure)




        print("Get images done")
        return self._get_images_names()

    def run(self):
        pass


def test_grab():
    R_ZED = Restful_ZED()

    for i in range(1):
        R_ZED.grab_rgb_and_depth()


    R_ZED.stop()


def test_info():
    R_ZED = Restful_ZED()

    R_ZED.get_camera_parameters()


    time.sleep(2)

    R_ZED.stop()






if __name__ == "__main__":

    # test_grab()
    test_info()
