import abc
import numpy as np
import typing


class CameraCalibration(object):
    def __init__(self, leftK = np.array([[320, 0, 320], [0, 320, 240], [0, 0, 1]]),
                 rightK = np.array([[320, 0, 320], [0, 320, 240], [0, 0, 1]])):
        self.__leftK = leftK
        self.__rightK = rightK

    def getK(self):
        return self.__leftK.copy()

    def getLeftK(self):
        return self.__leftK.copy()

    def getRightK(self):
        return self.__rightK.copy()



class CameraBase(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, cameraCalibration = CameraCalibration()) -> None:
        self.cameraCalibration = cameraCalibration
        self.camera_settings_value = {'WHITEBALANCE': 4600, 'BRIGHTNESS': 4, 'CONTRAST': 4, 'EXPOSURE': 54, 'HUE': 0,
                                      'GAIN': 98, 'AUTO_WHITEBALANCE': 1, 'SATURATION': 4}

    def getCameraCalibration(self) -> CameraCalibration:
        return self.cameraCalibration

    def getCameraSettingsValue(self):
        return self.camera_settings_value

    @abc.abstractmethod
    def open(self) -> bool:
        return False

    @abc.abstractmethod
    def close(self) -> bool:
        return False

    @abc.abstractmethod
    def getImage(self) -> typing.Tuple[np.ndarray, np.ndarray]:
        rgb_image = np.ndarray(shape=(640, 480), dtype=np.uint8)
        depth_image = np.ndarray(shape=(640, 480), dtype=np.uint8)
        return rgb_image, depth_image

    @abc.abstractmethod
    def getParameters(self) -> dict:
        return {}

    @abc.abstractmethod
    def setParameters(self, params : dict, use_default=False) -> bool:
        return False

    def changeParametersGUI(self):
        from zed_gui import Application
        try:
            import tkinter as tk  # for python 3
        except:
            import Tkinter as tk  # for python 2

        import cv2
        while True:
            img = self.getImage()[0]  # rgb
            cv2.imshow('img', img)
            k = cv2.waitKey(5000)
            if k == 27:  # Esc key to stop
                break
            elif k == ord('c'):
                print("continue")
                root = tk.Tk()
                app = Application(root, self)
                root.mainloop()





if __name__ == '__main__':

    c = CameraBase()

    c.changeParametersGUI()

    print("DONE")
