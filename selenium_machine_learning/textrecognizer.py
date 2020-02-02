import os
import cv2
import numpy as np


def _get_recognition_files():
    dir_ = os.path.abspath(os.path.dirname(__file__))
    intel_dir = os.path.join(dir_, 'intel', 'text-recognition-0012', 'FP16')

    bin_file = os.path.join(intel_dir, 'text-recognition-0012.bin')
    xml_file = os.path.join(intel_dir, 'text-recognition-0012.xml')

    return bin_file, xml_file


class TextRecognizer:
    def __init__(self):
        self.symbols = "0123456789abcdefghijklmnopqrstuvwxyz#"
        bin, xml = _get_recognition_files()
        self.net = cv2.dnn.readNet(xml, bin)

    def process(self, img_source):
        img = img_source.copy()
        input_width = 120
        input_height = 32
        img_height = img.shape[0]
        img_width = img.shape[1]
        blob = cv2.dnn.blobFromImage(img, 1.0, (input_width, input_height))
        self.net.setInput(blob)
        res = self.net.forward(self.net.getUnconnectedOutLayersNames())
        return res

    def ctc_decoder(self, data):
        result = ""
        prev_pad = False
        num_classes = len(self.symbols)
        for i in range(data.shape[0]):
            symbol = self.symbols[np.argmax(data[i])]
            if symbol != self.symbols[-1]:
                if len(result) == 0 or prev_pad or (len(result) > 0 and symbol != result[-1]):
                    prev_pad = False
                    result = result + symbol
            else:
                prev_pad = True
        return result

    def inference(self, img, bbrect):
        texts = []
        for x, y, w, h in bbrect:
            img_gray = cv2.cvtColor(img[y:y+h, x:x+w, :], cv2.COLOR_BGR2GRAY)
            result = self.process(img_gray)
            text = self.ctc_decoder(result[0]).strip()
            if text:
                cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,0,255), 1)
                texts.append(text)
        return texts
