#

# myWebServer.py

#

# Josh Sigurdson - 7858405

#


import socket
import threading
import sys
import os
import uuid
import json
import tempfile


HOST = ''


def main():

    if len(sys.argv) < 2:
        print("Supply a port to run webServer.py.\nUse the format \"python3 webServer.py [port-number]\"")
        sys.exit()

    PORT = int(sys.argv[1])

    # Create a socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to a specific address and port
    server_socket.bind((HOST, PORT))
    print(f"Server started on port {PORT}.")

    # Start listening for incoming connections
    server_socket.listen()

    while True:

        # Accept a new connection

        client_socket, address = server_socket.accept()

        # Start a new thread to handle the request

        t = threading.Thread(target=handle_request,
                             args=(client_socket, address))
        t.start()


def handle_request(client_socket, address):

    # Receive request

    request = client_socket.recv(2048).decode()
    response = ""
    print(request)

    print(f"Connected by {address}")
    # Extract the path from the request
    if request:
        
        path, method, body, protocol, cookie = parse_request(request)

        if method == "GET" and (path == "/" or path == "/index.html"):

            path = '/index.html'
            with open("index.html", "r") as f:
                content = f.read()

            response = buildResponse(content)
        elif method == "GET" and path == "/style.css":

            path = "/style.css"
            with open("style.css", "r") as f:
                content = f.read()

            response = buildResponseCSS(content)

        elif method == "GET" and path == "/script.js":

            path = "/script.js"
            with open("script.js", "r") as f:
                content = f.read()

            response = buildResponseJS(content)

        elif method == "GET" and path == "/images.html":

            path = "/images.html"
            with open("images.html", "r") as f:
                content = f.read()

            response = buildResponse(content)

        elif method == "POST" and path == "/api/images":
            content_length = get_content_length(request)
            filename = str(uuid.uuid4()) + '.png'  # Assume the image is in PNG format
            filepath = os.path.join('images', filename)

            with open(filepath, 'wb') as image_file:
                image_file.write(body.encode())

            response = "HTTP/1.1 200 OK\r\n\r\nImage uploaded successfully"

        elif method == "GET" and path == "/api/images":
            path = "/api/images"
            with open("images", "r") as f:
                content = f.read()
            response = self.build_response_json(content)

        elif method == "GET" and path.endswith('jpeg'):
            print(f"{method} {path} {protocol}\n")
            try:
                with open("."+path, "rb") as f:

                    content = f.read()

                response = buildResponseImage(content, "image/jpeg")
                client_socket.sendall(response)
                client_socket.close()
                response = ""
            except FileNotFoundError:
                print(f"Image not found at {path}")

        elif method == "POST" and path == "/api/login":  # login
            cookie = login(body)
            print(cookie)

            if cookie:
                response = buildResponseCookie(cookie)
            else:
                response = buildErrorResponse("400")

        elif method == "POST" and path == "/api/tweet":  # add tweets
            print(f"{method} {path} {protocol}\n {body}")
            response = buildResponseJSON(addTweet(body))
            response = testCookie(cookie, response, "403")

        elif method == "GET" and path == "/api/tweet":  # get tweets

            response = buildResponseJSON(getTweets())
            response = testCookie(cookie, response, "403")

        elif method == "GET" and path.startswith("/api/tweet/"): # get specific tweet
            print(f"{method} {path} {protocol}\n1")
            tweet_id = path.split("/")
            tweet_id = int(tweet_id[3])
            response = buildResponseJSON(getTweet(tweet_id))
            response = testCookie(cookie, response, "403")
            if 'null' in response:
                response = buildErrorResponse("404")
        # delete tweet
        elif method == "DELETE" and path.startswith("/api/tweet/"):
            tweet_id = path.split("/")
            tweet_id = tweet_id[3]

            response = testCookie(cookie, response, "403")

            if "HTTP/1.1 4" not in response:
                response = buildResponse(deleteTweet(tweet_id))

        elif method == "DELETE" and path == "/api/login":  # logout

            response = buildResponseLogout("logged out")
            response = testCookie(cookie, response, "403")
        else:
            response = buildErrorResponse("404")

    if response:
        client_socket.sendall(response.encode())

    client_socket.close()


def get_content_length(request_data):
    for line in request_data.split('\n'):
        if line.startswith('Content-Length:'):
            return int(line.split(':')[1].strip())
    return 0

