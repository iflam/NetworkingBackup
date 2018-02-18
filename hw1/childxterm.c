#include "incl.h"

#define MAXLINE 1024

int main(int argc, char *argv[]) {
	char sendline[MAXLINE], recvline[MAXLINE];

	int pipefd[2];
	pipefd[0] = atoi(argv[1]);
	pipefd[1] = atoi(argv[2]);
	printf("write end %d\n", pipefd[1]);

	fd_set rfds, rfds_init;

	int maxfd = pipefd[0];

	FD_ZERO(&rfds_init);
	FD_SET(fileno(stdin), &rfds_init);
	FD_SET(pipefd[0], &rfds_init);

	while(1) {
		rfds = rfds_init;
		if(select(maxfd+1, &rfds, NULL, NULL, NULL) < 0)
			err_sys("select error\n");
		if(FD_ISSET(fileno(stdin), &rfds)) { 
			fgets(sendline, MAXLINE, stdin); 
			if(write(pipefd[1], sendline, strlen(sendline)) <= 0)
				perror("write error"); 
		}
		if(FD_ISSET(pipefd[0], &rfds)) { 
			if(read(pipefd[0], recvline, MAXLINE) == 0)
				err_quit("EOF\n"); 
			fputs(recvline, stdout);
		}
	}
/* SELECT
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
	}*/
}
