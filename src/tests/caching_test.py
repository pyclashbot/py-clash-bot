import unittest
from os.path import join
from tempfile import TemporaryDirectory

from pyclashbot.utils.caching import _cache_data, _load_data

iterations = 50000


class CachingTest(unittest.TestCase):
    def test_cache_and_load_data(self):
        # create a temporary file for this test
        test_name = "cache_and_load_data.json"
        with TemporaryDirectory() as temp_dir:
            test_f = join(temp_dir, test_name)
            # demo data dict:
            demo = {"test": "test"}
            # cache data
            _cache_data(demo, test_f)
            # load data
            self.assertEqual(_load_data(test_f), demo)

    def test_no_load_data(self):
        self.assertEqual(_load_data("test_no.json"), {})

    def test_changed_cache_and_load_data(self):
        # testing if the cache data method overwrites the data
        test_name = "changed_cache_and_load_data.json"
        with TemporaryDirectory() as temp_dir:
            test_f = join(temp_dir, test_name)
            # demo data dict:
            demo = {"test": "test"}
            # cache data
            _cache_data(demo, test_f)
            # load data
            self.assertEqual(_load_data(test_f), demo)
            # change data
            demo["test"] = "test2"
            # cache data
            _cache_data(demo, test_f)
            # load data
            self.assertEqual(_load_data(test_f), demo)

    def test_malformed_cache_and_load_data(self):
        # testing if the load data method can handle malformed data
        test_name = "malformed_cache_and_load_data.json"
        with TemporaryDirectory() as temp_dir:
            test_f = join(temp_dir, test_name)
            # cache data
            _cache_data({"test": "test"}, test_f)

            # change the file to be malformed
            with open(test_f, "r+", encoding="utf-8") as f:
                f.seek(0, 0)
                f.write("{")

            # load data
            self.assertEqual(_load_data(test_f), {})
