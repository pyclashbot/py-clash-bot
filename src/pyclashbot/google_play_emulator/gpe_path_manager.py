import json
import os
import FreeSimpleGUI as sg
import webbrowser


def read_json_file(file_path: str) -> dict:
    """
    Reads a JSON file and returns its content as a dictionary.
    If the file does not exist, returns an empty dictionary.
    """
    if not os.path.exists(file_path):
        return {}

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def set_path_popup():
    """
    Displays a popup to set the Google Play Emulator path.
    """
    layout = [
        [sg.Text("Please set the Google Play Emulator path:")],
        [sg.InputText(key="gpe_path_input")],
        [sg.Button("Set Path"), sg.Button("Cancel")],
    ]

    window = sg.Window("Set GPE Path", layout, modal=True)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Cancel"):
            break
        elif event == "Set Path":
            new_path = values["gpe_path_input"]
            if new_path:
                gpe_manager = GPEPathManager()
                gpe_manager.set_emulator_path(new_path)
                sg.popup("Path set successfully!")
                break

    window.close()

def show_invalid_gpe_path_popup() -> None:
    gpe_manager = GPEPathManager()

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
        [sg.Button("Open Install Link"),
         sg.Button('Continue Anyway'),
         sg.Button('Set GPE Path'),
         ],
    ]

    window = sg.Window("Invalid GPE Path Attribute", layout, modal=True)

    while True:
        event, _ = window.read()
        if event in (sg.WIN_CLOSED, "Continue Anyway"):
            break
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
        # self.default_path = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Google Play Games Developer Emulator\Google Play Games Developer Emulator.lnk"
        self.default_path = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Google Play Games Developer Emulator\Google Play Games Developer Emulator.lnk"
        self.json_path = r"gpe_info.json"

    def get_emulator_path(self):
        if os.path.exists(self.json_path):
            content = read_json_file(self.json_path)
            if "emulator_path" in content:
                path = content["emulator_path"]
                if os.path.exists(path) and 'Google Play Games Developer Emulator' in path:
                    print(f'GPEPathManager found a valid saved path: "{path}"')
                    return path

        if os.path.exists(self.default_path):
            print(f'GPEPathManager found a valid default path: "{self.default_path}"')
            return self.default_path

        print(f"GPEPathManager did not find a valid path.")
        show_invalid_gpe_path_popup()
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
