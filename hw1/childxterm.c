#include "incl.h"

#define MAXLINE 1024

int main(int argc, char *argv[]) {
	char sendline[MAXLINE], recvline[MAXLINE];

	while(1) {
		int n = read(atoi(argv[1]), recvline, MAXLINE);
		recvline[n] = 0; // null-terminate
		printf("(child) received msg:\n");
		fputs(recvline, stdout);
	}

}
