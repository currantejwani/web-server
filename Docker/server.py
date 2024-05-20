import socket
import sys
import ssl
import os
import subprocess

"""
A simple HTTP server that supports GET, POST, PUT, DELETE, and PATCH methods.
Handles static files and PHP scripts with query parameters.
"""


# Log the request to a log file
def log_request(request):
    """
    Log the incoming request in a log file.

    :param request: The request data as bytes.
    """
    with open(os.path.dirname(os.path.abspath(".")) + "/app/logfile.txt", "a") as logfile:
        lines = request.split(b'\r\n')
        first_line = lines[0].split()
        logfile.write(f"{first_line}\n")


# Parse query string from the URI and return a dictionary
def parse_query_string(query_string):
    """
    Parse the query string and return a dictionary of key-value pairs.

    :param query_string: The query string as a string.
    :return: A dictionary of key-value pairs.
    """
    query_dict = {}
    if query_string:
        for pair in query_string.split('&'):
            key, value = pair.split('=')
            query_dict[key] = value
    return query_dict


# Process the client request, including parsing and handling HTTP methods
def parse_request(conn):
    """
    Parse the incoming request, determine the request method, and call the appropriate handler function.

    :param conn: The connection object.
    """
    root_dir = os.path.dirname(os.path.abspath(".")) + '/app'
    # Receive the request data
    request = conn.recv(1024)
    if not request:
        return

    # Split the data into separate lines
    lines = request.split(b'\r\n')

    # Extract the first line to get the request method, URI, and HTTP version
    first_line = lines[0].split()
    if len(first_line) != 3:
        send_response(conn, 400)
        return

    log_request(request)

    method, uri, http_version = first_line

    # Check if the method is supported
    if method not in [b'GET', b'POST', b'PUT', b'DELETE', b'PATCH']:
        send_response(conn, 501)
        return

    # Check if the HTTP version is supported
    if http_version not in [b'HTTP/1.0', b'HTTP/1.1']:
        send_response(conn, 505)
        return

    url = uri.decode()
    # Check if the file exists and is accessible
    if '?' in url:
        # This is a PHP script with parameters
        uri_path, query_params_str = url.split('?')
        query_params = {}
        for param in query_params_str.split('&'):
            key, value = param.split('=')
            query_params[key] = value
        # Handle the request accordingly
        # ...
    else:
        # This is a file path
        uri_path = url
        file_path = root_dir + uri_path if uri_path != "/" else root_dir + "/index.html"
        if not os.path.exists(file_path):
            send_response(conn, 404)
            return
        if not os.access(file_path, os.R_OK):
            send_response(conn, 403)
            return
    # Check if the file exists and is accessible

    # Handle the GET method
    if method == b'GET':
        if '?' in url:
            script_path = root_dir + url.split('?')[0]

            # Create a list of strings with each key-value pair as a string
            param_list = [f"-d '{key}={value}'" for key, value in query_params.items()]

            # Join the list of strings with spaces
            param_string = ' '.join(param_list)

            command = f'php-cgi -f {script_path} -- {param_string}'
            try:
                output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                send_response(conn, 200, output)
            except subprocess.CalledProcessError as e:
                output = e.output
                send_response(conn, 500, output)
        else:
            with open(file_path, 'rb') as f:
                content = f.read()
            send_response(conn, 200, content, file_path)

    # Handle the POST method
    if method == b'POST':
        # Check if the content-length header is set
        content_length = None
        for line in lines[1:]:
            if line.startswith(b'Content-Length:'):
                content_length = int(line.split(b':')[1].strip())
                break
        if content_length is None:
            send_response(conn, 411)
            return

        content_type = None
        for line in lines[1:]:
            if line.startswith(b'Content-Type:'):
                content_type = (line.split(b':')[1].strip())
                break

        # Read the content of the request
        content = request.split(b'\r\n\r\n')[1]
        if content_type == b'application/x-www-form-urlencoded':
            post_data = content.decode()
            post_dict = {}
            for pair in post_data.split('&'):
                key, value = pair.split('=')
                post_dict[key] = value

            headers = {
                "REDIRECT_STATUS": "true",
                "SCRIPT_FILENAME": file_path,
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": "application/x-www-form-urlencoded",
                "CONTENT_LENGTH": str(content_length),
            }

            encoded_params = ""
            for key, value in post_dict.items():
                encoded_params += key + "=" + str(value) + "&"

            # Remove the trailing "&" from the encoded string
            encoded_params = encoded_params.rstrip("&")
            command = f'php-cgi'
            try:
                output = subprocess.check_output(command, input=encoded_params.encode(), env=headers, shell=True,
                                                 stderr=subprocess.STDOUT)
                send_response(conn, 200, output)
            except subprocess.CalledProcessError as e:
                output = e.output
                send_response(conn, 500, output)

        if content_type == b'text/plain':
            with open(file_path, 'wb') as f:
                f.write(content)
            send_response(conn, 201)

    # Handle the PUT method
    if method == b'PUT':
        # Check if the content-length header is set
        content_length = None
        for line in lines[1:]:
            if line.startswith(b'Content-Length:'):
                content_length = int(line.split(b':')[1].strip())
                break
        if content_length is None:
            send_response(conn, 411)
            return

        # Read the content of the request
        content = request.split(b'\r\n\r\n')[1]
        # Write the content to the file
        with open(file_path, 'wb') as f:
            f.write(content)
        send_response(conn, 201)

    # Handle the DELETE method
    if method == b'DELETE':
        os.remove(file_path)

    # Handle the PATCH method
    if method == b'PATCH':
        # Check if the content-length header is set
        content_length = None
        for line in lines[1:]:
            if line.startswith(b'Content-Length:'):
                content_length = int(line.split(b':')[1].strip())
                break
        if content_length is None:
            send_response(conn, 411)
            return

        # Read the content of the request
        content = request.split(b'\r\n\r\n')[1]

        # Apply the patch to the file
        try:
            with open(file_path, 'rb') as f:
                original_content = f.read()
            patched_content = original_content[:content_length] + content
            with open(file_path, 'wb') as f:
                f.write(patched_content)
            send_response(conn, 200)
        except IOError:
            send_response(conn, 500)


