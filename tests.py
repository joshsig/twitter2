import socket
import json
import sys
import os

HOST = ''

def sendDelete(user, tweet_id):
    request = f"DELETE /api/tweet/{tweet_id} HTTP/1.1\r\nCookie: username={user}\r\n\r\n"
    return request

def doGet(user):
     return f"GET /api/tweet HTTP/1.1\r\nCookie: username={user}\r\n\r\n"
    

def buildAddTweet(user, tweet):
    return f'POST /api/tweet HTTP/1.1\r\nContent-Length: {len(tweet)}\r\nCookie: username={user}\r\n\r\n{json.dumps(tweet)}'

def testList(tweet, tweet_list):
    for t in tweet_list:
        if tweet == t:
            return "Tweet has not been deleted from the database."
    return "Tweet not in GET. Tweet has been deleted successfully."

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

def connectServer(PORT):

    server_address = (HOST, PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect((HOST, PORT))

    return sock

def main():

    if(len(sys.argv) != 4):
        print("Run with the format: python3 tests.py [port] [username] [password]")
        sys.exit()

    PORT = int(sys.argv[1])

    username = sys.argv[2]
    password = sys.argv[3]

    tweet = {
        'tweet_id': '-1',
        'tweet_str': 'This tweet should be added from the test. :)',
        'username': f'{username}'
    }

    print("--- Start of Tests ---")

    sock = connectServer(PORT)
    # add the tweet we are going to delete
    sock.sendall(buildAddTweet(username, tweet).encode())
    response = sock.recv(1024)
    path, method, body, protocol, cookie = parse_request(response.decode())
    tweet = body
    assert(response.decode().startswith("HTTP/1.1 200 OK"))
    print("Tweet added from test.\n")

    sock.close()

    sock = connectServer(PORT)
    # get list of tweets
    sock.sendall(doGet(username).encode())
    response = sock.recv(1024) # should be list of tweets
    
    path, method, body, protocol, cookie = parse_request(response.decode())
    list_tweets = json.loads(body)
    tweet_deletable = list_tweets[len(list_tweets) - 1] # lets delete the last tweet
    
    sock.close()
    sock = connectServer(PORT)
    sock.sendall(sendDelete("rob", tweet_deletable['tweet_id']).encode())
    print("Sending delete from user: rob.\nShould fail to delete and be forbidden.")
    
    response = sock.recv(1024)
    print(response.decode())
    assert(response.decode().startswith("HTTP/1.1 403"))
    sock.close()
    print("Delete as incorrect user test passed.\n")

    sock = connectServer(PORT)
    sock.sendall(sendDelete(username, tweet_deletable['tweet_id']).encode())
    print(f"Sending delete from user: {username}.\nShould succeed and be OK.\n")

    response = sock.recv(1024)
    print(response.decode())
    sock.close()
    assert(response.decode().startswith("HTTP/1.1 200"))

    sock = connectServer(PORT)
    sock.sendall(doGet(username).encode())
    response = sock.recv(1024) # should be list of tweets
    path, method, body, protocol, cookie = parse_request(response.decode())
    list_tweets = json.loads(body)


    print("\nTest that tweet has been successfully deleted.")
    print(testList(tweet, list_tweets))

    sock.close()

    print("--- End of testing ---")


if __name__=='__main__':
    main()