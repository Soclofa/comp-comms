
"""

Abraham Soclof
674098915
Lab5 - Http Server


"""

import socket
import os

IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 10
DEFAULT_URL = 'index.html'
REDIRECTION_DICTIONARY = {'avi': 'index1.html'}
CONTENT_TYPES = {
        'html': 'text/html; charset=utf-8',
        'txt': 'text/html; charset=utf-8',
        'jpg': 'image/jpeg',
        'js': 'text/javascript; charset=UTF-8',
        'css': 'text/css',
        'ico': 'image/x-icon'  
    }

def calculate_area(resource, client_socket): 
    """
    This function calculates the area of a triangle given the height and width from the query parameters of the HTTP request, 
    and sends the result back to the client in the HTTP response.

    Parameters:
    resource (str): The requested resource from the client. It should contain the query parameters for height and width.
    client_socket (socket): The client socket to send the response to.

    Returns:
    None
    """

    # Split the resource by '?' and get the last part, which should be the query parameters
    params = resource.split('?')[-1]

    # Split the parameters by '&' to get each individual parameter
    # For each parameter, split by '=' and get the last part, which should be the value
    # Convert the value to an integer
    height = int(params.split('&')[0].split('=')[-1])
    width = int(params.split('&')[1].split('=')[-1])

    # Calculate the area of the triangle using the formula 'height * width / 2'
    area = height*width/2

    # Create the HTTP response
    # Start with the status line
    # Then add the 'Content-Length' header, which is the length of the area
    # Add the 'Content-Type' header, which is 'text/plain' for plain text
    # Add two CRLF to indicate the end of the headers
    # Finally, add the body of the response, which is the area
    http_response = f"HTTP/1.1 200 OK\r\nContent-Length: {str(len(str(area)))}\r\nContent-Type: text/plain\r\n\r\n{str(area)}"

    # Send the response to the client
    client_socket.send(http_response.encode())

def redirect(resource, client_socket):
    """
    This function handles HTTP redirection. It sends a 302 Found response to the client, 
    with the 'Location' header set to the new URL.

    Parameters:
    resource (str): The requested resource from the client. It should be a key in the REDIRECTION_DICTIONARY.
    client_socket (socket): The client socket to send the response to.

    Returns:
    None
    """
    print("Redirecting...")

    # Start building the HTTP response
    # Start with the status line, which is "HTTP/1.1 302 Found"
    response = "HTTP/1.1 302 Found\r\n"

    # Add the 'Location' header to the response
    # The value of the 'Location' header is the new URL that the client should redirect to
    # This is looked up in the REDIRECTION_DICTIONARY using the requested resource as the key
    # Note that we remove the leading slash from the resource before looking it up in the dictionary
    response += f"Location: {REDIRECTION_DICTIONARY[resource.lstrip('/')]}\r\n\r\n"

    # Send the response to the client
    client_socket.send(response.encode())

    # Close the connection to the client
    client_socket.close()

def NOT_FOUND(resource, client_socket):
    """
    This function handles the case when the requested resource is not found on the server. 
    It sends a 404 Not Found response to the client and closes the connection.

    Parameters:
    resource (str): The requested resource from the client that was not found.
    client_socket (socket): The client socket to send the response to.

    Returns:
    None
    """
    print(f"Error: '{resource}'")

    # Start building the HTTP response
    # Start with the status line, which is "HTTP/1.0 404 Not Found"
    response = "HTTP/1.0 404 Not Found\r\n"

    # Add the 'Connection: close' header to the response
    # This tells the client that the server will close the connection after completing the response
    response += "Connection: close\r\n"

        
    # Add the 'Content-Type' header to the response
    # This tells the client that the body of the response is HTML
    response += "Content-Type: text/html; charset=utf-8\r\n\r\n"

    # Add the body of the response
    # This is a simple HTML page that displays an error message
    response += "<html><body><h1>Error 404: File not found</h1></body></html>"

    # Send the response to the client
    client_socket.send(response.encode())

    # Close the connection to the client
    client_socket.close()



def get_file_data(filename):
    """
    This function reads the data from a file and returns it. If the file does not exist, it returns None.

    Parameters:
    filename (str): The name of the file to read.

    Returns:
    bytes: The data read from the file, or None if the file does not exist.
    """

    # Check if the file exists
    # os.path.isfile returns True if the given filename refers to an existing file
    if not os.path.isfile(filename):
        return None
    
    # Open the file in binary mode
    # 'rb' stands for 'read binary'
    # This means that the file is read as is, without any special encoding or decoding
    with open(filename, 'rb') as file:  
        # Read the entire contents of the file and return it
        return file.read()
    
