"""
Code snippets for ZED Restful API with Flask
"""

from ZEDCamera import ZEDCamera

from flask import Flask, jsonify

app = Flask("Restful_ZED")

@app.route('/')
def index():
    info = "This is the Restful API of ZED! '/grab/images' for grabing RGB*2+Depth*1 images and return names"

    return jsonify({'HowTo': info})

@app.route('/grab/images', methods=['GET'])
def get_images():
    R_ZED.grab_rgb_and_depth(pre_grab=True) # I have no idea, but, it seems we need grab twice ...
    im_names = R_ZED.grab_rgb_and_depth()[0]
    return jsonify({'image_names': im_names})

@app.route('/camera_info', methods=['GET'])
def camera_info():
    K1, K2 = R_ZED.get_camera_parameters()
    return jsonify({'K1': K1, 'K2':K2})

@app.route('/available', methods=['GET'])
def available():
    return jsonify({'available': R_ZED.available()})

# @app.route('/stop', methods=['GET'])
# def stop():
#     R_ZED.stop()
#     return jsonify({'Stop': True})




if __name__ == '__main__':
    R_ZED = ZEDCamera(write2disk=True)
    # app.run(debug=True)
    app.run(host='0.0.0.0')
