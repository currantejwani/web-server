import sys


def parser(reqt):
    try:
        lines = reqt.strip().split("\r\n")

        reqt_line = lines[0].strip()
        rlp = reqt_line.split()

        if len(rlp) != 3:
            return "HTTP/1.1 400 Bad Request\r\n\r\n"
        if rlp[2] != "HTTP/1.1":
            return "HTTP/1.1 400 Bad Request\r\n\r\n"

        # Getting the request method
        method = rlp[0]
        if method not in ["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT"]:
            return "HTTP/1.1 400 Bad Request\r\n\r\n"

        # Checking if the headers are valid
        headers = {}
        for line in lines[1:]:
            header = line.split(":", 1)
            if len(header) != 2:
                return "HTTP/1.1 400 Bad Request\r\n\r\n"
            headers[header[0].strip()] = header[1].strip()

        return "HTTP/1.1 200 OK\r\n\r\n"
    except:
        return "HTTP/1.1 500 Internal Server Error\r\n\r\n"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Error: File path")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path, "r") as file:
            req = file.read()
    except:
        print("Error: File Read\n\n")
        sys.exit(1)

    response = parser(req)
    print(response)
