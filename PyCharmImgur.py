from selenium import webdriver

print("imgur gif test case started")
driver = webdriver.Chrome()
driver.maximize_window()
# navigate to the url
driver.get("https://imgur.com/t/cat/vdBmtBG/")

if(driver.find_element_by_xpath('//html/head/meta[31]')) is None:
    print("tag:funny was not found")
else:
    print("tag:funny was found")

element = driver.find_element_by_id("submit-comment")
if element.is_enabled():
    print("Post comment is enabled")
else:
    print("Post comment is not enabled")

if(driver.find_element_by_xpath('//*[@id="inside"]/div[2]/div[3]/div[1]/div/div[1]/div[2]/div')) is None:
    print("Next Post button was not found")
else:
    print("Next Post button was found")

if(driver.find_element_by_xpath('//*[@id="captions"]/div[2]/span[2]/div[1]/div/div[1]/span/span')) is None:
    print("top comment: touch the kitty was not found")
else:
    print("top comment: touch the kitty was found")

# close the browser
driver.close()
print("imgur gif test case successfully completed")
