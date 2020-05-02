import logging
from distutils.util import strtobool
import yaml
from flask import Flask, request
import pandas as pd
from google.cloud import bigquery
import utils


with open('config.yaml', 'r') as config_file:
    config = yaml.load(config_file, Loader=yaml.SafeLoader)


bq = bigquery.Client()


app = Flask(__name__)


@app.route('/homes_no')
def run():
    area = request.args.get('area', default='oslo', type=str)
    new_ad = strtobool(request.args.get('new_ad', default='True', type=str))
    property_type = request.args.get('property_type',
                                     default='detached,semi_detached,'
                                             'apartment,terraced',
                                     type=str)
    verbose = request.args.get('verbose', default=True, type=bool)
    min_wait = request.args.get('min_wait', default=1, type=int)
    max_wait = request.args.get('max_wait', default=2, type=int)
    max_pages = request.args.get('max_pages', default=1, type=int)

    run_res = []
    for p in property_type.split(','):
        print(f'Extracting ads for {area}, {p}.')
        run_res += utils.extract_ads(area, new_ad, p, verbose, min_wait,
                                     max_wait, max_pages)

    res_df = pd.DataFrame(run_res)
    for c in ['viewed', 'detail_seen']:
        res_df[c] = pd.to_datetime(res_df[c])
    res_df.drop_duplicates(inplace=True)
    res_df.to_gbq(destination_table=config['bq_dest'],
                  project_id=config['project_id'],
                  if_exists='append')
    return 'Records inserted'


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=logging.INFO)

    app.run(host='127.0.0.1', port=8080, debug=True)
