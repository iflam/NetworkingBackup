#include "incl.h"

#define MAXLINE 1024

int main() {
	char sendline[MAXLINE], recvline[MAXLINE];

	int pipefd[2];

	pipe(pipefd);

	pid_t pid = fork();

	if(pid == 0) { // child 
		close(pipefd[1]);
		char *args[5];
		args[0] = "xterm";
		args[1] = "-e";
		args[2] = "./child";
		args[3] = calloc(sizeof(int)+1, sizeof(char));
		args[4] = NULL;
		snprintf(args[3], sizeof(int)+1, "%d", pipefd[0]); // give child pipefd as arg
		if(execvp(args[0], args) < 0)
			perror("exec error");
		
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
