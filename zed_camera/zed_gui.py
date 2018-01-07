"""
pygubu-designer

Drag and drop GUI
"""
try:
    import tkinter as tk  # for python 3
except:
    import Tkinter as tk  # for python 2
import pygubu

from CameraBase import CameraBase

class Application:

    def __init__(self, master, zed=CameraBase()):

        #1: Create a builder
        self.builder = builder = pygubu.Builder()

        #2: Load an ui file
        builder.add_from_file('gui/zed_gui.ui')

        #3: Create the widget using a master as parent
        self.mainwindow = builder.get_object('mainwindow', master)

        self.zed = zed
        # self.camera_settings_value = {'WHITEBALANCE': 4600, 'BRIGHTNESS': 4, 'CONTRAST': 4, 'EXPOSURE': 54, 'HUE': 0, 'GAIN': 98, 'AUTO_WHITEBALANCE': 1, 'SATURATION': 4}
        self.camera_settings_value = self.zed.getCameraSettingsValue().copy()
        self.old_camera_settings_value = self.camera_settings_value.copy()


        self.AWB_flag = True
        self.AutoExposure_flag = True

        self.var_awb_check = self.builder.get_variable('VAR_awb_check') # boolean value
        self.var_AutoExposure_check = self.builder.get_variable('VAR_auto_exposure_check')
        self.obj_AWB = self.builder.get_object('ID_WHITEBALANCE')
        self.obj_Gain = self.builder.get_object('ID_GAIN')
        self.obj_Exposure = self.builder.get_object('ID_EXPOSURE')

        self.__assign_init_value()



        builder.connect_callbacks(self)


    def __assign_init_value(self):


        for k in ['BRIGHTNESS', 'CONTRAST', 'HUE', 'SATURATION',
                  'WHITEBALANCE', 'GAIN', 'EXPOSURE']:

            k_id = 'ID_' + k  # specified in ui file
            k_v_label = k_id + '_LABEL'

            try:
                label = self.builder.get_object(k_v_label)
                scale = self.builder.get_object(k_id)

                v = self.camera_settings_value[k]

                scale.configure(value=v)
                label.configure(text=v)

                if k == 'WHITEBALANCE':
                    scale.configure(value=int(v/100))

            except:
                print("Seems {} is not existing".format(k_id))



        self.var_awb_check.set(True)
        self.var_AutoExposure_check.set(True)
        self.awb_check_command() # init
        self.auto_exposure_check_command()

        print("Init done")





    def _perform_settings_AWB(self):
        self.zed.setParameters({'WHITEBALANCE':-1, 'AUTO_WHITEBALANCE':-1}, use_default=True)
        print("Set AUTO_WHITEBALANCE done")


    def _perform_settings_AutoExposure(self):
        self.zed.setParameters({'GAIN':-1, 'EXPOSURE':-1}, use_default=True)
        print("Set AutoExposure done")



    def _perform_settings_change(self):

        if self.AWB_flag == False and self.camera_settings_value['WHITEBALANCE'] != self.old_camera_settings_value['WHITEBALANCE']:
            self.zed.setParameters({'WHITEBALANCE': self.camera_settings_value['WHITEBALANCE']})
            print("CHANGE WHITEBALANCE done")

        if self.AutoExposure_flag == False and (
                self.camera_settings_value['GAIN'] != self.old_camera_settings_value['GAIN'] or
                self.camera_settings_value['EXPOSURE'] != self.old_camera_settings_value['EXPOSURE']):
            self.zed.setParameters({'GAIN': self.camera_settings_value['GAIN'], 'EXPOSURE': self.camera_settings_value['EXPOSURE']})
            print("CHANGE GAIN and EXPOSURE done")

        for k in ['BRIGHTNESS', 'CONTRAST', 'HUE', 'SATURATION']:
            if self.camera_settings_value[k] != self.old_camera_settings_value[k]:
                self.zed.setParameters({k: self.camera_settings_value[k]})
                print("CHANGE:{} done".format(k))

        self.camera_settings_value = self.zed.getCameraSettingsValue().copy()
        self.old_camera_settings_value = self.camera_settings_value.copy()

        print(self.camera_settings_value)
        print("Set settings done")


    def awb_check_command(self):

        self.AWB_flag = self.var_awb_check.get()

        print("AWB configure changed:{}".format(self.AWB_flag))
        if self.AWB_flag:
            self.obj_AWB.state(["disabled"]) # https://stackoverflow.com/a/30736732/7067150
            self._perform_settings_AWB()
        else:
            """
            [Tkinter-discuss] Disabling widgets [especially ttk.Scale](https://mail.python.org/pipermail/tkinter-discuss/2011-January/002744.html)
            > if you're familiar with Tkinter states, the handling of states in ttk 
            > may seem a bit odd. To set a widget to "normal" state you must not
            > define the state "normal" but instead turn off the "disabled" state by
            > prefixing the state name with an exclamation mark. Here's a minimal
            > example how this can be done:
            """
            self.obj_AWB.state(["!disabled"])

        self._perform_settings_change()

    def on_whitebalance_change(self, event):

        assert self.AWB_flag == False

        v = int(self.obj_AWB.get())*100 # 100 per step
        label = self.builder.get_object('ID_WHITEBALANCE_LABEL')

        label.configure(text=v)

        self.camera_settings_value['WHITEBALANCE'] = v

        self._perform_settings_change()


    def auto_exposure_check_command(self):

        self.AutoExposure_flag = self.var_AutoExposure_check.get()

        print("AutoExposure configure changed:{}".format(self.AutoExposure_flag))
        if self.AutoExposure_flag:
            self.obj_Gain.state(["disabled"])
            self.obj_Exposure.state(["disabled"])
            self._perform_settings_AutoExposure()
        else:
            self.obj_Gain.state(["!disabled"])
            self.obj_Exposure.state(["!disabled"])

        self._perform_settings_change()

    def on_gain_or_exposure_change(self, event):

        assert self.AutoExposure_flag == False

        v = int(self.obj_Gain.get())
        label = self.builder.get_object('ID_GAIN_LABEL')
        label.configure(text=v)
        self.camera_settings_value['GAIN'] = v

        v = int(self.obj_Exposure.get())
        label = self.builder.get_object('ID_EXPOSURE_LABEL')
        label.configure(text=v)
        self.camera_settings_value['EXPOSURE'] = v

        self._perform_settings_change()

    def standalone_update(self, event):

        # {'WHITEBALANCE': 4600, 'BRIGHTNESS': 4, 'CONTRAST': 4, 'EXPOSURE': 54, 'HUE': 0, 'GAIN': 98, 'AUTO_WHITEBALANCE': 1, 'SATURATION': 4}
        for k in ['BRIGHTNESS', 'CONTRAST', 'HUE', 'SATURATION']:

            k_id = 'ID_'+k # specified in ui file
            k_v_label = k_id+'_LABEL'

            try:
                label = self.builder.get_object(k_v_label)
                scale = self.builder.get_object(k_id)

                v = int(scale.get())
                label.configure(text=v)
                self.camera_settings_value[k] = v
            except:
                print("Seems {} is not existing".format(k_id))


        self._perform_settings_change()


def test_zed():
    from ZEDCamera import ZEDCamera
    c = ZEDCamera()

    c.changeParametersGUI()

    print(c.camera_settings_value)

def plain_test():
    c = CameraBase()
    root = tk.Tk()
    app = Application(root, c)
    root.mainloop()

if __name__ == '__main__':
    test_zed()




