#include "incl.h"

#define MAXLINE 1024

int main() {
	char sendline[MAXLINE], recvline[MAXLINE];

	int client2chat[2], chat2client[2]; //pipes

	pipe(client2chat);
	pipe(chat2client);

	pid_t pid = fork();

	if(pid == 0) { // child process
		close(client2chat[1]);
		close(chat2client[0]);

		char *args[6];
		args[0] = "xterm";
		args[1] = "-e";
		args[2] = "./child"; // xterm will run child program 
		args[3] = calloc(sizeof(int)+1, sizeof(char));
		args[4] = calloc(sizeof(int)+1, sizeof(char));
		args[5] = NULL;
		snprintf(args[3], sizeof(int)+1, "%d", client2chat[0]); // give child read end of client2chat pipe 
		snprintf(args[4], sizeof(int)+1, "%d", chat2client[1]); // give child write end of chat2client pipe 

		if(execvp(args[0], args) < 0) // run xterm
			perror("exec error");
	}
	else { // parent process
		close(client2chat[0]);
		close(chat2client[1]);

		fd_set rfds, rfds_init;

		int maxfd = chat2client[0];

		FD_ZERO(&rfds_init);
		FD_SET(fileno(stdin), &rfds_init);
		FD_SET(chat2client[0], &rfds_init);

		while(1) {
			rfds = rfds_init;
			if(select(maxfd+1, &rfds, NULL, NULL, NULL) < 0)
				err_sys("select error");
			if(FD_ISSET(fileno(stdin), &rfds)) {
				fgets(sendline, MAXLINE, stdin);
				write(client2chat[1], sendline, strlen(sendline));
			}
			if(FD_ISSET(chat2client[0], &rfds)) {
				if(read(chat2client[0], recvline, MAXLINE) == 0)
					err_quit("EOF\n");
				fputs(recvline, stdout);
			}
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
