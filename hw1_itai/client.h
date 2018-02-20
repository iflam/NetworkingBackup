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

typedef struct chat chat;
struct chat{
    char* name;
    int readfd;
    int writefd;
    int pid;
    chat* next;
};
typedef enum cmd_type{HELP=1, LOG=2, LIST=3,CHAT=4,ERR=5} Cmd_type;
typedef struct {
	enum cmd_type cmdt;
	char* to; //NULL when anything but CHAT
	char* msg; //NULL when anything but CHAT
} cmd;
cmd* parse_cmsg(char* in);
char* makeTo(cmd* command);

typedef enum server_cmd_type{U2EM, ETAKEN, MAI, MOTD, UTSIL, FROM, OT, EDNE, EYB, UOFF} Server_cmd_type;
typedef struct {
    enum server_cmd_type cmdt;
    char* to; //NULL when not FROM or EDNE or UOFF or OT
    char* msg; //NULL when not FROM or MOTD
    char** users; //NULL when not UTSIL
} server_cmd;

server_cmd* parse_server_msg(char* in);
char** make_users(char* string);
