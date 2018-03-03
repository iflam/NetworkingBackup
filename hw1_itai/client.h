#pragma once

#define ARGC 4
#define MAXLINE 1024 
#define MAXNAME 10
#define NAME_ARG 1
#define IP_ARG 2
#define PORT_ARG 3
#define ENDLINE "\r\n\r\n"
#define _ME2U "ME2U" ENDLINE
#define _U2EM "U2EM" ENDLINE
#define _IAM "IAM " 
#define _ETAKEN "ETAKEN" ENDLINE
#define _MAI "MAI" ENDLINE
#define _MOTD "MOTD " 
#define _LISTU "LISTU" ENDLINE
#define _BYE "BYE" ENDLINE
#define _UTSIL "UTSIL"
#define _MORF "MORF "
#define _EDNE "EDNE "

#define READ 0
#define WRITE 1

#define FD_SZ_CHAR 4

void ConnectSocket(int sockfd, char **argv);
void CreateChatWindow(int client2chat[2], int chat2client[2], char *to_name);

void readuntil(int sockfd, char *buf, char *str);
void readuntilend(int sockfd, char *buf);

void Login(int sockfd, char *username);
void Logout(int sockfd, char *username);
void sendmrof(int sockfd, char* name);
void sendDNE(int sockfd, char* name);
void sendme2u(int sockfd);
void readme2u(int sockfd);
void sendiam(int sockfd, char *username);
void readmai(int sockfd);
void readmotd(int sockfd);
void sendlist(int sockfd);
void printhelp();
void blockuntilOT(int sockfd);
int blockuntil(int sockfd, char *reply);
void handlefrom(int sockfd);

void replyloop(int sockfd, char *cmd);

char *strrev(char *str);

typedef struct chat chat;
struct chat{
    char* name;
    int readfd;
    int writefd;
    int pid;
    chat* next;
};

chat* removeChat(chat* chats, chat* remChat);

typedef enum cmd_type{HELP=1, LOG=2, LIST=3,CHAT=4,ERR=5} Cmd_type;
typedef struct {
	enum cmd_type cmdt;
	char* to; //NULL when anything but CHAT
	char* msg; //NULL when anything but CHAT
} cmd;
cmd* parse_cmsg(char* in);
char* makeTo(char *to, char *msg);

typedef enum server_cmd_type{U2EM, ETAKEN, MAI, MOTD, UTSIL, FROM, OT, EDNE, EYB, UOFF} Server_cmd_type;
typedef struct {
    enum server_cmd_type cmdt;
    char* to; //NULL when not FROM or EDNE or UOFF or OT
    char* msg; //NULL when not FROM or MOTD
    char** users; //NULL when not UTSIL
} server_cmd;

server_cmd* parse_server_msg(char* in, Server_cmd_type type);
char** make_users(char* string);

enum replies          { TO_R, FROM_R, LISTU_R, IAM_R, BYE_R, ME2U_R };
const char* reply[] = { "OT", "MORF", "UTSIL", "MAI", "EYB", "U2EM" };
