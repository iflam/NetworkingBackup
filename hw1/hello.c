#include<stdlib.h>
#include<stdio.h>
#include<string.h>
#include<unistd.h>
#include<sys/types.h>
#include<sys/socket.h>
#include<arpa/inet.h>

#include "consts.h"
#include "err_msg.h"

int main(int argc, char** argv) {
	int sockfd, n;
	char recvline[MAXLINE+1];
	struct sockaddr_in servaddr;

	if(argc != 3)
		err_quit("usage: a.out <IPaddress> <port>\n");

	if((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0) 
		err_sys("socket error\n");

	memset(&servaddr, 0, sizeof(servaddr));
	servaddr.sin_family = AF_INET;
	servaddr.sin_port = htons(atoi(argv[2]));
	if(inet_pton(AF_INET, argv[1], &servaddr.sin_addr) <= 0)
		err_quit("inet_pton error for %s\n", argv[1]);

	if(connect(sockfd, (struct sockaddr*)&servaddr, sizeof(servaddr)) < 0)
		err_quit("connect error\n");

	while((n = read(sockfd, recvline, MAXLINE)) > 0) {
		printf("%d bytes read:\n", n);
		recvline[n] = 0; 
		if(fputs(recvline, stdout) == EOF) 
			err_sys("EOF error\n");
	}
	if(n < 0)
		err_sys("read error\n");

	exit(0);
}

