import wpc_map_scraper


# TODO add setup and teardown behavior that creates and deletes a temporary test directory

def test_scraper_map():
    start = '2017-06-10'
    stop = '2017-06-11'
    times = ['00']
    map_types = ['usfntsfc']
    map_dir = '~/Desktop/Weather_Maps'
    actual = wpc_map_scraper.scrape_map(start, stop, times, map_types, map_dir)
    assert(actual is True)
    # TODO test for presence of map file in temp directory
    # TODO test that the file is not zero-sized


# TODO add a test that downloads multiple types of maps
# TODO add a test that downloads for many different times
# TODO add a test that downloads multiple days
