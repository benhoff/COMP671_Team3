from selenium import webdriver
from code import interact


driver = webdriver.Chrome()

# wait for 10 seconds before erroring
driver.implicitly_wait(10)

# Go to imgur
driver.get("https://imgur.com/")

# https://selenium-python.readthedocs.io/locating-elements.html
header = driver.find_element_by_class_name('TrendingTags-container')

# Each trending topic is actually a link, so let's grab all the links
links = header.find_elements_by_tag_name('a')

# let's keep a reference to each url
my_links = []

# and the english title of the trending
titles = []

# and the number of posts that are available
posts = []


for link in links:
    # uncomment the below python line to drop into the REPL to explore attributes and methods without rerunning and printing
    # interact(local=locals())

    # the actual link is a property of the DOM element
    # named `href`. We use the `get_property` method to access element attributes
    href = link.get_property('href')
    my_links.append(href)

    # Xpaths let us use the structured nature of the DOM to navigate to elements
    # including relative navigation and some "helpers"
    # Cheatsheet for xpaths: https://devhints.io/xpath

    # Using the '.' lets you navigate the xpath relatively
    name_element = link.find_element_by_xpath('./div/div')
    # the `text` method let's us get the text out
    name_text = name_element.text
    # keep track of the english title
    titles.append(name_text)

    # use some of the helper methods of the @class method to navigate to the second post
    data_element = link.find_element_by_xpath('./div/div[@class="Tag-posts"]')
    data_text = data_element.text
    # use some python to grab the number we're interested in
    num_posts = data_text.split(' ')[-2]

    posts.append(num_posts)

driver.close()    

print("\n")

for name, number, link in zip(titles, posts, my_links):
    print("Trending topic '{}' has {} posts found at: {}".format(name, number, link))

print()