def validate_http_request(request):
    """
    This function validates an HTTP request. It checks if the request method is GET and if the HTTP version is 1.1.
    If the request is valid, it returns True and the requested URL. If the request is not valid, it returns False and the requested URL.

    Parameters:
    request (str): The HTTP request to validate.

    Returns:
    tuple: A tuple where the first element is a boolean indicating whether the request is valid, and the second element is the requested URL.
    """
    try:
        # Split the request into a list
        lines = request.split('\r\n')

        # The first item of the request is the request line
        request_line = lines[0].split(' ')

        # The request line is split into three parts: the method, the URL, and the HTTP version
        method, url, version = request_line[0], request_line[1], request_line[2]

        # Check if the method is GET
        # If it's not, return False and the URL
        if method != 'GET':
            return False, url

        # Check if the HTTP version is 1.1
        # If it's not, return False and the URL
        if 'HTTP/1.1' not in version.upper():
            return False, url

        # If the method is GET and the HTTP version is 1.1, the request is valid
        # Return True and the URL
        return True, url

    # If there's an error (for example, if the request line doesn't have three parts), print the error and return False and an empty string
    except Exception as e:
        print(f"Error: {e}")
        return False, ""

def handle_client_request(resource, client_socket):
    """
    This function handles a client request. It checks the requested resource and generates the appropriate HTTP response.

    Parameters:
    resource (str): The requested resource from the client.
    client_socket (socket): The client socket to send the response to.

    Returns:
    None
    """    
    print(f"Client requested: {resource}")

    # Check if the requested resource is in the redirection dictionary
    # If it is, call the redirect function and return
    if resource.lstrip('/') in REDIRECTION_DICTIONARY:
        redirect(resource, client_socket)
        return
    
    # Check if the requested resource starts with '/calculate-area'
    # If it does, call the calculate_area function and return
    if resource.startswith('/calculate-area'):
        calculate_area(resource, client_socket)
        return

    # If the requested resource is '/', set the filename to the default URL
    # Otherwise, set the filename to the requested resource
    # The filename is used to find the file in the webroot directory
    if resource == '/':
        filename = os.path.join('webroot', DEFAULT_URL)
    else:
        filename = os.path.join('webroot', resource.lstrip('/'))  # Handle any file

    # Get the data from the file
    # If the file does not exist, call the NOT_FOUND function and return
    file_data = get_file_data(filename)
    if file_data is None:
        NOT_FOUND(resource,client_socket)
        return

    # Get the filetype from the resource
    # This is done by splitting the resource by '.' and getting the last part
    # The filetype is used to set the 'Content-Type' header in the response
    filetype = resource.split('.')[-1]  # Assuming the filetype is after the last dot in the URL
    content_type = CONTENT_TYPES.get(filetype)

    # Start building the HTTP response
    # Start with the status line, which is "HTTP/1.0 200 OK"
    response = "HTTP/1.0 200 OK\r\n"
    

    # Add the 'Content-Length' header to the response
    # This is the size of the file in bytes
    response += f"Content-Length: {os.path.getsize(filename)}\r\n"


    # If the content type is known, add the 'Content-Type' header to the response
    # Otherwise, just add a newline
    if content_type:
        response += f"Content-Type: {content_type}\r\n\r\n"
    else:
        response += "\r\n"

    # If the file data is a string, add it to the response and send the response
    # Otherwise, send the response and the file data separately
    if isinstance(file_data, str):
        response += file_data
        client_socket.send(response.encode())
    else:
        client_socket.send(response.encode() + file_data) # Send the headers and the file data separately

def handle_client(client_socket):
    """ Handles client requests: verifies client's requests are legal HTTP, calls function to handle the requests """
    print('Client connected')
    
    try:
        client_request = client_socket.recv(1024).decode()
        valid_http, resource = validate_http_request(client_request)
        if valid_http:
            print('Got a valid HTTP request')
            handle_client_request(resource, client_socket)
        else:
            print('Error: Not a valid HTTP request')
            raise Exception('Not a valid HTTP request')
    except Exception as e:
        print(f"Error: {e}")
        response = "HTTP/1.0 500 Internal Server Error\r\n\r\n"
        client_socket.send(response.encode())
    finally:
        client_socket.close()

def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print("Listening for connections on port {}".format(PORT))

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        client_socket.settimeout(SOCKET_TIMEOUT)
        handle_client(client_socket)

if __name__ == "__main__":
    # Call the main handler function
    main()
