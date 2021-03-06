import os
import time
# from code import interact

from selenium import webdriver


driver = webdriver.Chrome()
driver.get("https://imgur.com/")

png_data = driver.get_screenshot_as_png()

dirname = os.path.abspath(os.path.dirname(__file__))
filename = 'my_png.png'

filename = os.path.join(dirname, filename)

if os.path.isfile(filename):
    os.remove(filename)

with open(filename, 'wb') as f:
    f.write(png_data)
# interact(local=locals())

driver.close()
