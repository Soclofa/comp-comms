'''
Abraham Soclof 
674098915
Lab 3
server.py
'''

import select
import socket
import chat_protocol

SERVER_PORT = 7777
SERVER_IP = "0.0.0.0"


# Initialize the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Lists to keep track of connected client sockets and their names
client_sockets = []
clients_names = {}
messages_to_send = []

def handle_name_request(current_socket, clients_names, data):
    """
    Handle name setting request from a client.
    """
    if current_socket in clients_names:
        return chat_protocol.RESPONSE_STRINGS[chat_protocol.CLIENT_NAME_ALREADY_SET], current_socket
    else:
        client_name = data.split(" ")[-1].strip()
        if client_name in clients_names.values():
            return chat_protocol.RESPONSE_STRINGS[chat_protocol.NAME_ALREADY_TAKEN], current_socket
        else:
            clients_names[current_socket] = client_name
            print(f"Client's name is: {clients_names[current_socket]}")
            return f"{chat_protocol.RESPONSE_STRINGS[chat_protocol.HELLO_MESSAGE]} {client_name}", current_socket

def handle_get_names_request(clients_names, current_socket):
    """
    Handle request to get the list of connected client names.
    """
    names_list = chat_protocol.RESPONSE_STRINGS[chat_protocol.GET_NAMES_RECEIVED] + " " + " ".join(clients_names.values())
    return names_list, current_socket

def handle_msg_request(current_socket, clients_names, data):
    """
    Handle message sending request from a client.
    """
    try:
        _, recipient_name, message = [part.strip() for part in data.split(" ", 2)]
    except ValueError:
        return chat_protocol.RESPONSE_STRINGS[chat_protocol.INVALID_MESSAGE_FORMAT], current_socket
    
    recipient_socket = None
    for socket, name in clients_names.items():
        if name == recipient_name:
            recipient_socket = socket
            break

    if recipient_socket:
        chat_protocol.send_message(current_socket, chat_protocol.RESPONSE_STRINGS[chat_protocol.MSG_RECEIVED])
        return f"{clients_names[current_socket]} SENT: {message}", recipient_socket
    else:
        return f"{chat_protocol.RESPONSE_STRINGS[chat_protocol.INVALID_MSG_RECIPIENT]} {recipient_name}", current_socket

def handle_client_request(current_socket, clients_names, data):
    """
    Handle incoming request from a client.
    """
    try:
        command_parts = data.split(maxsplit=1)
        if len(command_parts) == 0:
            return chat_protocol.RESPONSE_STRINGS[chat_protocol.INVALID_COMMAND], current_socket
        command_code = int(command_parts[0])

        if current_socket not in clients_names and command_code != chat_protocol.NAME_COMMAND:
            return chat_protocol.RESPONSE_STRINGS[chat_protocol.NAMELESS_CLIENT], current_socket

        if command_code == chat_protocol.NAME_COMMAND:
            return handle_name_request(current_socket, clients_names, data)
        elif command_code == chat_protocol.GET_NAMES_COMMAND:
            return handle_get_names_request(clients_names, current_socket)
        elif command_code == chat_protocol.MSG_COMMAND:
            return handle_msg_request(current_socket, clients_names, data)
        elif command_code == chat_protocol.EXIT_COMMAND:
            if current_socket in clients_names:
                del clients_names[current_socket]
            return chat_protocol.RESPONSE_STRINGS[chat_protocol.EXIT], current_socket
        else:
            return chat_protocol.RESPONSE_STRINGS[chat_protocol.INVALID_COMMAND], current_socket
    except Exception as e:
        print(f"Error in handle_client_request: {e}")
        return chat_protocol.RESPONSE_STRINGS[chat_protocol.INVALID_COMMAND], current_socket

def create_initial_response(): 
    """
    Create the initial welcome message for a new client.
    """
    return chat_protocol.RESPONSE_STRINGS[chat_protocol.WELCOME_MESSAGE]

def handle_disconnection(current_socket, client_address):
    """
    Handle disconnection of a client.
    """
    if current_socket in client_sockets:
        client_sockets.remove(current_socket)
    if current_socket in clients_names:
        del clients_names[current_socket]
    current_socket.close()
    print(f"Connection closed for {client_address}")

def main():
    """
    Main function to set up and run the server.
    """
    try:
        print("Setting up server...")
        server_socket.bind((SERVER_IP, SERVER_PORT))
        server_socket.listen()
        print("Listening for clients...")

        while True:
            read_list = client_sockets + [server_socket]
            ready_to_read, ready_to_write, in_error = select.select(read_list, client_sockets, [])

            for current_socket in ready_to_read:
                if current_socket is server_socket:
                    # Handle new client connection
                    client_socket, client_address = server_socket.accept()
                    print("Client connected from", client_address)
                    client_sockets.append(client_socket)
                    chat_protocol.send_message(client_socket, create_initial_response())
                else:
                    # Handle data from existing client
                    try:
                        data = chat_protocol.receive_message(current_socket)
                        if not data:
                            handle_disconnection(current_socket, client_address)
                        else:
                            response, dest_socket = handle_client_request(current_socket, clients_names, data)
                            messages_to_send.append((dest_socket, response))
                    except Exception as e:
                        print(f"Error in main loop: {e}")
                        handle_disconnection(current_socket, client_address)

            # Send queued messages to clients
            for message in messages_to_send:
                dest_socket, data = message
                if dest_socket in ready_to_write:
                    chat_protocol.send_message(dest_socket, data)
                    messages_to_send.remove(message)

    except KeyboardInterrupt:
        # Handle server shutdown
        print("Received exit signal. Informing clients and closing connections...")
        shutdown_message = chat_protocol.RESPONSE_STRINGS[chat_protocol.EXIT]
        for client_socket in client_sockets:
            try:
                chat_protocol.send_message(client_socket, shutdown_message)
            except Exception as e:
                print(f"Error while notifying client of shutdown: {e}")
            handle_disconnection(client_socket, client_address)
        server_socket.close()
        print("Server shutdown complete.")

if __name__ == '__main__':
    main()
