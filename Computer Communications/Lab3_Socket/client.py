'''
Abraham Soclof 
674098915
Lab 3
client.py

As a Mac user, it is necessary to use the curses library instead of msvcrt 
for handling console input and output in the terminal. 
This library is appropriate for Unix-like operating systems, including macOS, 
and provides capabilities to create text-based user interfaces.
'''

import socket
import curses
import select
import sys
import chat_protocol

def create_client_name(data):
    """
    Create a name setting command.
    """
    if len(data.split()) != 2:
        return chat_protocol.RESPONSE_STRINGS[chat_protocol.INVALID_NAME_FORMAT]
    return f"{chat_protocol.NAME_COMMAND} {data.split()[1]}"

def create_client_get_names(command):
    """
    Create a get names command.
    """
    if len(command.split()) != 1:
        return chat_protocol.RESPONSE_STRINGS[chat_protocol.INVALID_GET_NAMES_FORMAT]
    return f"{chat_protocol.GET_NAMES_COMMAND}"

def create_client_message(data):
    """
    Create a message sending command.
    """
    if len(data.split()) != 3:
        return chat_protocol.RESPONSE_STRINGS[chat_protocol.INVALID_MESSAGE_FORMAT]
    return f"{chat_protocol.MSG_COMMAND} {data.split()[1]} {data.split(maxsplit=2)[2]}"

def create_exit_message(command, my_socket, scr):
    """
    Create an exit command and close the connection.
    """
    if len(command.split()) != 1:
        return chat_protocol.RESPONSE_STRINGS[chat_protocol.INVALID_EXIT_FORMAT]
    chat_protocol.send_message(my_socket, str(chat_protocol.EXIT_COMMAND))
    my_socket.close()
    scr.addstr("Exiting...\n")
    scr.refresh()
    curses.endwin()
    exit()

def safe_addstr(scr, data):
    """
    Safely add a string to the curses window, handling line wrapping.
    """
    max_y, max_x = scr.getmaxyx()
    lines = data.splitlines()
    for line in lines:
        for i in range(0, len(line), max_x):
            scr.addstr(line[i:i+max_x] + "\n")

def handle_server_shutdown(scr):
    """
    Handle server shutdown and close the client.
    """
    scr.addstr("Server is shutting down. Exiting...\n")
    scr.refresh()
    curses.endwin()
    exit()

def main(scr):
    """
    Main function to run the client.
    """
    try:
        curses.echo()
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_ip = "127.0.0.1"
        server_port = 7777
        my_socket.connect((server_ip, server_port))

        message = chat_protocol.receive_message(my_socket)
        if message:
            safe_addstr(scr, message)
            scr.refresh()

        while True:
            ready_to_read, _, _ = select.select([my_socket, sys.stdin], [], [], 0)
            
            for s in ready_to_read:
                if s == my_socket:
                    # Handle incoming message from the server
                    try:
                        data = chat_protocol.receive_message(my_socket)
                        if data:
                            if data == chat_protocol.RESPONSE_STRINGS[chat_protocol.EXIT]:
                                handle_server_shutdown(scr)
                            safe_addstr(scr, data)
                            scr.refresh()
                    except ConnectionResetError:
                        handle_server_shutdown(scr)
                elif s == sys.stdin:
                    # Handle user input
                    scr.refresh()
                    command = scr.getstr().decode()

                    if command.strip() == "":
                        continue
                    if command.startswith(chat_protocol.COMMAND_STRINGS[chat_protocol.NAME_COMMAND]):
                        message = create_client_name(command)
                    elif command.startswith(chat_protocol.COMMAND_STRINGS[chat_protocol.GET_NAMES_COMMAND]):
                        message = create_client_get_names(command)
                    elif command.startswith(chat_protocol.COMMAND_STRINGS[chat_protocol.MSG_COMMAND]):
                        message = create_client_message(command)
                    elif command.startswith(chat_protocol.COMMAND_STRINGS[chat_protocol.EXIT_COMMAND]):
                        message = create_exit_message(command, my_socket, scr)
                    else:
                        scr.addstr(chat_protocol.RESPONSE_STRINGS[chat_protocol.INVALID_COMMAND] + "\n")
                        scr.refresh()
                        continue  # Skip sending invalid commands to the server

                    # Client handles invalid message formatting
                    if message.startswith(chat_protocol.RESPONSE_STRINGS[chat_protocol.INVALID_NAME_FORMAT]) or \
                       message.startswith(chat_protocol.RESPONSE_STRINGS[chat_protocol.INVALID_MESSAGE_FORMAT]) or \
                       message.startswith(chat_protocol.RESPONSE_STRINGS[chat_protocol.INVALID_GET_NAMES_FORMAT]) or \
                       message.startswith(chat_protocol.RESPONSE_STRINGS[chat_protocol.INVALID_EXIT_FORMAT]):
                        scr.addstr(message + "\n")
                        scr.refresh()
                        continue

                    # Send the message to the server     
                    if not message.startswith(chat_protocol.RESPONSE_STRINGS[chat_protocol.INVALID_COMMAND]):
                        chat_protocol.send_message(my_socket, message)

    except KeyboardInterrupt:
        create_exit_message("EXIT", my_socket, scr)

if __name__ == '__main__':
    curses.wrapper(main)
