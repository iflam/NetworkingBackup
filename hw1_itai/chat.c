#include "incl.h"
#include "chat.h"

int main(int argc, char *argv[]) {
	char sendline[MAXLINE+1], recvline[MAXLINE+1];
	int client2chat, chat2client; // pipe ends

	if(argc != ARGC)
		err_quit("usage: chat <client2chat pipefd> <chat2client pipefd>\n");

	client2chat = atoi(argv[RPIPE_ARG]);
	chat2client = atoi(argv[WPIPE_ARG]);

	fd_set rfds, rfds_init;

	FD_ZERO(&rfds_init);
	FD_SET(fileno(stdin), &rfds_init);
	FD_SET(client2chat, &rfds_init);

	int maxfd = client2chat;

	printf(PROMPT);
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
			recvline[n] = 0;
			printf(TPMORP);
			fputs(recvline, stdout);
			printf(PROMPT);
			fflush(stdout);
		}
	}
}

