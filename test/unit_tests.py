import wx_map
from datetime import datetime, timezone


def test_create_url():
    dt = datetime(year=2017, month=6, day=1, hour=12, tzinfo=timezone.utc)
    maptype = 'usfntsfc'
    expected = 'http://www.wpc.ncep.noaa.gov/archives/web_pages/sfc/sfc_archive_maps.php?arcdate=06/01/2017&selmap=2017060112&maptype=usfntsfc'
    assert (wx_map._build_page_url(dt, maptype)) == expected


def test_make_iso_date():
    y = 2017; m = 6; d = 28; h = 18
    date_str = f'{y:04d}-{m:02d}-{d:02d}'
    time_str = f'{h:02d}'
    expected = datetime(year=y, month=m, day=d, hour=h, tzinfo=timezone.utc)
    assert (wx_map._make_iso_date(date_str, time_str)) == expected


def test_build_no_time_series():
    # start is later in time than stop
    start = '2017-01-01'
    stop = '2016-12-31'
    times = []
    assert (wx_map._make_time_series(start, stop, times)) == []


def test_build_time_series():
    start = '2016-12-31'
    stop = '2017-01-01'
    times = [0, 6, 18]
    assert (len(wx_map._make_time_series(start, stop, times))) == 6


def test_short_build_time_series():
    start = '2017-01-01'
    stop = '2017-01-01'
    times = ['06', '18']
    actual = wx_map._make_time_series(start, stop, times)
    start_dt = wx_map._make_iso_date(start, times[0])
    stop_dt = wx_map._make_iso_date(stop, times[1])
    assert(len(actual)) == 2
    assert(start_dt in actual)
    assert(stop_dt in actual)


def test_page_url():
    expected = 'http://www.wpc.ncep.noaa.gov/archives/web_pages/sfc/sfc_archive_maps.php?arcdate=06/15/2017&selmap=2017061521&maptype=usfntsfc'
    date_str = '2017-06-15'
    time_str = '21'
    date_time = wx_map._make_iso_date(date_str, time_str=time_str)
    assert (wx_map._build_page_url(date_time, 'usfntsfc')) == expected


def test_map_path():
    expected = '/Users/rob/Downloads/wx_maps/20170601_12z_namussfc.gif'
    dt = datetime(year=2017, month=6, day=1, hour=12, tzinfo=timezone.utc)
    maptype = 'namussfc'
    assert (wx_map._get_map_path('~/Downloads/wx_maps', dt, maptype)) == expected


def test_build_image_url():
    expected = 'http://www.wpc.ncep.noaa.gov/archives/sfc/2017/namussfc2017060112.gif'
    dt = datetime(year=2017, month=6, day=1, hour=12, tzinfo=timezone.utc)
    maptype = 'namussfc'
    page_url = wx_map._build_page_url(dt, maptype)
    assert (wx_map._build_image_url(page_url)) == expected
