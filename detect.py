import datetime
import threading
import time

from kivy.graphics.texture import Texture
import requests
import numpy as np
import cv2
import json
import os
import glob
from kivymd.toast import toast


class DetectFruitHealth:

    def __init__(self):
        self.image = None
        self.output_image_path = None
        files = glob.glob('inference_outputs/*')
        for f in files:
            os.remove(f)

    def infer(self, img_path):
        url = 'https://zendimak-passion-image.herokuapp.com/predict'

        payload = {"file": open(img_path, "rb")}
        start_time = time.time()
        response = requests.post(url=url, files=payload)
        if response.status_code == 200:
            image = np.array(json.loads(response.text).get('results'))
            img_path = 'inference_outputs/output{:}.jpg'.format(datetime.datetime.now())
            cv2.imwrite(img_path, image)
            self.output_image_path = img_path
            toast('Inference took: {:.2f} ms'.format((time.time() - start_time)*1000))
            self.detecting = False
        else:
            self.detecting = False
            toast('Check your internet connection')

    def post_process(self):
        buf = cv2.flip(self.image, 0).tostring()
        texture = Texture.create(size=(self.image.shape[1], self.image.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        return texture

    def invoke(self, img_path=None):
        self.infer(img_path)

    def run(self, img_path):
        threading.Thread(target=self.invoke, args=(img_path,), daemon=True).start()


if __name__ == '__main':
    obj = DetectFruitHealth()
