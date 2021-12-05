"""knmi_ingestion.py: Collects weather data from the KNMI
 between [start_date] and [end_date] for [station]
 https://www.knmi.nl/kennis-en-datacentrum/achtergrond/data-ophalen-vanuit-een-script"""

__author__ = "@emielsteegh"
__version__ = "0.0.1"

######################################
# run from project root with
# > python ingestion/knmi_ingestion.py (--help)

import requests
import datetime
import csv
import os
import click

sensor_start = "2020-08-31"
today = datetime.date.today().strftime("%Y-%m-%d")


@click.command()
@click.option('--station', default="240", help='station code to collect from as listed by KNMI (default 240).')
@click.option('--start_date', default=sensor_start, help='starting date as YYYY-MM-DD (default 2020-08-32)')
@click.option('--end_date', default=today, help='end date as YYYY-MM-DD (default today)')
def knmi_ingestion(station, start_date, end_date):
    start_time = start_date.replace('-', '') + '01'  # starting hours for each day
    end_time = end_date.replace('-', '') + '24'  # last hour of each day
    fmt = 'csv'

    url = "https://www.daggegevens.knmi.nl/klimatologie/uurgegevens/"
    params = {
        "stns": station,
        "start": start_time,
        "end": end_time,
        "fmt": fmt
    }

    outname = f'knmi_raw.csv'
    outdir = os.path.join('data', 'raw')
    fullpath = os.path.join(outdir, outname)
    commentpath = os.path.join(outdir, 'knmi_comment.txt')

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    download = requests.post(url, data=params)

    with open(fullpath, 'w') as f:
        # create the csv writer
        writer = csv.writer(f)

        with requests.Session() as s:
            download = s.post(url, data=params, stream=True)
            download_iter = download.iter_lines()

            # the following section deals with the comment header in the obtained csv file
            next_row = next(download_iter).decode('utf-8')
            header_row = next_row
            header_comment = ""

            # keep checking until we hit the first actual row
            while '#' in next_row:
                header_comment += next_row + '\n'
                header_row = next_row
                next_row = next(download_iter).decode('utf-8')

            with open(commentpath, "w") as text_file:
                text_file.write(header_comment)

            # the actual header is a comment, so we want to write that one
            writer.writerow(header_row[1:].split(','))
            writer.writerow(next_row.split(','))  # and this one bc the iterator hit it

            for line in download_iter:
                row = line.decode('utf-8')
                writer.writerow(row.split(','))


if __name__ == "__main__":
    knmi_ingestion()
