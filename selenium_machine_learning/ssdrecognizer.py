import os
import cv2

from code import interact


class SSDRecognizer:
    def __init__(self):
        weights, config = self._get_filepaths()

        self.net = cv2.dnn.readNetFromTensorflow(weights, config)


    def _get_filepaths(self):
        dir_ = os.path.abspath(os.path.dirname(__file__))
        dir_ = os.path.join(dir_, 'public',
                           'ssd_mobilenet_v2_coco', 'ssd_mobilenet_v2_coco_2018_03_29')

        weights = os.path.join(dir_, 'frozen_inference_graph.pb')
        config = os.path.join(dir_, 'config.pbtxt')

        return weights, config

    def inference(self, image):
        blob = cv2.dnn.blobFromImage(image, crop=False)
        self.net.setInput(blob)
        cv_out = self.net.forward()

        return cv_out


    def contains_cat_and_person(self, image):
        cv_out = self.inference(image)
        cat_found = False
        person_found = False


        for i in range(cv_out.shape[2]):
            score = float(cv_out[0, 0, i, 2])
            # Confidence threshold is in prototxt.
            class_ = int(cv_out[0, 0, i, 1])

            if score > .5:
                if class_ == 17:
                    cat_found = True
                elif class_ == 1:
                    person_found = True

        return cat_found, person_found
