'''
Abraham Soclof 
ID: 674098915
Lab2/Client.py
'''
import socket
import SMTP_protocol
import base64

CLIENT_NAME = "THE CLIENT"
MAIL_FROM = "sender@gmail.com"
RECIEVER = "reciever@gmail.com"
EMAIL_TEXT = \
    "From: sender@gmail.com\r\n" \
    "To: receiver@gmail.com\r\n" \
    "Subject: SOS: Send Money. Not A\r\n" \
    "\r\n" \
    "I am in need of help. Send $20,000 and save my life.\r\nP.S. This is not a scam." \
    "\r\n.\r\n"

def create_EHLO():
    """
    Creates the EHLO message with the client name.
    
    Returns:
        bytes: The EHLO message encoded in bytes.
    """
    return (f"EHLO {CLIENT_NAME}".encode())
    
def create_AUTH_LOGIN():
    """
    Creates the AUTH LOGIN message.
    
    Returns:
        bytes: The AUTH LOGIN message encoded in bytes.
    """
    return "AUTH LOGIN".encode()

def create_MAIL_FROM():
    """
    Creates the MAIL FROM message with the sender's email address.
    
    Returns:
        bytes: The MAIL FROM message encoded in bytes.
    """
    return(f"Mail FROM: <{MAIL_FROM}>".encode())
    
def create_RCPT_TO():
    """
    Creates the RCPT TO message with the receiver's email address.
    
    Returns:
        bytes: The RCPT TO message encoded in bytes.
    """
    return (f"RCPT TO: <{RECIEVER}>".encode())

def create_email_content():
    """
    Creates the email content.
    
    Returns:
        bytes: The email content encoded in bytes.
    """
    return EMAIL_TEXT.encode()

def create_DATA():
    """
    Creates the DATA message to indicate the start of the email content.
    
    Returns:
        bytes: The DATA message encoded in bytes.
    """
    return "DATA".encode()

def create_QUIT():
    """
    Creates the QUIT message to terminate the SMTP session.
    
    Returns:
        bytes: The QUIT message encoded in bytes.
    """
    return "QUIT".encode()

def create_username_response(user):
    """
    Encodes the username in base64 format.
    
    Args:
        user (str): The username.
        
    Returns:
        bytes: The base64-encoded username.
    """
    return base64.b64encode(user.encode())

def create_password_response(password):
    """
    Encodes the password in base64 format.
    
    Args:
        password (str): The password.
        
    Returns:
        bytes: The base64-encoded password.
    """
    return base64.b64encode(password.encode())

def main():
    """
    Main function that handles the SMTP client communication.
    """

    # Connect to server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', SMTP_protocol.PORT))

    # 1 server welcome message
    message = s.recv(1024).decode()
    print(message)
    # Check that the welcome message is according to the protocol
    if not message.startswith(SMTP_protocol.SMTP_SERVICE_READY):
        print("CONNECTION:SERVER ERROR")
        s.close()
        return

    # 2 EHLO message
    message = create_EHLO()
    s.send(message)
    response = s.recv(1024).decode()
    print(response)
    if not response.startswith(SMTP_protocol.REQUESTED_ACTION_COMPLETED):
        print("CONNECTION: SERVER ERROR")
        s.close()
        return

    # 3 AUTH LOGIN
    message = create_AUTH_LOGIN()
    s.send(message)
    response = s.recv(1024).decode()

    print(response)
    if not response == (f"{SMTP_protocol.AUTH_INPUT}{'VXNlcm5hbWU6'}"):
        print("AUTH LOGIN SERVER ERROR")
        s.close()
        return

    # 4 User
    user = "barbie"
    message = create_username_response(user)
    s.send(message)
    response = s.recv(1024).decode()
    print(response)
    if not response == (f"{SMTP_protocol.AUTH_INPUT}{'UGFzc3dvcmQ6'}"):
        print("AUTH LOGIN USERNAME: SERVER ERROR")
        s.close()
        return

    # 5 password
    password = "helloken"
    message = create_password_response(password)
    s.send(message)
    response = s.recv(1024).decode()
    print(response)
    if not response.startswith(SMTP_protocol.AUTH_SUCCESS):
        print("AUTH LOGIN PASSWORD: SERVER ERROR")
        s.close()
        return

    # 6 mail from
    message = create_MAIL_FROM()
    s.send(message)
    response = s.recv(1024).decode()
    print(response)
    if not response.startswith(SMTP_protocol.REQUESTED_ACTION_COMPLETED):
        print("MAIL FROM: SERVER ERROR")
        s.close()
        return

    # 7 rcpt to
    message = create_RCPT_TO()
    s.send(message)
    response = s.recv(1024).decode()
    print(response)
    if not response.startswith(SMTP_protocol.REQUESTED_ACTION_COMPLETED):
        print("RCPT TO: SERVER ERROR")
        s.close()
        return

    # 8 data
    message = create_DATA()
    s.send(message)
    response = s.recv(1024).decode()
    print(response)
    if not response.startswith(SMTP_protocol.ENTER_MESSAGE):
        print("DATA: ERROR")
        s.close()
        return

    # 9 email content
    message = create_email_content()
    s.send(message)
    response = s.recv(1024).decode()
    print(response)
    if not response.startswith(SMTP_protocol.REQUESTED_ACTION_COMPLETED):
        print("CONTENT ERROR")
        s.close()
        return

    # 10 quit
    message = create_QUIT()
    s.send(message)
    response = s.recv(1024).decode()
    print(response)
    if not response.startswith(SMTP_protocol.GOODBYE):
        print("QUIT: ERROR")
        s.close()
        return

    print("Closing\n")
    s.close()

main()