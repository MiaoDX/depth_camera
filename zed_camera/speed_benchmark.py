"""
A relatively simple speed benchmark for grabbing images (and showing it) via python and its Restful API
Note that the speed is also related to the USB version (USB3 will be quicker that USB2)
"""

from Restful_ZED import Restful_ZED
import time

def direct():

    R_ZED = Restful_ZED()

    start = time.time()

    n = 50

    for i in range(n):
        R_ZED.grab_rgb_and_depth()
        # time.sleep(0.001)
        pass

    etime = time.time() - start

    R_ZED.stop()

    print("elapsed time:{}".format(etime))
    print("Ave {} fps".format(n/etime))

def restful():

    from ZED_Client import ZED_Client

    zed_client = ZED_Client()

    zed_client.check_available()

    zed_client.generate_cmd_and_parse_response('/')

    zed_client.get_camera_info()

    # zed_client.get_and_show_ims()


    start = time.time()

    n = 50

    for i in range(n):
        im_names_json = zed_client.get_im_names()
        # im_names = [im_names_json['left_file'], im_names_json['right_file'], im_names_json['left_depth_file']]
        # zed_client.download_ims(im_names)

    etime = time.time() - start

    print("elapsed time:{}".format(etime))
    print("Ave {} fps".format(n / etime))


if __name__ == '__main__':

    # direct()

    restful()