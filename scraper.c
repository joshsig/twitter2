#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <sys/socket.h>
#include <arpa/inet.h>

#include <netdb.h>  // For getaddrinfo
#include <unistd.h> // for close
#include <stdlib.h> // for exit

int main(int argc, char *argv[])
{
    int socket_desc;
    struct sockaddr_in server_addr;
    char server_message[2000], client_message[2000];
    char address[100];

    char *username;
    char *password;
    char *tweet;

    struct addrinfo *result;

    if (argc < 4)
    {
        printf("Error: username, password, and tweet are required arguments\n");
        return 0;
    }

    username = argv[1];
    password = argv[2];

    // Get the tweet text
    tweet = malloc(strlen(argv[3]) + 1);
    strcpy(tweet, argv[3]);

    for (int i = 4; i < argc; i++)
    {
        tweet = realloc(tweet, strlen(tweet) + strlen(argv[i]) + 2);
        strcat(tweet, " ");
        strcat(tweet, argv[i]);
    }

    printf("The tweet is>%s<\n", tweet);

    // Clean buffers:
    memset(server_message, '\0', sizeof(server_message));
    memset(client_message, '\0', sizeof(client_message));

    // Create socket:
    socket_desc = socket(AF_INET, SOCK_STREAM, 0);

    if (socket_desc < 0)
    {
        printf("Unable to create socket\n");
        return -1;
    }

    struct addrinfo hints;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = PF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags |= AI_CANONNAME;

    // get the ip of the page we want to scrape
    int out = getaddrinfo("localhost", NULL, &hints, &result);
    // fail gracefully
    if (out != 0)
    {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(out));
        exit(EXIT_FAILURE);
    }

    // ai_addr is a struct sockaddr
    // so, we can just use that sin_addr
    struct sockaddr_in *serverDetails = (struct sockaddr_in *)result->ai_addr;

    // Set port and IP the same as server-side:
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(8080);
    // server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    server_addr.sin_addr = serverDetails->sin_addr;

    // converts to octets
    printf("Converting...\n");
    inet_ntop(server_addr.sin_family, &server_addr.sin_addr, address, 100);
    printf("Connecting to %s\n", address);
    // Send connection request to server:
    if (connect(socket_desc, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    {
        printf("Unable to connect\n");
        exit(EXIT_FAILURE);
    }
    // server connected successfully
    printf("\nConnected with server successfully\n");

    // login
    int req_length = strlen(username) + strlen(password);
    char *json_string = malloc(req_length + 20);
    sprintf(json_string, "{\"user\":\"%s\",\"pass\":\"%s\"}", username, password);

    char *headers = malloc(sizeof(char) * 70);
    sprintf(headers, "POST /api/login HTTP/1.1\r\nContent-Length: %d\r\n\r\n", req_length);

    char *request = malloc(strlen(json_string) + strlen(headers) + 10);
    strcat(request, headers);
    strcat(request, json_string);

    printf("Sending:\n%s\n", request);
    // Send the message to server:
    printf("Sending request, %lu bytes\n", strlen(request));
    if (send(socket_desc, request, strlen(request), 0) < 0)
    {
        printf("Unable to send message\n");
        return -1;
    }

    // Receive the server's response:
    if (recv(socket_desc, server_message, sizeof(server_message), 0) < 0)
    {
        printf("Error while receiving server's msg\n");
        return -1;
    }

    printf("Server's response: %s\n", server_message);

    printf("logged in?\n");
    assert(strstr(server_message, username));

    // ------------------- END OF LOGIN TEST -------------------

    free(json_string);
    free(request);
    free(headers);

    close(socket_desc);

    // --------------- RECONNECT ---------------

    // Clean buffers:
    memset(server_message, '\0', sizeof(server_message));
    memset(client_message, '\0', sizeof(client_message));

    // Create socket:
    socket_desc = socket(AF_INET, SOCK_STREAM, 0);

    if (socket_desc < 0)
    {
        printf("Unable to create socket\n");
        return -1;
    }

    out = getaddrinfo("localhost", NULL, &hints, &result);
    // fail gracefully
    if (out != 0)
    {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(out));
        exit(EXIT_FAILURE);
    }

    // Set port and IP the same as server-side:
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(8080);
    // server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    server_addr.sin_addr = serverDetails->sin_addr;

    // Send connection request to server:
    if (connect(socket_desc, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    {
        printf("Unable to connect\n");
        exit(EXIT_FAILURE);
    }
    // server connected successfully
    printf("\nConnected with server successfully\n");

    // ------------------- TEST Post Tweet Functionality -------------------

    json_string = malloc(strlen(tweet) + strlen(username) + 10);
    sprintf(json_string, "{\"tweet_id\": \"-1\",\"tweet_str\":\"%s\",\"username\":\"%s\"}", tweet, username);

    headers = malloc(sizeof(char) * 70);
    sprintf(headers, "POST /api/tweet HTTP/1.1\r\nCookie: username=%s\r\n\r\n", username);

    request = malloc(strlen(json_string) + strlen(headers) + 10);
    strcat(request, headers);
    strcat(request, json_string);

    printf("Sending:\n%s\n", headers);
    // Send the message to server:
    printf("Sending request, %lu bytes\n", strlen(request));
    if (send(socket_desc, request, strlen(request), 0) < 0)
    {
        printf("Unable to send message\n");
        return -1;
    }

    // Receive the server's response:
    if (recv(socket_desc, server_message, sizeof(server_message), 0) < 0)
    {
        printf("Error while receiving server's msg\n");
        return -1;
    }

    printf("Server's response:\n %s\n", server_message);

    // Post tweet

    free(json_string);
    free(request);

    // Close the socket:
    close(socket_desc);

    // --------------- RECONNECT ---------------

    // Clean buffers:
    memset(server_message, '\0', sizeof(server_message));
    memset(client_message, '\0', sizeof(client_message));

    // Create socket:
    socket_desc = socket(AF_INET, SOCK_STREAM, 0);

    if (socket_desc < 0)
    {
        printf("Unable to create socket\n");
        return -1;
    }

    out = getaddrinfo("localhost", NULL, &hints, &result);
    // fail gracefully
    if (out != 0)
    {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(out));
        exit(EXIT_FAILURE);
    }

    // Set port and IP the same as server-side:
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(8080);
    // server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    server_addr.sin_addr = serverDetails->sin_addr;

    // Send connection request to server:
    if (connect(socket_desc, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    {
        printf("Unable to connect\n");
        exit(EXIT_FAILURE);
    }
    // server connected successfully
    printf("\nConnected with server successfully\n");

    // GET Test ensure that tweet was added. ------------

    request = malloc(25);

    sprintf(request, "GET /api/tweet HTTP/1.1\r\nCookie: username=%s", username);

    printf("Sending:\n%s\n", request);
    // Send the message to server:
    printf("Sending request, %lu bytes\n\n", strlen(request));
    if (send(socket_desc, request, strlen(request), 0) < 0)
    {
        printf("Unable to send message\n");
        return -1;
    }

    // Receive the server's response:
    if (recv(socket_desc, server_message, sizeof(server_message), 0) < 0)
    {
        printf("Error while receiving server's msg\n");
        return -1;
    }

    // printf("Server's response: %s\n", server_message);

    // test that the tweet has been added successfully!
    assert(strstr(server_message, tweet));

    // ---------------END OF TEST - POST api/tweet---------------

    return 0;
}
