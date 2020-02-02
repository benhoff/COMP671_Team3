import unittest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import numpy as np
import cv2
import io
import os

from pixellinkdecoder import PixelLinkDecoder
from textrecognizer import TextRecognizer
from ssdrecognizer import SSDRecognizer
from code import interact

# Ref: https://www.techbeamers.com/selenium-python-test-suite-unittest/#h2
class ImgurPageTest(unittest.TestCase):

    @classmethod
    def setUp(instance):
        instance.driver = webdriver.Chrome()
        instance.driver.implicitly_wait(10)
        instance.driver.maximize_window()
        instance.driver.get("https://imgur.com")

        instance.text_detect = PixelLinkDecoder()
        instance.text_recog = TextRecognizer()
        instance.obj_finder = SSDRecognizer()

    @classmethod
    def tearDown(instance):
        instance.driver.close()
        del instance.text_detect
        del instance.text_recog

    def _get_trending_topics(self):
        header = self.driver.find_element_by_class_name('TrendingTags-container')
        # Each trending topic is actually a link, so let's grab all the links
        links = header.find_elements_by_tag_name('a')
        titles = []

        for link in links:
            name_element = link.find_element_by_xpath('./div/div')
            name_text = name_element.text
            titles.append(name_text)

        return titles

    """
    # NOTE: This model take 70+ seconds to run
    def test_semantic_similarity(self):
        word2vec_file = self._get_word2vec_path()
        import gensim

        load_word2vec = gensim.models.KeyedVectors.load_word2vec_format

        model = load_word2vec(word2vec_file, binary=True)
        titles = self._get_trending_topics()
        cat_topic = False
        
        # Titles can have multiple words, we can only parse single words
        for title in titles:
            # Use the `split` method to seperate the words
            title_words = title.split(' ')
            for word in title_words:
                # See if words are semantically similar to cat
                try:
                    similarity = model.similarity(word, "cat")
                except KeyError:
                    continue
                if similarity > .8:
                    cat_topic = True
                    break

            if cat_topic:
                break
        del model
        self.assertTrue(cat_topic)
    """

    def _get_cv2_img_array(self, image_data):
        nparr = np.frombuffer(image_data, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    def _get_word2vec_path(self):
        dir_ = os.path.abspath(os.path.dirname(__file__))
        word2vec = os.path.join(dir_, 'models',
                                'GoogleNews-vectors-negative300.bin')
        return word2vec

    def test_logo_present(self):
        logo = self.driver.find_element_by_tag_name('svg')
        location = logo.location
        size = logo.size
        img_data = self.driver.get_screenshot_as_png()

        img = self._get_cv2_img_array(img_data)

        fudge_factor = 125

        # left = location['x']
        # top = location['y']
        left = 0
        top = 0
        right = left + size['width'] + fudge_factor
        bottom = top + size['height'] + fudge_factor

        img = img[top:int(bottom), left:int(right)]
        image_show, bounding_rects = self.text_detect.inference(img)
        texts = self.text_recog.inference(img, bounding_rects)

        texts_found = len(texts)
        self.assertGreater(texts_found, 0)

        self.assertEqual(texts[0], 'imgur')

    def test_logo_works_minified(self):
        self.driver.get('chrome://settings/')
        self.driver.execute_script('chrome.settingsPrivate.setDefaultZoom(0.25);')
        self.driver.get("https://imgur.com")
        self.test_logo_present()

    def test_logo_maximized(self):
        self.driver.get('chrome://settings/')
        self.driver.execute_script('chrome.settingsPrivate.setDefaultZoom(1.5);')
        self.driver.get("https://imgur.com")

    def test_find_person_and_cat_on_front_page(self):
        img_data = self.driver.get_screenshot_as_png()
        img = self._get_cv2_img_array(img_data)

        cat_found, person_found = self.obj_finder.contains_cat_and_person(img)

        self.assertTrue(person_found)
        self.assertTrue(cat_found)
    
    def test_find_cat(self):
        self.driver.get('https://imgur.com/t/cat/vdBmtBG')
        img_data = self.driver.get_screenshot_as_png()
        img = self._get_cv2_img_array(img_data)

        cat_found, _ = self.obj_finder.contains_cat_and_person(img)
        # interact(local=locals())
        self.assertTrue(cat_found)

    def test_find_person(self):
        self.driver.get('https://imgur.com/gallery/ruzXxXk')
        img_data = self.driver.get_screenshot_as_png()
        img = self._get_cv2_img_array(img_data)

        _, person_found = self.obj_finder.contains_cat_and_person(img)
        self.assertTrue(person_found)

    def find_cat_and_person(self):
        self.driver.get('https://imgur.com/t/cat/9afWxMO')
        img_data = self.driver.get_screenshot_as_png()
        img = self._get_cv2_img_array(img_data)

        cat_found, person_found = self.obj_finder.contains_cat_and_person(img)

        self.assertTrue(person_found)
        self.assertTrue(cat_found)

if __name__ == '__main__':
    unittest.main()
