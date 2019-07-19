import os
import cv2
import sys

from PyQt5.QtCore import QThread
from PyQt5.QtGui import QImage, QPixmap

dir_path = os.path.dirname(os.path.realpath(__file__))
try:
    sys.path.append(dir_path + '/openpose')
    os.environ['PATH'] = os.environ['PATH'] + ';' + dir_path + '/openpose;' + dir_path + '/3rdparty;'
    import pyopenpose as op
except ImportError as e:
    print('Error: OpenPose library could not be found. \
            Did you enable `BUILD_PYTHON` in CMake and \
            have this Python script in the right folder?')
    raise e


class OpenposeThead(QThread):
    """多线程处理图像"""
    def __init__(self, label, param={"model_folder": "models/"}):
        super(OpenposeThead, self).__init__()
        self.label = label
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640)
        self.cap.set(4, 480)
        self.op_wrapper = op.WrapperPython()
        self.op_wrapper.configure(param)
        self.op_wrapper.start()
        self.datum = op.Datum()
        self.working = True

    def config_wrapper(self, params):
        self.working = False
        self.op_wrapper.stop()
        self.op_wrapper.configure(params)
        self.op_wrapper.start()
        self.working = True

    def run(self):
        try:
            while True:
                ret, frame = self.cap.read()
                # frame = cv2.imread('media/2.jpg')
                if frame is None:
                    print("读取摄像头失败")
                    return
                self.datum.cvInputData = frame
                if self.working:
                    self.op_wrapper.emplaceAndPop([self.datum])
                    self.updata_label(self.datum.cvOutputData)
        except Exception as e:
            print("openpose thread error", e)

    def updata_label(self, frame):
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # bgr -> rgb
        h, w, c = img.shape  # 获取图片形状
        image = QImage(img, w, h, 3 * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        self.label.setPixmap(pixmap)
