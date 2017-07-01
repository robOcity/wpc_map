'''
This program downloads historical weather maps from the Weather Prediction Center (WPC)
that is part of the National Weather Service.  Surface weather maps for North America and CONUS 
are available from May 1, 2005 onward.  Eight different kinds of maps are available at eight 
differnt times per day.  This program will allow you to download one type of map for a range
of dates, and store the maps in a folder.
'''

import requests
from bs4 import BeautifulSoup
from dateutil import parser
import iso8601   # sane and scientific time parsing
import datetime
import argparse
import click
import sys


def build_url(date_and_time, maptype):
    """
    Builds to url to load the surface weather map. 
    """
    site_url = 'http://www.wpc.ncep.noaa.gov/'
    page_url = 'archives/web_pages/sfc/sfc_archive_maps.php?'
    year, month, day, hour = date_and_time.year, date_and_time.month, date_and_time.day, date_and_time.hour
    return f'{site_url}{page_url}arcdate={month:02d}/{day:02d}/{year}&selmap={year}{month:02d}{day:02d}{hour}&maptype={maptype}'


def make_iso_date(date_str, time='00'):
    """
    Creates and parses an ISO8601 compliant date string into a datetime object.  
    All times are in Universal Coordinated Time (UTC) which is commonly referred to a Z or 'Zulu'. 
    date = Valid date strings that have the form: YYYY-MM-DD or YYYYMMDD.
    time = Valid times include: 00, 06, 12, 18
    """
    iso_str = date_str + 'T' + time + 'Z'
    return iso8601.parse_date(iso_str)


def build_time_series(begin, end, times):
    """
    Builds the series of datetime objects for the period of interest.
    """
    # create the starting and ending datetime objects using values provided on the command line 
    start_dt = make_iso_date(begin)
    stop_dt = make_iso_date(end)
    num_days = (stop_dt - start_dt).days  # timedelta object has a days attribute

    # reality check
    if start_dt > stop_dt:
        return []

    # build a list of datetime objects by adding incremental day and time offsets to the start date
    # note: range(value) is generates values from 0 to value - 1, therefore adding 1
    return [start_dt + datetime.timedelta(days=d, hours=int(t)) for d in range(num_days+1) for t in times]


def scrape_map(begin, end, times, maps):
    pass


# TODO 0. Check into git
# TODO 1. Get app working
# TODo 2. Add type hints
# TODO 3Test bad / missing input values
# TODO 4. Update documentation
# TODO 5. Add a Readme.rst
# TODO 6. Check into github
# TODO 7. Have a beer
def main():
    pass


# TODO Click can't handle sequences with unknown length, consider alternaitives
# TODO Get Click command line working
# TODO Create a python package structure
# @click.command()
# @click.option('-b', '--begin', help='Starting date as YYYY-MM-DD or YYYYMMDD format. ')
# @click.option('-e', '--end',   help='Ending date as YYYY-MM-DD or YYYYMMDD format')
# @click.option('-t', '--times', multiple=True, help='Time(s) UTC or Z for weather map(s) (00, 06, 12, 18)')
# @click.option('-m', '--maps',  multiple=True, help='Type(s) of surface weather maps to download (namussfc, usfntsfc, print_us, ussatsfc, radsfcus_exp, namfntsfc, na_zoomin, satsfcnps)')
# def main():
#     """
#     This program downloads archived surface weather maps for a range of dates and times from the
#     Weather Prediction Center (part of the National Weather Service).
#     """
#     dt_series = build_time_series(begin, end, times)
#     scrape_map(begin, end, times, maps)


if __name__ == '__main__':
    main()
