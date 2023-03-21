from parse import parse_input
from db_handler import DBConnection


if __name__ == "__main__":
    print("--------------------------------------------------")
    print("Welcome to the Query Interface!")
    print("--------------------------------------------------")
    print("Start by entering \"LOAD DATA\" into the prompt!")
    print("--------------------------------------------------")
    print("Then type \"HELP\" to view commands!")
    print("--------------------------------------------------")
    conx = DBConnection()
    # Continue taking user input until they decide to exit
    user_command = input("Enter a command: ")
    if user_command.upper() != "EXIT":
        while user_command.upper() != "EXIT":
            parse_input(conx, user_command)
            user_command = input("Enter a command: ")
        # Close the database connection before exiting
        conx.close_connection()
