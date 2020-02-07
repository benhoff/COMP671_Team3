import time, warnings, webbrowser, unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class TestExamples(unittest.TestCase):

    def launch_flickr(self, test_number, browser="chrome", browserVersion="latest",
                      platform="WIN10", platformName="windows"):
        warnings.filterwarnings("ignore")
        try:
            driver = webdriver.Remote(
                command_executor="http://b3jkokkh8wy0Jo6n8BeQ4FlBmCzct5bu:YlEcvOkubIkLXhYVI2CDyN4KguMzpOTd@TENJ4OF9.gridlastic.com:80/wd/hub",
                desired_capabilities={
                    "browserName": browser,
                    "browserVersion": browserVersion,
                    "video": "True",
                    "platform": platform,
                    "platformName": platformName,
                }
            )
            driver.implicitly_wait(10)
            driver.get("https://identity.flickr.com/sign-up")
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
            #time.sleep(1)
        finally:
            url = "http://s3-us-east-2.amazonaws.com/17d3b7d9-c6f4-80d4-9872-r9392763baf1/26ba6434-54b3-b6ee-fe98-5afae1411b62/play.html?" + driver.session_id
            print("Test " + str(test_number) + " Video:\n" + url)
            webbrowser.open(url)
            driver.quit()

    def test_one(self):
        self.launch_flickr(1)
		   
    def test_two(self):
        self.launch_flickr(2,browser="firefox",browserVersion="71")

    def test_three(self):
        self.launch_flickr(3,browser="internet explorer",browserVersion="11")

    def test_four(self):
        self.launch_flickr(4,platform="WIN8_1")

    def test_five(self):
        self.launch_flickr(5,platform="LINUX",platformName="linux")

if __name__ == "__main__":
    unittest.main()
