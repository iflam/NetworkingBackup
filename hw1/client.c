#include<stdlib.h>
#include<stdio.h>
#include<string.h>
#include<unistd.h>
#include<sys/types.h>
#include<sys/socket.h>
#include<sys/select.h>
#include<arpa/inet.h>

#include "consts.h"
#include "err_msg.h"
#include "client.h"

int main(int argc, char** argv) {
	int sockfd;
	char sendline[MAXLINE+1], recvline[MAXLINE+1];
	char *username;

	if(argc != ARGS)
		err_quit("usage: client <Name> <IPaddress> <port>\n");

	Setusername(username, argv[NAME_ARG]);

	if((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0) 
		err_sys("socket error\n");

	ConnectSocket(sockfd, argv);

	fd_set rfds, rfds_init;

	FD_ZERO(&rfds_init);
	FD_SET(fileno(stdin), &rfds_init);
	FD_SET(sockfd, &rfds_init);

	while(1) {
		rfds = rfds_init;
		if(select(sockfd+1, &rfds, NULL, NULL, NULL) == -1)
			err_sys("select error\n");
		if(FD_ISSET(fileno(stdin), &rfds)) { 
			fgets(sendline, MAXLINE, stdin); // read stdin
			write(sockfd, sendline, strlen(sendline)); // send to sockfd
		}
		if(FD_ISSET(sockfd, &rfds)) { 
			if(read(sockfd, recvline, MAXLINE) == 0)
				err_quit("EOF\n"); 
			fputs(recvline, stdout);
		}
	}

	exit(0);
}

int setusername(char *dest, char *src) {
	if(strlen(src) > MAXNAME) 
		return NAME_LEN_ERR;
	dest = src;
	return 0;
}
void Setusername(char *dest, char *src) {
	switch(setusername(dest, src)) {
		case NAME_LEN_ERR:
			err_quit("Name too long. Must be <%d chars", MAXNAME);
	}
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
