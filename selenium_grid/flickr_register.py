from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import time					 
					 
driver = webdriver.Remote(
   command_executor="http://b3jkokkh8wy0Jo6n8BeQ4FlBmCzct5bu:YlEcvOkubIkLXhYVI2CDyN4KguMzpOTd@TENJ4OF9.gridlastic.com:80/wd/hub",
   desired_capabilities={
            "browserName": "chrome",
            "browserVersion": "latest",
            "video": "True",
            "platform": "WIN10",
            "platformName": "windows"
        })
print ("Video: http://s3-us-east-2.amazonaws.com/17d3b7d9-c6f4-80d4-9872-r9392763baf1/26ba6434-54b3-b6ee-fe98-5afae1411b62/play.html?"+driver.session_id)
  
try:
    # wait for 10 seconds before erroring
    driver.implicitly_wait(10)

    # Go to flickr
    driver.get("https://identity.flickr.com/sign-up")

    # interact(local=locals())
    firstname = driver.find_element_by_id("sign-up-first-name")
    firstname.send_keys("COMP671")

    lastname = driver.find_element_by_id("sign-up-last-name")
    lastname.send_keys("Student")

    age = driver.find_element_by_id("sign-up-age")
    age.send_keys("100")

    email = driver.find_element_by_id("sign-up-email")
    email.send_keys("my_email@franklin.edu")

    password = driver.find_element_by_id("sign-up-password")
    password.send_keys("my_super_secret_password")

    time.sleep(5)
finally:
    driver.quit()
