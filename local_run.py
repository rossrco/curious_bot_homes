import pandas as pd
from google.cloud import bigquery
from code import utils


bq = bigquery.Client()


def run(area, new_ad, property_type, verbose, min_wait, max_wait, max_pages):
    run_res = []

    for p in property_type.split(','):
        run_res += utils.extract_ads(area, new_ad, p, verbose, min_wait,
                                     max_wait, max_pages)

    res_df = pd.DataFrame(run_res)
    res_df.to_csv('result.csv', index=False)


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

    run(args.area, args.new_ad, args.property_type, args.verbose,
        args.min_wait, args.max_wait, args.max_pages)
