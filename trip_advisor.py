import requests
import lxml
import lxml.html
import requests
from bs4 import BeautifulSoup as bs
import lxml.html


trip = requests.get('https://www.tripadvisor.de/ShowUserReviews-g187323-d2694703-r162455177-BBI_Berlin_Burger_International-Berlin.html')
trip_url = "https://www.tripadvisor.de/ShowUserReviews-g187323-d2694703-r499602079-BBI_Berlin_Burger_International-Berlin.html"


page_trip = lxml.html.fromstring(trip.text)
for p in page_trip.xpath('//*[contains(@class, "pageNum")]'):
    print(p.text, p.get('href'))

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()

def visit_next(driver):
    numb = driver.find_element_by_class_name('pageNumbers')
    links = numb.find_elements_by_tag_name('a')
    to_visit = None
    for link in links:
        if link.text not in visited:
            visited.add(link.text)
            print(link.text)
#             do some magic here
            link.click()
            return len(driver.find_elements_by_xpath('//*[contains(@class, "reviewSelector")]'))
    return 0



visited = set(['1'])
reviews = 0
driver.get(trip_url)
while True:
    new_reviews = visit_next(driver)
    if not new_reviews:
        print("Done")
        break
    reviews += new_reviews
    print("We now have {} reviews".format(reviews))
    if len(visited) > 1200:
        print("Done")
        break