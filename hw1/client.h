#pragma once

#define ARGC 4
#define MAXLINE 4096
#define MAXNAME 10
#define NAME_ARG 1
#define IP_ARG 2
#define PORT_ARG 3

#define READ 0
#define WRITE 1

#define FD_SZ_CHAR 4

void ConnectSocket(int sockfd, char **argv);
void CreateChatWindow(int client2chat[2], int chat2client[2]);
