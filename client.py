import os
import platform
import sys

import yaml

from client_utils import Client


def main():
    config_path = input("Input the path of config file: [./config.yaml]")
    if config_path == "":
        config_path = "./config.yaml"
    config = load_config(config_path)
    usr_list = []
    for item in config['clients']:
        usr_list.append(item['username'])

    while True:
        print("Username List: ", usr_list)
        username = input("Input a username to start: ")
        if username in usr_list:
            break
        else:
            print("Input Username Must in the configuration file! Press enter to continue.")
            input()
            clear_screen()

    # sleep=-1 := sleep=rand(0,3)
    client = Client(username=username, config_path=config_path, sleep=3)

    while True:
        clear_screen()
        print(f" --- Client {username} Interface --- ")
        print("1. Assign Token")
        print("2. Initiate Snapshot")
        print("3. Modify Lose Probability")
        print()
        print("0. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            client.assign_token()
            print('=' * 30)
            print("Press enter to continue. ")
            input()
        elif choice == '2':
            client.launch_snapshot()
            print('=' * 30)
            print("Press enter to continue. ")
            input()
        elif choice == '3':
            new_prob = input("Type in the new token lose probability (%): ")
            client.modify_lose_prob(int(new_prob))
            print('=' * 30)
            print("Press enter to continue. ")
            input()
        elif choice == '0':
            client.stop_udp()
            print("Bye!")
            exit(1)
        else:
            print("Invalid choice. Press enter to continue.")
            input()


def load_config(path: str) -> dict:
    with open(path, 'r') as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    return config


def clear_screen():
    os_type = platform.system().lower()
    if os_type == 'linux' or os_type == 'darwin':
        os.system('clear')  # for linux/macOS
    elif os_type == 'windows':
        os.system('cls')  # for Windows
    else:
        print("Unsupported operating system! Unable to clear the screen!")


if __name__ == '__main__':
    main()
