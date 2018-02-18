#include "incl.h"
#include "client.h"

int main(int argc, char** argv) {
	int sockfd;
	char linebuf[MAXLINE+1];
	char *username;
	int client2chat[2], chat2client[2]; // pipes

	pipe(client2chat);
	pipe(chat2client);

	if(argc != ARGC)
		err_quit("usage: client <Name> <IPaddress> <port>\n");

	if(strlen(argv[NAME_ARG]) > MAXNAME)
		err_quit("username too long\n");
	username = argv[NAME_ARG];

	if((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0) 
		err_sys("socket error\n");

	ConnectSocket(sockfd, argv);

	pid_t pid = fork();

	if(pid == 0) { // child (chat window)
		CreateChatWindow(client2chat, chat2client);
	}
	else { // parent (client) -> the whole select schpiel
		fd_set rfds, rfds_init;

		FD_ZERO(&rfds_init);
		FD_SET(fileno(stdin), &rfds_init); // prepare to read from stdin
		FD_SET(sockfd, &rfds_init); // prepare to read from server
		FD_SET(chat2client[READ], &rfds_init); // prepare to read from chat window

		int maxfd = max(sockfd, chat2client[READ]);

		int readcount;
		while(1) {
			rfds = rfds_init;
			if(select(maxfd+1, &rfds, NULL, NULL, NULL) == -1)
				err_sys("select error\n");
			/*if(FD_ISSET(fileno(stdin), &rfds)) { 
				fgets(sendline, MAXLINE, stdin); // read stdin
				write(sockfd, sendline, strlen(sendline)); // send to server
			}*/
			if(FD_ISSET(sockfd, &rfds)) { 
				if((readcount = read(sockfd, linebuf, MAXLINE)) == 0) // read from server
					err_quit("EOF\n"); 
				linebuf[readcount] = 0; // null-terminate
				write(client2chat[WRITE], linebuf, strlen(linebuf)); // write to chat window
			}
			if(FD_ISSET(chat2client[READ], &rfds)) {
				if((readcount = read(chat2client[READ], linebuf, MAXLINE)) == 0) // read from chat window
					err_quit("EOF\n");
				linebuf[readcount] = 0; // null-terminate
				write(sockfd, linebuf, strlen(linebuf)); // write to server 
			}
		}
	}
}

void CreateChatWindow(int client2chat[2], int chat2client[2]) {
	char *args[6];
	args[0] = "xterm";
	args[1] = "-e";
	args[2] = "./chat";
	args[3] = calloc(FD_SZ_CHAR+1, sizeof(char));
	args[4] = calloc(FD_SZ_CHAR+1, sizeof(char));
	args[5] = NULL;
	snprintf(args[3], FD_SZ_CHAR, "%d", client2chat[READ]); 
	snprintf(args[4], FD_SZ_CHAR, "%d", chat2client[WRITE]);
	if(execvp(args[0], args) < 0) 
		perror("exec error"); 
}

void ConnectSocket(int sockfd, char **argv) {
	struct sockaddr_in servaddr;

	memset(&servaddr, 0, sizeof(servaddr));
	servaddr.sin_family = AF_INET;
	servaddr.sin_port = htons(atoi(argv[PORT_ARG]));
	if(strcmp(argv[IP_ARG], "localhost") == 0) argv[IP_ARG] = "127.0.0.1";
	if(inet_pton(AF_INET, argv[IP_ARG], &servaddr.sin_addr) <= 0)
		err_quit("inet_pton error for %s\n", argv[IP_ARG]);

	if(connect(sockfd, (struct sockaddr*)&servaddr, sizeof(servaddr)) < 0)
		err_quit("connect error\n");
}

int max(int a, int b) {
	if(a > b) return a;
	return b;
}
