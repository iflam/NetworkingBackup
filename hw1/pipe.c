#include "incl.h"

#define MAXLINE 1024

int main() {
	char sendline[MAXLINE], recvline[MAXLINE];

	int pipefd[2];

	pipe(pipefd);

	pid_t pid = fork();

	if(pid == 0) { // child 
		close(pipefd[1]);
		while(1) {
			int n = read(pipefd[0], recvline, MAXLINE);
			recvline[n] = 0; // null-terminate
			printf("(child) received msg:\n");
			fputs(recvline, stdout);
		}
	}
	else {
		close(pipefd[0]);
		while(1) {
			printf("(parent) write a msg:\n");
			fgets(sendline, MAXLINE, stdin);
			write(pipefd[1], sendline, strlen(sendline));
		}
	}
}
