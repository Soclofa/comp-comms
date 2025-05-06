'''
Abraham Soclof 
ID: 674098915
Lab2/Server.py
'''
import socket
import SMTP_protocol
import base64

# Server configurations
IP = '127.0.0.1'
SOCKET_TIMEOUT = 1
SERVER_NAME = "SMTP_server"

# Sample user credentials
user_names = {"shooki": "abcd1234", "barbie": "helloken"}

def create_initial_response():
    """
    Creates the initial SMTP response: "220 Welcome to the SMTP server\r\n"
    
    Returns:
        bytes: The initial SMTP response encoded in bytes.
    """
    return (SMTP_protocol.SMTP_SERVICE_READY).encode()
    
def create_EHLO_response(client_message):
    """
    Creates the EHLO response: "250 OK\r\n"
    
    Args:
        client_message (str): The message received from the client.
        
    Returns:
        bytes: The EHLO response encoded in bytes, or a syntax error response if the client message is invalid.
    """
    if not client_message.startswith("EHLO"):
        return (f"{SMTP_protocol.COMMAND_SYNTAX_ERROR}").encode()
    return (f"{SMTP_protocol.REQUESTED_ACTION_COMPLETED}\n").encode()

def create_AUTH_LOGIN_response(client_message):
    """
    Creates the AUTH LOGIN response: "334 VXNlcm5hbWU6"
    
    Args:
        client_message (str): The message received from the client.
        
    Returns:
        bytes: The AUTH LOGIN response encoded in bytes, or a syntax error response if the client message is invalid.
    """
    if not client_message.startswith("AUTH LOGIN"):
        return (f"{SMTP_protocol.COMMAND_SYNTAX_ERROR}").encode()
    return (f"{SMTP_protocol.AUTH_INPUT}{'VXNlcm5hbWU6'}").encode()

def create_pass_response(client_message, username):
    """
    Creates the AUTH LOGIN response for the password: "235 Authentication successful\r\n Authentication successful"
    
    Args:
        client_message (str): The password received from the client.
        username (str): The username provided by the client.
        
    Returns:
        bytes: The AUTH LOGIN password response encoded in bytes, or a syntax error response if the password is incorrect.
    """
    if user_names.get(username) == client_message:
        return (f"{SMTP_protocol.AUTH_SUCCESS}{'Authentication Successful'}").encode()
    return ("{}".format(SMTP_protocol.COMMAND_SYNTAX_ERROR)).encode()

def create_MAIL_FROM_response(client_message):
    """
    Creates the MAIL FROM response: "250 OK Sender Email Received Successfully"
    
    Args:
        client_message (str): The message received from the client.
        
    Returns:
        bytes: The MAIL FROM response encoded in bytes, or a syntax error response if the client message is invalid.
    """
    if not client_message.startswith("Mail FROM:"):
        return (SMTP_protocol.COMMAND_SYNTAX_ERROR).encode()
    
    email = client_message.split(':')[1].strip()

    if not email.startswith('<') or not email.endswith('>'):
        return (f"{SMTP_protocol.COMMAND_SYNTAX_ERROR}").encode()
    
    email = email[1:-1]  # Remove the < and > characters
    return (f"{SMTP_protocol.REQUESTED_ACTION_COMPLETED} Sender Email Recieved Successfully").encode()

def create_RCPT_TO_response(message):
    """
    Creates the RCPT TO response: "250 OK Receiver Received Successfully"
    
    Args:
        message (str): The message received from the client.
        
    Returns:
        bytes: The RCPT TO response encoded in bytes, or a syntax error response if the client message is invalid.
    """
    if not message.startswith("RCPT TO"):
        return (SMTP_protocol.COMMAND_SYNTAX_ERROR).encode()
    return (f"{SMTP_protocol.REQUESTED_ACTION_COMPLETED} Email Recieved Successfully").encode()

def create_user_response(client_message):
    """
    Creates the AUTH INPUT response for the username: "334 UGFzc3dvcmQ6" (base64 encoded "Password:")
    
    Args:
        client_message (str): The username received from the client.
        
    Returns:
        bytes: The AUTH INPUT username response encoded in bytes, or a syntax error response if the username is invalid.
    """
    if user_names.get(client_message) is not None:
        return (f"{SMTP_protocol.AUTH_INPUT}{'UGFzc3dvcmQ6'}").encode()
    return (f"{SMTP_protocol.COMMAND_SYNTAX_ERROR}").encode()

def create_DATA_response(message):
    """
    Creates the DATA response: "354 End data with <CR><LF>.<CR><LF>"
    
    Args:
        message (str): The message received from the client.
        
    Returns:
        bytes: The DATA response encoded in bytes, or a syntax error response if the client message is invalid.
    """
    if not message.startswith("DATA"):
        return (f"{SMTP_protocol.COMMAND_SYNTAX_ERROR}{'DATA Recieved Unsuccesfully'}").encode()
    return (f"{SMTP_protocol.ENTER_MESSAGE}{'DATA Recieved Successfully'}").encode()

