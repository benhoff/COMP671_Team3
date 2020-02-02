import os

from selenium import webdriver
import numpy as np
import cv2
import io

from code import interact

from pixellinkdecoder import PixelLinkDecoder
from textrecognizer import TextRecognizer


# Selenium to opencv
# https://stackoverflow.com/a/50850092/2701402
def main():
    td = PixelLinkDecoder()

    driver = webdriver.Chrome()
    # NOTE: there doesn't seem to be a good way to change the zoom settings that is cross browser
    # driver.get('chrome://settings/')
    # driver.execute_script('chrome.settingsPrivate.setDefaultZoom(0.25);')
    # Test cases of .25, .5, and 1. work

    # driver.set_window_position(0, 0)
    # driver.set_window_size(1024, 768)

    # could try various configurations

    driver.get("https://imgur.com/")

    logo = driver.find_element_by_tag_name('svg')

    location = logo.location
    size = logo.size

    img_data = driver.get_screenshot_as_png()
    # img_data = logo.screenshot_as_png
    # img_data = logo.screenshot

    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    fudge_factor = 125

    # left = location['x']
    # top = location['y']
    left = 0
    top = 0
    right = left + size['width'] + fudge_factor
    bottom = top + size['height'] + fudge_factor

    # print(location, size)

    img = img[top:int(bottom), left:int(right)]

    # GRAVEYARD ------
    # Ref: https://stackoverflow.com/a/25589276/2701402
    # see comment of above answer
    # img_data = io.BytesIO(img_data)
    # img = np.asarray(img_data)
    # img = cv2.imread(img_data)

    # img = cv2.UMat(img)
    # img = np.float32(img)

    # GRAVEYARD ------
    

    driver.close()
    # bin, xml = _get_recognition_files()
    # text_recog = cv2.dnn.readNet(xml, bin)

    image_show, bounding_rects = td.inference(img)

    # https://github.com/iamrishab/openvino-ocr/blob/a291cee5af2980f332456b9f5654bec562156456/text_recognition.py
    # https://github.com/opencv/opencv/blob/master/samples/dnn/text_detection.py
    # https://github.com/Panepo/Mutsuki/tree/70bd8811cf1b0fbe6f83489710804235a3caa5ab/text-recognition

    text_recognizer = TextRecognizer()

    texts = text_recognizer.inference(img, bounding_rects)

    print(texts)

    cv2.imshow("detected text", image_show)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