# Get the content type of a file based on its extension
def get_content_type(file_path):
    """
    Determine the content type of the file based on its extension.

    :param file_path: The file path as a string.
    :return: The content type as a string.
    """
    extension = os.path.splitext(file_path)[1]
    if extension == ".html":
        return "text/html"
    elif extension == ".css":
        return "text/css"
    elif extension == ".js":
        return "application/javascript"
    else:
        return "text/plain"


# Send a response to the client
def send_response(conn, status_code, content=None, file_path=None):
    """
    Send a response to the client with the specified status code and content.

    :param conn: The connection object.
    :param status_code: The HTTP status code as an integer.
    :param content: The content of the response as bytes (optional).
    :param file_path: The file path as a string (optional).
    """
    if status_code == 200:
        status_line = b'HTTP/1.1 200 OK\r\n'
    elif status_code == 201:
        status_line = b'HTTP/1.1 201 Created\r\n'
    elif status_code == 400:
        status_line = b'HTTP/1.1 400 Bad Request\r\n'
    elif status_code == 403:
        status_line = b'HTTP/1.1 403 Forbidden\r\n'
    elif status_code == 404:
        status_line = b'HTTP/1.1 404 Not Found\r\n'
    elif status_code == 411:
        status_line = b'HTTP/1.1 411 Length Required\r\n'
    elif status_code == 500:
        status_line = b'HTTP/1.1 500 Internal Server Error\r\n'
    elif status_code == 501:
        status_line = b'HTTP/1.1 501 Not Implemented\r\n'
    elif status_code == 505:
        status_line = b'HTTP/1.1 505 HTTP Version Not Supported\r\n'
    response_message = status_line.decode()
    if content:
        content_length = len(content)
        headers = ""

        if file_path:
            content_type = get_content_type(file_path)
            headers += f"Content-Type: {content_type}\r\n"
        else:
            headers += f"Content-Type: text/plain\r\n"

        headers += f"Content-Length: {content_length}\r\n"
        response_message = status_line.decode() + headers + "\r\n" + content.decode()

    conn.send(response_message.encode())


# Create a socket, bind it, and start listening for connections
def main():
    if len(sys.argv) < 3:
        print("Error: Provide IP address and port number as arguments")
        sys.exit(1)
    ip_address = sys.argv[1]
    port = int(sys.argv[2])

    pem_file = None
    key_file = None
    if len(sys.argv) > 3:
        pem_file = sys.argv[3]
    if len(sys.argv) > 4:
        key_file = sys.argv[4]

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip_address, port))
    server_socket.listen()

    if pem_file and key_file:
        server_socket = ssl.wrap_socket(server_socket, certfile=pem_file, keyfile=key_file, server_side=True)

    print(f"Listening on {ip_address}:{port}...")

    while True:
        try:
            client_socket, client_address = server_socket.accept()
            parse_request(client_socket)
            client_socket.close()
        except ssl.SSLError as e:
            print(f"SSLError: {e}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
