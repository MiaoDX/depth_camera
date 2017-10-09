"""
A http client, call the flask APP
"""

import requests
import cv2
import numpy as np
import os



class ZED_Client(object):
    """
    The ZED client, call the flask APP and deal with download from the http.server
    """

    def __init__(self):
        self.rest_url = 'http://127.0.0.1:5000/'
        self.download_url = 'http://127.0.0.1:8001/'


    def generate_cmd_and_parse_response(self, cmd=''):
        if cmd[0] == '/':
            cmd = cmd[1:]

        r = requests.get(self.rest_url + cmd)
        assert r.status_code == 200
        assert r.headers['content-type'] == "application/json"
        print(r.json())
        return r.json()


    def check_available(self):
        r_json = self.generate_cmd_and_parse_response('/available')
        available = r_json['available']
        print("Status:{}".format(available))
        return available

    def stop(self):
        r_json = self.generate_cmd_and_parse_response('/stop')
        status = r_json['Stop']
        print("Status:{}".format(status))
        return status


    def get_camera_info(self):
        r_json = self.generate_cmd_and_parse_response('/camera_info')
        K1 = np.array(r_json['K1']).reshape(3, 3)
        K2 = np.array(r_json['K2']).reshape(3, 3)
        print("K1:\n{}\nK2:\n{}".format(K1, K2))
        return r_json


    def get_im_names(self):
        r_json = self.generate_cmd_and_parse_response('/grab/images')
        im_names_json = r_json['image_names']
        return im_names_json

    def show_ims(self, im_files):
        for im_file in im_files:
            im = cv2.imread(im_file)
            cv2.imshow(im_file, im)
            cv2.waitKey(0)

    def get_and_show_ims(self):
        im_names_json = self.get_im_names()
        im_names = [im_names_json['left_file'], im_names_json['right_file'], im_names_json['left_depth_file']]
        self.show_ims(im_names)


    def download_file(self, url_file='http://127.0.0.1/1.txt', save_file=''):
        from tqdm import tqdm
        import requests

        response = requests.get(url_file, stream=True)

        with open(save_file, "wb") as handle:
            for data in tqdm(response.iter_content()):
                handle.write(data)

    def download_im(self, im_name, save_dir='output'):

        print("\nGoing to download {} into folder {}\n".format(im_name, save_dir))

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        base_name = os.path.basename(im_name)
        save_name = os.path.join(save_dir, base_name)
        self.download_file(self.download_url+base_name, save_name)

        return save_name



    def download_ims(self, im_names, save_dir='output'):
        # im_names_json = get_im_names()
        # im_names = [im_names_json['left_file'], im_names_json['right_file'], im_names_json['left_depth_file']]

        im_names_save = []

        for name in im_names:
            im_names_save.append(self.download_im(name, save_dir))

        return im_names_save


if __name__ == "__main__":


    zed_client = ZED_Client()

    zed_client.check_available()

    zed_client.generate_cmd_and_parse_response('/')

    zed_client.get_camera_info()

    zed_client.get_and_show_ims()

    im_names_json = zed_client.get_im_names()
    im_names = [im_names_json['left_file'], im_names_json['right_file'], im_names_json['left_depth_file']]
    zed_client.download_ims(im_names)

    zed_client.download_im(im_names_json['left_file'], save_dir='output2')

