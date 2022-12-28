# method to append a line to a file given a directory
def add_this_ssid_to_log(line):
    directory = r"C:\Users\matmi\OneDrive\Desktop\ssid_account_index_log.txt"
    with open(directory, "a") as file:
        file.write(line + "\n")


add_this_ssid_to_log("pafghth")
