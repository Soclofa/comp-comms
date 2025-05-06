# chat_protocol.py
'''
Abraham Soclof 
674098915
Lab 3
'''

# Command Codes
NAME_COMMAND = 1
GET_NAMES_COMMAND = 2
MSG_COMMAND = 3
EXIT_COMMAND = 4

# Response Codes
WELCOME_MESSAGE = 100
HELLO_MESSAGE = 101
INVALID_NAME_FORMAT = 102
NAME_ALREADY_TAKEN = 103
NAMELESS_CLIENT = 104
INVALID_GET_NAMES_FORMAT = 105
GET_NAMES_RECEIVED = 106
MSG_RECEIVED = 107
INVALID_MSG_RECIPIENT = 108
INVALID_COMMAND = 109
INVALID_MESSAGE_FORMAT = 110
CLIENT_NAME_ALREADY_SET = 111
INVALID_EXIT_FORMAT = 112
EXIT = 113

# Command Strings
COMMAND_STRINGS = {
    NAME_COMMAND: "NAME",
    GET_NAMES_COMMAND: "GET_NAMES",
    MSG_COMMAND: "MSG",
    EXIT_COMMAND: "EXIT"
}

# Response Strings
RESPONSE_STRINGS = {
    WELCOME_MESSAGE: "Welcome to the chat server!",
    HELLO_MESSAGE: "HELLO",
    INVALID_NAME_FORMAT: "ERROR: Invalid name format. Use: NAME <name>\n<name> must be one word.",
    NAME_ALREADY_TAKEN: "ERROR: Name already taken.",
    NAMELESS_CLIENT: "ERROR: Set your name first using: NAME <name>",
    INVALID_GET_NAMES_FORMAT: "ERROR: Invalid get names format. Use: GET_NAMES",
    GET_NAMES_RECEIVED: "Connected clients:",
    MSG_RECEIVED: "Message sent.",
    INVALID_MSG_RECIPIENT: "ERROR: Invalid message recipient.",
    INVALID_COMMAND: "ERROR: Unknown command.",
    INVALID_MESSAGE_FORMAT: "ERROR: Invalid message format. Use: MSG <name> <message>\n<message> must be one word",
    CLIENT_NAME_ALREADY_SET: "ERROR: Name already set.",
    INVALID_EXIT_FORMAT: "ERROR: Invalid exit format. Use: EXIT",
    EXIT: "EXIT"
}

def send_message(socket, message): 
    length = len(message)
    socket.send(f"{length:02}".encode())
    socket.send(message.encode())

def receive_message(socket):
    raw_length = socket.recv(2)
    if not raw_length:
        return None
    message_length = int(raw_length.decode())
    data = socket.recv(message_length).decode()
    return data