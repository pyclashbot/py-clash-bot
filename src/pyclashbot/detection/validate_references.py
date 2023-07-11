"""A script to validate the reference images"""
from os.path import dirname, join
from os import listdir
from pyclashbot.utils.image_handler import open_image


def validate_references():
    """Method to validate the reference images"""
    reference_folder = join(dirname(__file__), "reference_images")
    valid = []
    invalid = []
    for folder in listdir(reference_folder):
        for image in listdir(join(reference_folder, folder)):
            try:
                print(f"Validating image {image}")
                open_image(join(reference_folder, folder, image))
                print(f"\tImage {image} is valid")
                valid.append(image)
            except Exception as err:  # pylint: disable=broad-except
                print(f"\tImage {image} is not valid")
                print(f"\t{err}")
                invalid.append(image)
    print(f"Validated {len(valid)} images")
    print(f"Failed to validate {len(invalid)} images")


if __name__ == "__main__":
    validate_references()
