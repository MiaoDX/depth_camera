"""
A relatively simple speed benchmark for grabbing images (and showing it) via python and its Restful API
Note that the speed is also related to the USB version (USB3 will be quicker that USB2)
"""

from ZEDCamera import ZEDCamera
import time
import cv2

def direct(write2disk=False, show=False):

    R_ZED = ZEDCamera(write2disk=write2disk)

    start = time.time()

    n = 100

    for i in range(n):
        im_names, rgb_image, depth_image = R_ZED.grab_rgb_and_depth()
        if show:
            cv2.imshow('1', rgb_image)
            cv2.imshow('2', depth_image)
            cv2.waitKey(1)

    etime = time.time() - start

    R_ZED.stop()

    print("elapsed time:{}".format(etime))
    print("Ave {} fps".format(n/etime))

def restful(show=False):

    from ZED_Client import ZED_Client

    zed_client = ZED_Client()

    zed_client.check_available()

    zed_client.generate_cmd_and_parse_response('/')

    zed_client.get_camera_info()

    # zed_client.get_and_show_ims()


    start = time.time()

    n = 100

    for i in range(n):
        im_names_json = zed_client.get_im_names()
        # im_names = [im_names_json['left_file'], im_names_json['right_file'], im_names_json['left_depth_file']]
        # zed_client.download_ims(im_names)
        if show:
            rgb_image = cv2.imread(im_names_json['left_file'])
            depth_image = cv2.imread(im_names_json['left_depth_file'], cv2.IMREAD_UNCHANGED)
            cv2.imshow('1', rgb_image)
            cv2.imshow('2', depth_image)
            cv2.waitKey(1)

    etime = time.time() - start

    print("elapsed time:{}".format(etime))
    print("Ave {} fps".format(n / etime))


if __name__ == '__main__':

    direct(write2disk=False) # 16.47
    # direct(write2disk=False, show=True) # 12.633
    # direct(write2disk=True) #  4.8978 fps
    # direct(write2disk=True, show=True)  # 4.77 fps

    # restful() # 4.1403
    # restful(show=True)  # 3.21