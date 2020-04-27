import time
import random
import yaml
import certifi
import urllib3
from bs4 import BeautifulSoup
import requests

with open('config.yaml', 'r') as config_file:
    config = yaml.load(config_file, Loader=yaml.SafeLoader)


def compose_url(area, new_ad, new_building, property_type):
    url = config['overview_page']

    url += config['new_constr'] + str(new_building).lower() + '&'

    url += config['lifecycle']['for_sale'] + '&'

    for a in area.split(','):
        url += config['area_codes'][a] + '&'

    for p in property_type.split(','):
        url += config['property_type'][p] + '&'

    if new_ad is True:
        url += config['new_ad']

    return url


def extract_ad_tiles(url, min_wait, max_wait, max_pages):
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


def extract_tile_details(ad, new_building):
    details = {}
    link_tag = ad.find('a', {'class': 'ads__unit__link'})
    img_tag = ad.find('div', {'class': 'ads__unit__img__ratio'
                                       ' img-format img-format--ratio3by2'
                                       ' img-format--centered'})
    addr_tag = ad.find('div', {'class': 'ads__unit__content__details'})
    price_area_tag = ad.find('div', {'class': 'ads__unit__content__keys'})\
        .findAll('div')

    details['id'] = link_tag['id']
    details['link'] = config['link_prefix'] + link_tag['href']
    details['img_link'] = img_tag.img['src']
    details['short_desc'] = link_tag.string.strip()
    details['address_short'] = addr_tag.string.strip()
    details['new_building'] = new_building
    details['main_price'] = price_area_tag[1].string.strip()
    details['viewed'] = time.strftime('%Y-%m-%d %X')
    details['size'] = price_area_tag[0].string.strip()

    return details


def get_gmaps_address_response(address):
    google_maps_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'address': address,
              'key': config['gmaps_key']}

    response = requests.get(google_maps_url, params=params)
    return response.json()


def extract_gmaps_data(response):
    resp = response['results'][0]
    addr_comp = ['street_number', 'route', 'locality', 'postal_code',
                 'administrative_area_level_1', 'administrative_area_level_2']
    res = {}
    for c in resp['address_components']:
        for a_c in addr_comp:
            if a_c in c['types']:
                res[a_c] = c['long_name']
    res['lat'] = resp['geometry']['location']['lat']
    res['lng'] = resp['geometry']['location']['lng']
    return res


def extract_ads(area, new_ad, new_building, property_type, verbose, min_wait,
                max_wait, max_pages):
    url = compose_url(area, new_ad, new_building, property_type)

    ad_tiles = extract_ad_tiles(url, min_wait, max_wait, max_pages)
    for ad in ad_tiles:
        tile_details = extract_tile_details(ad, new_building)
        addr = tile_details['address_short']
        gmaps_json = get_gmaps_address_response(addr)
        print('\n' * 2)


if __name__ == '__main__':
    import argparse
    parser = argparse.\
        ArgumentParser(description='Run the housing data extractor')

    parser.add_argument('--area',
                        help='Comma separated area names',
                        type=str,
                        default='oslo')
    parser.add_argument('--new_ad',
                        help='Get only new ads',
                        type=bool,
                        default=True)
    parser.add_argument('--new_building',
                        help='Get only ads for new structures',
                        type=bool,
                        default=False)
    parser.add_argument('--property_type',
                        help='Comma separated property types',
                        type=str,
                        default='detached,semi_detached,apartment,terraced')
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
    extract_ads(args.area, args.new_ad, args.new_building, args.property_type,
                args.verbose, args.min_wait, args.max_wait, args.max_pages)
