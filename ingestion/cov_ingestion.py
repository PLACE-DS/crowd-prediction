"""cov_ingestion.py: Collects COVID-19 stringency data from covidtracker
 between [start_date] and [end_date] for [country]
 https://covidtracker.bsg.ox.ac.uk/about-api"""

__author__ = "@emielsteegh"
__version__ = "0.0.1"

######################################
# run from project root with
# > python ingestion/cov_ingestion.py --help

import requests
import datetime
import pandas as pd
import os
import click

sensor_start = "2020-08-31"
today = datetime.date.today().strftime("%Y-%m-%d")


@click.command()
@click.option('--country', default="NLD", help='country to collect from in alpha-3 (default NLD).')
@click.option('--start_date', default=sensor_start, help='starting date as YYYY-MM-DD (default 2020-08-32)')
@click.option('--end_date', default=today, help='end date as YYYY-MM-DD (default today)')
def cov_ingestion(country, start_date, end_date):
    request = f"https://covidtrackerapi.bsg.ox.ac.uk/api/v2/stringency/date-range/{start_date}/{end_date}/"

    response = requests.get(request)

    json = response.json()

    rows = []
    for date in json["data"]:
        rows.append(json["data"][date][country])

    df = pd.DataFrame(rows)

    outname = f'cov_{country.lower()}_raw.csv'
    outdir = os.path.join('data', 'raw')
    fullpath = os.path.join(outdir, outname)

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    df.to_csv(fullpath)


if __name__ == "__main__":
    cov_ingestion()
