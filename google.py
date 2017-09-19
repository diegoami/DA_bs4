from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()

google_url = "https://www.google.de/search?q=BBI+-+Berlin+Burger+International&oq=BBI+-+Berlin+Burger+International&aqs=chrome..69i57j69i60l2j0j69i60.455j0j7&sourceid=chrome&ie=UTF-8#lrd=0x47a84fb09074cdcd:0xdbb4649be7a5d4b3,1,"

driver.get(google_url)

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

driver.find_elements_by_xpath('//*[contains(@class, "_D7k gws-localreviews__google-review")]')
element = driver.find_elements_by_xpath('//*[contains(@class, "_D7k gws-localreviews__google-review")]')[-1]

location = element.location_once_scrolled_into_view
driver.execute_script("window.scrollTo(0, {});".format(location['y']))

element = driver.find_elements_by_xpath('//*[contains(@class, "_D7k gws-localreviews__google-review")]')[-1]
location = element.location_once_scrolled_into_view
