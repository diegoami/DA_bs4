

import requests
import json
head = {
"Host":"pizza.de",
"Referer":"https://pizza.de/lieferservice/berlin/restaurant-yoko-sushi-berlin-martin-luther-str-410/9647/",
"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
"x-mrv-namespace":"pizza.de"
}
url_p = 'https://pizza.de/marvin-api/reviews/?businessId=9647&size=5000&order=&'
url_l = 'https://www.lieferheld.de/api/restaurants/10475/comments/?fields=comment&has_text=1&offset=700&limit=700'

# Get url from Network tab on the Developer stuff

url_g = 'https://pizza.de/marvin-api/reviews/?businessId=9647&size=50&order=&hasText=true'
req_try = requests.get(url_g, headers=head)
print(req_try.text)
json_try = req_try.json()
print(json_try)
