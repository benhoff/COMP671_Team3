from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

import time


driver = webdriver.Chrome()

# wait for 10 seconds before erroring
driver.implicitly_wait(10)

# Go to imgur
driver.get("https://imgur.com/register")


# interact(local=locals())
username = driver.find_element_by_id("username")
username.send_keys("COMP671")

email = driver.find_element_by_id("email")
email.send_keys("COMP671@franklin.edu")

password = driver.find_element_by_id("password")
password.send_keys("my_example_password1")

confirm_password = driver.find_element_by_id("confirm_password")
confirm_password.send_keys("my_example_password1")

phone_number = driver.find_element_by_id("phone_number")
phone_number.send_keys("1111111111")

next_button = driver.find_element_by_id("Imgur")

actions = ActionChains(driver)
actions.move_to_element(next_button).perform()


time.sleep(3)
next_button.click()
time.sleep(2)

driver.close()
