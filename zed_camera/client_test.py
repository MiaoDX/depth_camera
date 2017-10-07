"""
A http client, call the flask APP
"""

import requests
import cv2
import numpy as np

def generate_cmd_and_parse_response(cmd=''):
    if cmd[0] == '/':
        cmd = cmd[1:]
    r = requests.get('http://127.0.0.1:5000/' + cmd)
    assert r.status_code == 200
    assert r.headers['content-type'] == "application/json"
    print(r.json())
    return r.json()


def show_ims(im_files):
    for im_file in im_files:
        im = cv2.imread(im_file)
        cv2.imshow(im_file, im)
        cv2.waitKey(0)


def get_camera_info():
    r_json = generate_cmd_and_parse_response('/camera_info')
    K1 = np.array(r_json['K1']).reshape(3,3)
    K2 = np.array(r_json['K2']).reshape(3, 3)
    print("K1:\n{}\nK2:\n{}".format(K1, K2))


def get_and_show_ims():
    r_json = generate_cmd_and_parse_response('/grab/images')
    im_names = r_json['image_names']
    show_ims(im_names)

if __name__ == "__main__":

    generate_cmd_and_parse_response('/')

    get_camera_info()

    get_and_show_ims()