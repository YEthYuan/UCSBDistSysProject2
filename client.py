import os
import sys

from client_utils import Client
from utils import *


def main():
    config_path = input("Input the path of config file: [./config.yaml]")
    if config_path == "":
        config_path = "./config.yaml"
    config = load_internet_config(config_path)
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

    pid = os.getpid()

    # sleep=-1 := sleep=rand(0,3)
    client = Client(pid=pid, username=username, config=config, sleep=3)

    while True:
        clear_screen()
        print(f" --- Client {username} Interface --- ")
        print(f" < PID: {pid} Clock: {client.get_current_clock()} Balance: {client.get_current_balance()} Step: {client.get_current_step()}> \n")
        print("1. Get Current Balance")
        print("2. Make Transaction")
        print("3. Print the Current Blockchain")
        print()
        print("7: [DEBUG] Manually broadcast fake request")
        print("8: [DEBUG] Manually broadcast fake release")
        print("9: [DEBUG] Change My Clock")
        print("0. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            client.send_balance_inquery()
            print('=' * 30)
            print("Press enter to continue. ")
            input()
        elif choice == '2':
            to = input("Send money to: ")
            amount = input("Amount: ")
            client.transact(amount=int(amount), to=to)
            print('=' * 30)
            print("Press enter to continue. ")
            input()
        elif choice == '3':
            client.print_blockchain()
            print('=' * 30)
            print("Press enter to continue. ")
            input()
        elif choice == '7':
            client.send_fake_request()
            print('=' * 30)
            print("Press enter to continue. ")
            input()
        elif choice == '8':
            client.send_fake_release()
            print('=' * 30)
            print("Press enter to continue. ")
            input()
        elif choice == '9':
            new_clock = input("Set my clock to: ")
            client.manually_modify_clock(int(new_clock))
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


if __name__ == '__main__':
    main()