def login(body):

    json_obj = json.loads(body)

    with open("db.json", "r") as db:

        data = json.load(db)
        db.close()

    users = data["users"]

    for user in users:

        if user["username"] == json_obj["user"] and user["pass"] == json_obj["pass"]:
            return json_obj


def getTweets():

    # get the tweets from the json

    with open("db.json", "r") as db:

        data = json.load(db)

    tweets = data["tweets"]

    tweet_obj = []

    for tweet in tweets:

        tweet_obj.append(tweet)

    return tweet_obj

def getTweet(tweet_id):

    with open('db.json') as f:
        data = json.load(f)
        tweets = data['tweets']
        for tweet in tweets:
            if tweet['tweet_id'] == tweet_id:
                return json.dumps(tweet)
        return None


def addTweet(body):

    json_tweet = json.loads(body)

    with open("db.json", "r") as db:

        data = json.load(db)
        db.close()

    json_tweet['tweet_id'] = id(len(data['tweets']))
    json_tweet['tweet_str'] = json_tweet['tweet_str'].strip()
    data["tweets"].append(json_tweet)

    with open("db.json", "w") as db:

        json.dump(data, db, indent=4)
        db.close()

    return json_tweet


def deleteTweet(index):

    index = index.strip()

    with open('db.json', 'r') as f:

        db = json.load(f)

        f.close()

    tweets = db['tweets']

    for tweet in tweets:

        if str(tweet['tweet_id']) == index:

            tweets.remove(tweet)

            break

    with open('db.json', 'w') as f:

        json.dump(db, f, indent=4)

        f.close()

    return index


def parse_request(request):

    # Parse HTTP request

    request_lines = request.split("\r\n")

    body = getLastLine(request).strip()

    cookie = request_lines[len(request_lines)-3]

    method, path, protocol = request_lines[0].split(" ")

    return path, method, body, protocol, cookie


def getLastLine(inStr):

    lines = inStr.split("\n")

    return lines[len(lines)-1]

def testCookie(cookie, response, error):
    # Extract the username
    username = cookie.split('=')[1]

    # Load the user database
    with open('db.json', 'r') as f:
        user_db = json.load(f)

    # Check if the username exists in the user database
    for user in user_db['users']:
        if user['username'] == username:
            return response

    return buildErrorResponse(error)


def buildResponseJSON(jsonObj):

    return "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(json.dumps(jsonObj))) + "\r\n\r\n" + json.dumps(jsonObj)


def buildResponse(content):

    return "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {}\r\n\r\n{}".format(

        len(content), content)

def buildResponseCSS(content):

    return "HTTP/1.1 200 OK\r\nContent-Type: text/css\r\nContent-Length: {}\r\n\r\n{}".format(

        len(content), content)


def buildResponseJS(content):
    
        return "HTTP/1.1 200 OK\r\nContent-Type: application/javascript\r\nContent-Length: {}\r\n\r\n{}".format(
    
            len(content), content)

def buildResponseCookie(cookie):
    headers = "HTTP/1.1 200 OK\r\n"
    headers += "Content-Type: text/html\r\n"
    headers += f"Set-cookie: username={cookie['user']}; Max-Age: 3600; Path=/\n\r"
    headers += "Content-Length " + str(len(cookie)) + "\r\n\r\n"

    response = headers + cookie['user']
    return response


def buildResponseLogout(body):
    headers = "HTTP/1.1 200 OK\r\n"
    headers += "Content-Type: text/html\r\n"
    headers += f"Set-cookie: username=-1; Path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT\n\r"
    headers += "Content-Length " + str(len(body)) + "\r\n\r\n"

    response = headers + body
    return response


def buildResponseImage(data, type):
    # build response in binary
    headers = "HTTP/1.1 200 OK\r\n"
    headers += f"Content-Type: {type}\r\n"
    headers += "Content-Length: " + str(len(data)) + "\r\n"
    headers += "\r\n"

    # Combine headers and binary data to form the HTTP response
    response = headers.encode() + data

    return response


def buildErrorResponse(error):
    if error == "404":
        return f"HTTP/1.1 {error} Not Found\r\n\r\n"
    elif error == "403":
        return f"HTTP/1.1 {error} Forbidden\r\n\r\n"
    elif error == "400":
        return f"HTTP/1.1 {error} Bad Request\r\n\r\n"
    else:
        return f"HTTP/1.1 Error Code Undefined\r\n\r\n"


if __name__ == "__main__":

    main()
