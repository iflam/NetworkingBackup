#include "incl.h"
#include "chat.h"

int client2chat, chat2client; // pipe ends
int main(int argc, char *argv[]) {
	char *name = argv[4];
	char *tpmorp = calloc(strlen(KCYN)+strlen(name)+strlen(TPMORP)+1,sizeof(char));
	strcpy(tpmorp,KCYN);
	strcat(tpmorp,name);
	strcat(tpmorp,TPMORP);
	char sendline[MAXLINE+1], recvline[MAXLINE+1];

	signal(SIGTERM, termHandler);

	if(argc != ARGC)
		err_quit("usage: chat <client2chat pipefd> <chat2client pipefd> <msg> <name>\n");

	client2chat = atoi(argv[RPIPE_ARG]);
	chat2client = atoi(argv[WPIPE_ARG]);
	char *msg = argv[MSG_ARG];

	fd_set rfds, rfds_init;

	FD_ZERO(&rfds_init);
	FD_SET(fileno(stdin), &rfds_init);
	FD_SET(client2chat, &rfds_init);

	int maxfd = client2chat;

	if(strlen(msg) != 0) {
		printf(PROMPT);
		printf("%s\n", msg);
		printf(PROMPT);
	}
	fflush(stdout);

	while(1) {
		rfds = rfds_init;
		if(select(maxfd+1, &rfds, NULL, NULL, NULL) < 0)
			err_sys("select error\n");
		if(FD_ISSET(fileno(stdin), &rfds)) {
			fgets(sendline, MAXLINE, stdin); // read stdin
			write(chat2client, sendline, strlen(sendline)); // send to client
			printf(PROMPT);
			fflush(stdout);
		}
		if(FD_ISSET(client2chat, &rfds)) {
			int n = read(client2chat, recvline, MAXLINE);
			recvline[n] = 0; // chomp newline
			printf("\n%s",tpmorp);
			printf("%s", recvline);
			printf(PROMPT);
			fflush(stdout);
		}
	}
}

void termHandler(int sig) {
	close(client2chat);
	close(chat2client);
}
