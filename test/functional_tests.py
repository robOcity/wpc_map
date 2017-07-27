import get_map as wpc
import os


def test_scrape_map(tmpdir):
    # create a sequence of events with two occurrences on two days
    expected, paths = _scrape_maps('2017-07-04', '2017-07-04', '24', ['namussfc'], tmpdir)

    # perform tests
    _check_numbers(expected, paths, tmpdir)
    _check_files_exist(paths)


def test_scrape_map_sequence(tmpdir):
    # create a sequence of events with two occurrences on two days
    expected, paths = _scrape_maps('2017-06-30', '2017-07-01', '12', ['usfntsfc', 'ussatsfc'], tmpdir)

    # perform tests
    _check_numbers(expected, paths, tmpdir)
    _check_files_exist(paths)


def _scrape_maps(tmpdir, start, stop, times, maps):
    # create a sequence of events with two occurrences on two days
    dates = [date for date in wpc._make_time_series(start, stop, times)]

    # create the unique file names for each map and time
    paths = [wpc._get_map_path(tmpdir, date, map)
             for date in dates
             for map in maps]
    wpc.cli(start, stop, times, maps, tmpdir)
    expected_num = len(dates) * len(maps)
    return expected_num, paths


def _check_files_exist(paths):
    for path in paths:
        assert (os.path.exists(path))


def _check_numbers(expected, paths, tmpdir):
    assert (len(paths)) == expected
    assert (len(tmpdir.listdir())) == expected


