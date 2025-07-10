import json
import os
import webbrowser

import FreeSimpleGUI as sg


def read_json_file(file_path: str) -> dict:
    """
    Reads a JSON file and returns its content as a dictionary.
    If the file does not exist, returns an empty dictionary.
    """
    if not os.path.exists(file_path):
        return {}

    with open(file_path, encoding="utf-8") as file:
        return json.load(file)


def set_path_popup():
    """
    Displays a popup with a folder browser to set the Google Play Emulator path.
    """
    layout = [
        [
            sg.Text(
                "Please select the Google Play Emulator installation file (Google Play Games Developer Emulator.lnk):"
            )
        ],
        [
            sg.InputText(key="gpe_path_input", enable_events=True),
            sg.FileBrowse("Browse"),
        ],
        [sg.Button("Set Path"), sg.Button("Cancel")],
    ]

    window = sg.Window("Set GPE Path", layout, modal=True)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Cancel"):
            break
        elif event == "Set Path":
            new_path = values["gpe_path_input"]
            if new_path and os.path.isfile(new_path):
                gpe_manager = GPEPathManager()
                gpe_manager.set_emulator_path(new_path)
                sg.popup("Path set successfully!")
                break
            else:
                sg.popup_error("Invalid file selected. Please choose a valid directory.")

    window.close()


def show_invalid_gpe_path_popup():
    layout = [
        [sg.Text("Warning! Your Google Play Emulator path is invalid.")],
        [sg.Text("Install Google Play Emulator from:")],
        [
            sg.Text(
                "https://developer.android.com/games/playgames/emulator",
                text_color="blue",
            )
        ],
        [
            sg.Text(
                "If you have already installed it, please set the correct\npath using the home page's 'Set GPE Path' button."
            )
        ],
        [
            sg.Button("Open Install Link"),
            sg.Button("Continue Anyway"),
            sg.Button("Set GPE Path"),
        ],
    ]

    window = sg.Window("Invalid GPE Path Attribute", layout, modal=True)

    while True:
        event, _ = window.read()
        if event in (sg.WIN_CLOSED, "Continue Anyway"):
            window.close()
            return False
        elif event == "Open Install Link":
            webbrowser.open("https://developer.android.com/games/playgames/emulator")
        elif event == "Set GPE Path":
            set_path_popup()
            break

    window.close()


class GPEPathManager:
    """
    Manages paths for the Google Play Emulator.
    """

    def __init__(self):
        self.json_path = r"gpe_info.json"

    def check_for_default_locations(self):
        default_base_paths = [
            char + r":\ProgramData\Microsoft\Windows\Start Menu\Programs\Google Play Games Developer Emulator"
            for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        ]

        for default_based_path in default_base_paths:
            if os.path.exists(default_based_path):
                for root, dirs, files in os.walk(default_based_path):
                    for file in files:
                        if "google" in file.lower() and ".lnk" in file.lower():
                            full_path = os.path.join(root, file)
                            print(f"Found GPE shortcut at: {full_path}")
                            return full_path

        return None

    def get_emulator_path(self):
        if os.path.exists(self.json_path):
            content = read_json_file(self.json_path)
            if "emulator_path" in content:
                path = content["emulator_path"]
                if os.path.exists(path) and (".exe" in path or ".lnk" in path):
                    print(f'GPEPathManager found a valid saved path: "{path}"')
                    return path

        default_path = self.check_for_default_locations()
        if default_path:
            print(f'GPEPathManager found a valid default path: "{default_path}"')
            return default_path

        print("GPEPathManager did not find a valid path.")
        if show_invalid_gpe_path_popup() is False:
            print('User clicked "Continue Anyway" without setting a path.')
            return None

        # otherwise retry
        return self.get_emulator_path()

    def set_emulator_path(self, new_path: str):
        existing_content = read_json_file(self.json_path)
        existing_content["emulator_path"] = new_path
        with open(self.json_path, "w", encoding="utf-8") as file:
            json.dump(existing_content, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    manager = GPEPathManager()
    path = manager.get_emulator_path()
    print(f"Current emulator path: {path}")
