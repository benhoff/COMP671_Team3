import os

from selenium import webdriver
import numpy as np
import cv2
import io

from code import interact

from pixellinkdecoder import PixelLinkDecoder

def _get_files():
    dir_ = os.path.abspath(os.path.dirname(__file__))
    intel_dir = os.path.join(dir_, 'intel', 'text-detection-0004', 'FP16')

    bin_file = os.path.join(intel_dir, 'text-detection-0004.bin')
    xml_file = os.path.join(intel_dir, 'text-detection-0004.xml')

    return bin_file, xml_file



# Selenium to opencv
# https://stackoverflow.com/a/50850092/2701402
def main():
    bin, xml = _get_files()
    td = cv2.dnn.readNet(xml, bin)

    driver = webdriver.Chrome()
    driver.get("https://imgur.com/")

    logo = driver.find_element_by_tag_name('svg')
    img_data = driver.get_screenshot_as_png()
    # img_data = logo.screenshot_as_png
    # img_data = logo.screenshot

    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # GRAVEYARD ------
    # Ref: https://stackoverflow.com/a/25589276/2701402
    # see comment of above answer
    # img_data = io.BytesIO(img_data)
    # img = np.asarray(img_data)
    # img = cv2.imread(img_data)

    # img = cv2.UMat(img)
    # img = np.float32(img)

    # GRAVEYARD ------
    

    out_layer_names = td.getUnconnectedOutLayersNames()
    expected_out_layer_names = (['model/link_logits_/add', 'model/segm_logits/add'],
                                ['pixel_cls/add_2', 'pixel_link/add_2'])
    if out_layer_names not in expected_out_layer_names:
        print("Net has unexpected output layer names, please check model files")
        print("Expected: '{e}', returned: '{r}'".format(e=expected_out_layer_names, r=out_layer_names))
        return 1

    blob = cv2.dnn.blobFromImage(img, 1, (1280, 768))
    td.setInput(blob)
    a, b = td.forward(out_layer_names)

    expected_a_shape = (1, 16, 192, 320)
    expected_b_shape = (1, 2, 192, 320)
    if a.shape != expected_a_shape or b.shape != expected_b_shape:
        print("Net has returned outputs of different shape, please check model files")
        print("Expected shapes: ({ea}, {eb}), returned: ({ra}, {rb})".format(ea=expected_a_shape,
                                                                             eb=expected_b_shape,
                                                                             ra=a.shape, rb=b.shape))
        return 1

    dcd = PixelLinkDecoder()
    dcd.load(img, a, b)
    dcd.decode()  # results are in dcd.bboxes
    dcd.plot_result_cvgui(img)


if __name__ == '__main__':
    main()
