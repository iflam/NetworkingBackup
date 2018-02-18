#include "incl.h"

#define MAXLINE 1024

int main() {
	char sendline[MAXLINE];
	int client2chat[2], chat2client[2]; //pipes

	pipe(client2chat);
	pipe(chat2client);

	char *args[6];
	args[0] = "xterm";
	args[1] = "-e";
	args[2] = "./chat";
	args[3] = calloc(5, sizeof(char));
	args[4] = calloc(5, sizeof(char));
	args[5] = NULL;
	snprintf(args[2], 5, "%d", client2chat[0]);
	snprintf(args[3], 5, "%d", chat2client[1]);

	pid_t pid = fork();
	if(pid == 0) { //child
		if(execvp(args[0], args) < 0)
			perror("exec error");
	}
	/*else { //parent
		while(1) {
			fgets(sendline, MAXLINE, stdin);
			write(client2chat[1], sendline, strlen(sendline));
		}
	}*/
}
