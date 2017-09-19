#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import csv
import datetime
import json
import argparse
import os
import requests
from bs4 import BeautifulSoup as bs
import lxml.html

from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup as bs
import iso8601


def is_404(content):
    if len(content.find_all(class_="restaurantreview")) == 0:
        return True
    for el in content.find_all('link'):
        if el.has_attr("href"):
            if "lieferando.de/404" in el['href']:
                return True
    return False


def get_review_comment_lieferando(review):
    comment = review.find(class_="reviewbody")
    if comment:
        return comment.text
    else:
        return ""


def get_rating_lieferando(review):
    for el in review.find_all('span'):
        if el.get('itemprop') == 'reviewRating':
            try:
                return float(el.find('meta')['content'])
            except ValueError:
                return 0.0


def get_stars_lieferando(review):
    delivery = 0
    quality = 0
    if len(review.find(class_="ratingscontainer").find_all(class_="review-rating")) == 2:
        for el in review.find(class_="ratingscontainer").find_all(class_="review-rating"):
            value = el.find(class_="review-stars-range").get('style')
            if not value:
                return None, None
            value = value.strip(";%").split(":")[-1]
            value = int(int(value) / 20)
            if "qualität" in el.text or "quality" in el.text:
                quality = value
            else:
                delivery = value
    return delivery, quality


def format_date(day, hour):
    return day + "T" + hour + "Z"


def parse_date_lieferando(content):
    day = content.get('content')
    try:
        _, hour = content.text.split(" um ")
        #         print("yes?")
        return format_date(day, hour)
    except:
        return day


# 2017-03-27T12:46:25Z
def parse_date_other(content):
    day, temp_hour = content.get('content').split("T")
    #     day, temp_hour = content.split("T")
    hour = temp_hour.strip("Z")
    return format_date(day, hour)


def extract_review_lieferando(review_content):
    review = {}
    review['Comment'] = get_review_comment_lieferando(review_content)
    delivery, quality = get_stars_lieferando(review_content)
    if not quality:
        return None
    review['Delivery'] = delivery
    review['Food quality'] = quality
    overall = get_rating_lieferando(review_content)
    # if overall != (delivery + quality) / 2:
    #     print(overall, delivery, quality)
    review['Overall stars'] = overall
    review['Datetime'] = parse_date_lieferando(review_content.find(class_="reviewdate"))
    return review


def extract_reviews_lieferando(content, brand=None):
    for this_one in content.find_all(class_="restaurantreview"):
        review = extract_review_lieferando(this_one)
        if review:
            review['Brand'] = brand
            review["Platform"] = "Lieferando"
            review['id'] = hash_review(review)
            yield review


def create_headers_pizza(url):
    headers_pizza = {'Host': 'pizza.de',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                     'Referer': url,
                     'x-mrv-namespace': 'pizza.de'}
    return headers_pizza


def create_headers_held(url, host=""):
    headers_held = {
        'Authentication':'LH api-key=BqFXeTedMu1LQazCYZznkzyL5CFffcWIDW7GEpmCFVAPLi1dA4cdt76BnXkyEuqWAbCf8ZWtADOzaz5851LQj1dlppQVZSxPPAe0cA0g7Tn2GoXWTdfStKk5yrKrrB0J',
        'Connection': 'keep-alive',
        'Host': host,
        'Referer': url,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    return headers_held


def yield_reviews(page_data, brand, platform):
    fields = {'created_at': 'Datetime',
              'message': 'Comment',
              'rating': 'Overall stars'}
    for base_review in page_data['data']:
        review = {"Brand": brand,
                  "Platform": platform}
        for key, value in fields.items():
            review[value] = base_review['comment'][key]
        for el in LIEFERANDO_SPECIFIC:
            review[el] = None
        yield review


def get_reviews_other(url, brand, platform, location):
    counter = 0
    platforms = get_platforms()
    headers = platforms[platform]["headers"](url)
    reviews = []
    restaurant_code = url.split("/")[-2]
    while True:
        data_url = '{}{}/comments/?fields=comment&limit={}&offset={}&sort='.format(platforms[
                                                                                       platform]["base_url"],
                                                                                   restaurant_code, 100, counter*100)
        # page = requests.get(data_url, headers=headers)
        page = requests.get(data_url)
        if page.status_code != 200:
            break
        page_data = page.json()
        if len(page_data['data']) == 0:
            break
        for review in yield_reviews(page_data, brand, platform):
            print(". ", end="", flush=True)
            review['id'] = hash_review(review)
            review['location'] = location
            reviews.append(review)
        counter += 1
    return reviews


def get_reviews_lieferando(brand, original_url, location, pages=None):
    counter = 1
    # original_url = "https://www.lieferando.de/lieferservice-gringo-burritos-berlin/bewertungen"
    url = original_url
    reviews = []
    # for i in range(1):
    while True:
        content = requests.get(url)
        # workaround for rewriting
        if counter == 1 and content.url != original_url:
            print("changing url from {} to {}".format(original_url, content.url))
            original_url = content.url
        bs_content = bs(content.text, "lxml")
        if is_404(bs_content):
            break
        for review in extract_reviews_lieferando(bs_content, brand):
            review['location'] = location
            print(". ", end="", flush=True)
            reviews.append(review)
        counter += 1
        url = original_url + "/" + str(counter)
        if pages and counter > pages:
            break
    print()
    print("{} reviews from {}".format(len(reviews), original_url))
    return reviews


def hash_review(review:dict):
    # return hash("".join([str(r) for r in review.values()]))
    return review['Datetime']+review['Brand']+review['Platform']


def get_lieferando_review_url(url):
    # https: // www.lieferando.de / greengurus
    # https: // www.lieferando.de / bewertungen - greengurus
    p = urlparse(url)
    p_path = "/" + "bewertungen-" + p.path.strip("/")
    p_url = p.scheme + "://" + p.hostname + p_path
    return p_url

def do_test_lieferando():
    reviews = get_reviews_lieferando('Sushi','https://www.lieferando.de/bewertungen-yoko-sushi-mitte',None)

    print(reviews)

def do_lieferando():
    counter = 1
    brand = "yoko-sushi-mitte"
    base_url = "https://www.lieferando.de/bewertungen"
    original_url = base_url + brand + "/"
    reviews = []
    while True:
        url = original_url + "/" + str(counter)
        content = requests.get(url)
        # workaround for rewriting
        #     if counter == 1 and content.url != original_url:
        #         original_url = content.url
        bs_content = bs(content.text, "lxml")
        if is_404(bs_content):
            break
        for review in extract_reviews_lieferando(bs_content, brand):
            print(". ", end="", flush=True)
            reviews.append(review)
        counter += 1
    # if counter == 2:
    #         break
    print()
    return reviews

reviews = do_lieferando()
print(reviews)