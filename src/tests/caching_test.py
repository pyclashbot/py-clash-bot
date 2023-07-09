import unittest
from os.path import join
from tempfile import TemporaryDirectory

from pyclashbot.utils.caching import _cache_data, _load_data

iterations = 50000


class CachingTest(unittest.TestCase):
    def test_cache_and_load_data(self):
        # create a temporary file for this test
        test_name = "cache_and_load_data.dat"
        with TemporaryDirectory() as temp_dir:
            test_f = join(temp_dir, test_name)
            # cache data
            _cache_data("test", test_f)
            # load data
            self.assertEqual(_load_data(test_f), "test")

    def test_no_load_data(self):
        self.assertEqual(_load_data("test_no.dat"), None)

    def test_changed_cache_and_load_data(self):
        # testing if the cache data method overwrites the data
        test_name = "changed_cache_and_load_data.dat"
        with TemporaryDirectory() as temp_dir:
            test_f = join(temp_dir, test_name)
            # cache data
            _cache_data("test", test_f)
            # load data
            self.assertEqual(_load_data(test_f), "test")
            # cache data
            _cache_data("test2", test_f)
            # load data
            self.assertEqual(_load_data(test_f), "test2")

    def test_malformed_cache_and_load_data(self):
        # testing if the load data method can handle malformed data
        test_name = "malformed_cache_and_load_data.dat"
        with TemporaryDirectory() as temp_dir:
            test_f = join(temp_dir, test_name)
            # cache data
            _cache_data("bad_test", test_f)

            # change every 3rd byte to 1
            with open(test_f, "rb+") as f:
                f.seek(2)
                while True:
                    f.write(b"\x01")
                    f.seek(3, 1)
                    if f.tell() >= f.seek(0, 2):
                        break

            # load data
            self.assertEqual(_load_data(test_f), None)