def create_QUIT_response(message):
    """
    Creates the QUIT response: "221 Bye"
    
    Args:
        message (str): The message received from the client.
        
    Returns:
        bytes: The QUIT response encoded in bytes, or a syntax error response if the client message is invalid.
    """
    if not message.startswith("QUIT"):
        return (SMTP_protocol.COMMAND_SYNTAX_ERROR).encode()
    return(f"{SMTP_protocol.GOODBYE}QUIT").encode()

def handle_SMTP_client(client_socket):
    # 1 send initial message
    print("#1: Sending Initial Message")
    message = create_initial_response()
    print(f"Server: {message.decode()}")
    client_socket.send(message)

    # 2 receive and send EHLO
    print("#2: Receiving and Sending EHLO")
    message = client_socket.recv(1024).decode()
    print(f"Client: {message}")
    response = create_EHLO_response(message)
    client_socket.send(response)
    print(f"Server: {response.decode()}")
    if not response.decode().startswith(SMTP_protocol.REQUESTED_ACTION_COMPLETED):
        print("EHLO: CLIENT ERROR")
        return

    # 3 receive and send AUTH Login
    print("#3: Receiving and Sending AUTH LOGIN")
    message = client_socket.recv(1024).decode()
    print(f"Client: {message}")
    response = create_AUTH_LOGIN_response(message)
    client_socket.send(response)
    print(f"Server: {response.decode()}\n")
    if not response.decode().startswith(SMTP_protocol.AUTH_INPUT):
        print("AUTH LOGIN: CLIENT ERROR")
        return

    # 4 receive and send USER message
    print("#4: Receiving and sending USER")
    user = base64.b64decode(client_socket.recv(1024).decode()).decode()
    print(f"Client: {user}")
    response = create_user_response(user)
    client_socket.send(response)
    print(f"Server: {response.decode()}\n")
    if not response.decode().startswith(SMTP_protocol.AUTH_INPUT):
        print("USERNAME: CLIENT ERROR")
        return

    # 5 password
    print("#5: Receiving and Sending PASSWORD")
    password = base64.b64decode(client_socket.recv(1024).decode()).decode()
    print(f"Client: {password}")
    response = create_pass_response(password, user)
    client_socket.send(response)
    print(f"Server: {response.decode()}\n")
    if not response.decode().startswith(SMTP_protocol.AUTH_SUCCESS):
        print("PASSWORD: CLIENT ERROR")
        return

    # 6 mail from
    print("#6: Receiving and Sending MAIL FROM")
    message = client_socket.recv(1024).decode()
    print(f"Client: {message}")
    response = create_MAIL_FROM_response(message)
    client_socket.send(response)
    print(f"Server: {response.decode()}\n")
    if not response.decode().startswith(SMTP_protocol.REQUESTED_ACTION_COMPLETED):
        print("MAIL FROM: CLIENT ERROR")
        return

    # 7 rcpt to
    print("#7: Receiving and Sending RCPT TO")
    message = client_socket.recv(1024).decode()
    print(message)
    print(f"Client: {message}")
    response = create_RCPT_TO_response(message)
    client_socket.send(response)
    print(f"Server: {response.decode()}\n")
    if not response.decode().startswith(SMTP_protocol.REQUESTED_ACTION_COMPLETED):
        print("RCPT TO: CLIENT ERROR")
        return

    # 8 DATA
    print("#8: Receiving and Sending DATA")
    message = client_socket.recv(1024).decode()
    print(f"Client: {message}")
    response = create_DATA_response(message)
    client_socket.send(response)
    print(f"Server: {response.decode()}\n")
    if not response.decode().startswith(SMTP_protocol.ENTER_MESSAGE):
        print("DATA: CLIENT ERROR")
        return

    # 9 email content
    print("#9: Receiving Email Content")
    while True:
        message = client_socket.recv(1024).decode()
        print(f"Client: {message}")
        if message.endswith(SMTP_protocol.EMAIL_END):
            client_socket.send(f"{SMTP_protocol.REQUESTED_ACTION_COMPLETED} {'Content Successfully Recieved'}".encode())         
            break

    # 10 quit
    print("#10: Receiving and Sending QUIT")
    message = client_socket.recv(1024).decode()
    print(f"Client: {message}")
    response = create_QUIT_response(message)
    client_socket.send(response)
    print(f"Server: {response.decode()}\n")
    if not response.decode().startswith(SMTP_protocol.GOODBYE):
        print(" QUIT: ERROR")
        return
    client_socket.close()

def main():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, SMTP_protocol.PORT))
    server_socket.listen()

    print(f"\nServer: Listening for connections on port {SMTP_protocol.PORT}\n")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print('Server: New connection received\n')
            client_socket.settimeout(SOCKET_TIMEOUT)
            handle_SMTP_client(client_socket)
            print("Server: Connection closed\n")

    except KeyboardInterrupt:
        print("\nServer: Shutting down server\n")
        server_socket.close()

main()