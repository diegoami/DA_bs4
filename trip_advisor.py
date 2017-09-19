import requests
import lxml
import lxml.html


trip = requests.get('https://www.tripadvisor.de/ShowUserReviews-g187323-d2694703-r162455177-BBI_Berlin_Burger_International-Berlin.html')

page_trip = lxml.html.fromstring(trip.text)
for p in page_trip.xpath('//*[contains(@class, "pageNum")]'):
    print(p.text, p.get('href'))
