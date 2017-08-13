import os

from click.testing import CliRunner

from wpc_map import cli


def test_scrape_map(tmpdir):
    # create a sequence of events with two occurrences on two days
    start, end, period, maps, map_dir = '2017-07-04', '2017-07-04', '24', ['namussfc'], tmpdir
    dates = [date for date in cli._make_time_series(start, end, period)]

    # create the unique file names for each map and time
    paths = [cli._get_map_path(tmpdir, date, _map)
             for date in dates
             for _map in maps]

    # get the maps
    runner = CliRunner()
    result = runner.invoke(cli.get, ['-s', start, '-e', end, '-p', period, '-m', 'namussfc', '-d', os.path.abspath(tmpdir)])

    # perform tests
    _check_numbers(paths, tmpdir)
    _check_files_exist(paths)


def test_scrape_map_sequence(tmpdir):
    # create a sequence of events with two occurrences on two days
    start, end, period, maps, map_dir = '2017-06-30', '2017-07-01', '12', ['usfntsfc', 'ussatsfc'], tmpdir
    dates = [date for date in cli._make_time_series(start, end, period)]

    # create the unique file names for each map and time
    paths = [cli._get_map_path(tmpdir, date, _map)
             for date in dates
             for _map in maps]

    runner = CliRunner()
    result = runner.invoke(cli.get, ['-s', start, '-e', end, '-p', period, '-m', maps[0], '-m', maps[1], '-d', os.path.abspath(tmpdir)])

    # perform tests
    _check_numbers(paths, tmpdir)
    _check_files_exist(paths)


def _check_files_exist(paths):
    for path in paths:
        assert (os.path.exists(path))


def _check_numbers(expected, tmpdir):
    actual_maps = tmpdir.listdir()
    assert (len(actual_maps)) == len(expected)
