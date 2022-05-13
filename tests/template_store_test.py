import unittest
from PIL import Image
from pyclashbot.template_store import TemplateStore


class TemplateStoreTest(unittest.TestCase):
    def test_adding_images(self):
        # make test store
        ts = TemplateStore("tests/assets/TestStore")
        # define template dict and open images
        td = {
            "clashtemp": Image.open("tests/assets/clashtemp.png"),
            "pass_template": Image.open("tests/assets/pass_template.png"),
            "fail_template": Image.open("tests/assets/fail_template.png")
        }
        # save template dict to store
        ts.add_templates(td)
        # read images from store and compare
        for name in td:
            # if image is not the same as in original dict, fail
            self.assertTrue(td[name] == ts.get_template(name))

        # pass if no fails
        self.assertTrue(True)

    def test_removing_images(self):
        # make test store
        ts = TemplateStore("tests/assets/TestStore")
        # define template dict and open images
        td = {
            "clashtemp": Image.open("tests/assets/clashtemp.png"),
            "pass_template": Image.open("tests/assets/pass_template.png"),
            "fail_template": Image.open("tests/assets/fail_template.png")
        }
        # save template dict to store
        ts.add_templates(td)
        # remove template from store and list
        ts.remove_template("fail_template")
        td.pop("fail_template")
        # read images from store and compare
        for name in td:
            # if image is not the same as in original dict, fail
            self.assertTrue(td[name] == ts.get_template(name))
        # pass if no fails
        self.assertTrue(True)
