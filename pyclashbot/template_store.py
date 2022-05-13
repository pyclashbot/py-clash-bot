import bz2
from io import BufferedReader
import pickle
from PIL.Image import Image


class TemplateStore:
    """
    This class handles interactions with the template store.
    Templates will be stored as a compressed pickle to reduce application size.
    """

    def __init__(self, store_name="store"):
        """TemplateStore init

        Args:
            store_name (str, optional): name of store file. Defaults to "store".
        """
        self.store_name = store_name
        self.template_store = self.open_store()

    def add_templates(self, template_dict: dict[str, Image]):
        """add templates to the store

        Args:
            template_dict (dict[str, Image]): a dictionary of strings and PIL Images
        """
        # make template store if none
        if self.template_store is None:
            self.template_store = template_dict
            self.save_store()
        else:
            # update store with new dict
            self.template_store.update(template_dict)
            self.save_store()

    def remove_template(self, template_name):
        """removes a template from the store by name

        Args:
            template_name (str): name of template to remove
        """
        if self.template_store is not None:
            # remove element from dict and update store
            self.template_store.pop(template_name)
            self.save_store()

    def open_store(self):
        """opens a store file and returns the contents

        Returns:
            dict[str, Image]: a dictionary of strings and PIL Images
        """

        try:
            with open(self.store_name, 'rb') as store_file:
                return self.decompress_pickle(store_file)
        except:
            return None

    def save_store(self):
        """writes template_dict to store file
        """
        self.compressed_pickle(self.store_name, self.template_store)

    def get_template(self, template_name):
        """returns template from store

        Args:
            template_name (str): the name of the template

        Returns:
            Image: the template image
        """
        if self.template_store is not None:
            return self.template_store[template_name]
        else:
            return None

    def compressed_pickle(self, title, data: dict):
        """saves data as a pickle and compresses

        Args:
            title (str): name of pickle
            data (Any): data to store
        """
        # Pickle a file and then compress it into a file with extension

        with bz2.BZ2File(title, 'w') as f:
            pickle.dump(data, f)

    def decompress_pickle(self, file: BufferedReader):
        """opens and decompresses pickle

        Args:
            file (BufferedReader): a file to decompress

        Returns:
            Any: the stored data
        """
        # Load any compressed pickle file
        data = bz2.BZ2File(file, 'rb')
        data = pickle.load(data)
        return data
