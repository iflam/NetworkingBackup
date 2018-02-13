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

int main(int argc, char** argv) {
	int sockfd;
	char sendline[MAXLINE+1], recvline[MAXLINE+1];
	struct sockaddr_in servaddr;

	if(argc != 3)
		err_quit("usage: a.out <IPaddress> <port>\n");

	if((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0) 
		err_sys("socket error\n");

	memset(&servaddr, 0, sizeof(servaddr));
	servaddr.sin_family = AF_INET;
	servaddr.sin_port = htons(atoi(argv[2]));
	if(strcmp(argv[1], "localhost") == 0) argv[1] = "127.0.0.1";
	if(inet_pton(AF_INET, argv[1], &servaddr.sin_addr) <= 0)
		err_quit("inet_pton error for %s\n", argv[1]);

	if(connect(sockfd, (struct sockaddr*)&servaddr, sizeof(servaddr)) < 0)
		err_quit("connect error\n");

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

