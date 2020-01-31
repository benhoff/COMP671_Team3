from selenium import webdriver
import time


driver = webdriver.Chrome()
driver.get("https://imgur.com/")

time.sleep(5)

driver.close()
