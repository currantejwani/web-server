# Simple Python Web Server

This is a simple web server implemented in Python. It supports serving static files over HTTP and HTTPS and can be accessed using a web browser.

## Features

- Serves static files (HTML, CSS, JavaScript, images, etc.)
- Supports HTTP and HTTPS (using self-signed SSL certificates)
- PHP execution support through the PHP interpreter (assuming PHP is installed on the server)
- Accessible via web browsers (e.g., Chrome, Firefox, Safari)
- Lightweight and easy to configure
- Logs incoming requests to a `logfile.txt` file in the `Code` folder
- Supports the following HTTP methods: GET, POST, PUT, DELETE, and PATCH

## Requirements

- Python 3.6 or higher
- PHP and PHP-CGI (for executing PHP scripts)

## Usage

1. Clone the repository to your local machine.
2. Open a terminal or command prompt, navigate to the `Code` directory with the `server.py` file.
3. Run the server with the following command: 
```bash
python3 server.py <ip_address> <port> [pem_file] [key_file]
```

## Example

- To start the server on IP address 127.0.0.1 and port 5500, run: 
```bash
python3 server.py 127.0.0.1 5500
```
- To start the server with HTTPS support, provide the paths to the PEM and KEY files:
```bash
python3 server.py 127.0.0.1 5500 cert.pem key_without_passphrase.pem
```

## Sample Requests

- GET Request 
```bash
echo -e "GET /script.php?name=curran&age=22 HTTP/1.1\r\nHost: localhost:5500\r\n" | nc localhost 5500
```
- POST Request
```bash
echo -e "POST /postscript.php HTTP/1.1\r\nHost: localhost:5500\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 16\r\n\r\nname=john&age=27" | nc localhost 5500
```

## PHP Support

This simple Python web server can also serve PHP files. The server uses the subprocess module to execute the PHP interpreter and return the output to the client.

Please make sure that PHP is installed on the server and that the php-cgi executable is available in the system PATH for this feature to work correctly.

## Deploying the Server as a Service on Ubuntu LTS Server with Ansible

You can use the provided Ansible playbook to deploy the server as a service on an Ubuntu LTS server. The script is located in the `Ansible` directory and is named `deploy_server.yml`.

To run the Ansible script, use the following command:

```bash
ansible-playbook -i inventory.ini deploy_server.yml --ask-become-pass
```

## Docker Deployment

You can easily deploy the web server using Docker with the provided `docker-compose.yml` file.

```bash
docker-compose up -d
```

This will create two web server instances, an Nginx reverse proxy, and an HAProxy container. The HAProxy will load balance the traffic between the two web server instances, while the Nginx reverse proxy will forward requests to the appropriate backend service through the HAProxy.

To stop the Docker containers and remove the created resources, run:

```bash
docker-compose down
```






