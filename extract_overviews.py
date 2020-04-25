import time
import random
import yaml
import certifi
import urllib3
from bs4 import BeautifulSoup

with open('config.yaml', 'r') as config_file:
    config = yaml.load(config_file, Loader=yaml.SafeLoader)


def compose_url(area, new_ads):
    url = config['overview_page']

    for a in area.split(','):
        url += config['area_codes'][a]

    if new_ads is True:
        url += '&' + config['new_ads']

    return url


def extract_ad_thumbnails(url, min_wait, max_wait, max_pages):
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                               ca_certs=certifi.where())

    i = 1
    right_button = True

    while i <= max_pages and right_button:
        time.sleep(random.randint(min_wait, max_wait))
        page_url = url + f'&page={i}'
        page = http.request('GET', page_url)
        parsed = BeautifulSoup(page.data.decode('utf-8'), 'html.parser')
        ads = parsed.findAll('article', {'class': 'ads__unit'})
        for a in ads:
            yield a
        i += 1


def extract_thumbnail_details(ad):
    thumbnail_details = {}
    link_tag = ad.find('a', {'class': 'ads__unit__link'})
    img_tag = ad.find('div', {'class': 'ads__unit__img__ratio'
                                       ' img-format img-format--ratio3by2'
                                       ' img-format--centered'})
    addr_tag = ad.find('div', {'class': 'ads__unit__content__details'})
    price_area_tag = ad.find('div', {'class': 'ads__unit__content__keys'})\
        .findAll('div')

    thumbnail_details['id'] = link_tag['id']
    thumbnail_details['link'] = config['link_prefix'] + link_tag['href']
    thumbnail_details['img_link'] = img_tag.img['src']
    thumbnail_details['short_desc'] = link_tag.string.strip()
    thumbnail_details['address_short'] = addr_tag.string.strip()
    thumbnail_details['new_building'] = False
    thumbnail_details['main_price'] = price_area_tag[1].string.strip()
    thumbnail_details['viewed'] = time.strftime('%Y-%m-%d %X')
    thumbnail_details['size'] = price_area_tag[0].string.strip()

    return thumbnail_details


def extract_data(area, new_ads, verbose, min_wait, max_wait, max_pages):
    url = compose_url(area, new_ads)

    ad_thumbnails = extract_ad_thumbnails(url, min_wait, max_wait, max_pages)
    for ad in ad_thumbnails:
        thumbnail_details = extract_thumbnail_details(ad)
        print(thumbnail_details)
        print('\n' * 2)


if __name__ == '__main__':
    import argparse
    parser = argparse.\
        ArgumentParser(description='Run the housing data extractor')

    parser.add_argument('--area',
                        help='Comma separated area names',
                        type=str,
                        default='oslo')
    parser.add_argument('--new_ads',
                        help='Get only new ads',
                        type=bool,
                        default=True)
    parser.add_argument('--verbose',
                        help='Log full results or run silently',
                        type=bool,
                        default=True)
    parser.add_argument('--min_wait',
                        help='Minimum wait time between ad pages',
                        type=int,
                        default=1)
    parser.add_argument('--max_wait',
                        help='Maximum wait time between ad pages',
                        type=int,
                        default=2)
    parser.add_argument('--max_pages',
                        help='Maximum number of pages to visit',
                        type=int,
                        default=1)

    args = parser.parse_args()
    extract_data(args.area, args.new_ads, args.verbose, args.min_wait,
                 args.max_wait, args.max_pages)
