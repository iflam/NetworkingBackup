#include "incl.h"
#include "client.h"

char linebuf[MAXLINE+1], sendbuf[MAXLINE+1], recvbuf[MAXLINE+1];
chat* chatlist = NULL;

int main(int argc, char** argv) {
	int sockfd;
	char *username;
	int client2chat[2], chat2client[2]; // pipes

	if(argc != ARGC)
		err_quit("usage: client <Name> <IPaddress> <port>\n");

	if(strlen(argv[NAME_ARG]) > MAXNAME)
		err_quit("username too long\n");
	username = argv[NAME_ARG];

	if((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0) 
		err_sys("socket error\n");

	ConnectSocket(sockfd, argv);

	Login(sockfd, username);

    fd_set rfds, rfds_init;

    FD_ZERO(&rfds_init);
    FD_SET(fileno(stdin), &rfds_init); // prepare to read from stdin
    FD_SET(sockfd, &rfds_init); // prepare to read from server
    FD_SET(chat2client[READ], &rfds_init); // prepare to read from chat window

    int maxfd = max(sockfd, chat2client[READ]);

    int readcount;
    while(1) {
    	puts("reached top");
	    rfds = rfds_init;
	    if(select(maxfd+1, &rfds, NULL, NULL, NULL) == -1)
		    err_sys("select error\n");
	    if(FD_ISSET(fileno(stdin), &rfds)) { 
		    if((readcount = read(fileno(stdin), linebuf, MAXLINE)) == 0) // read from stdin
			    err_quit("EOF\n"); 
		    linebuf[readcount] = 0; // null-terminate
			//char *cmd = strtok(linebuf, " ");
//			replyloop(sockfd, cmd);
		    cmd* command = parse_cmsg(linebuf);
		    switch(command->cmdt){
		    	case HELP:
					printhelp();
		    		break;
		    	case LOG:
					Logout(sockfd, username);
					break;
				case LIST:
					sendlist(sockfd);
		    		break;
		    	case CHAT:
		    		//fork here
		    		printf("to: %s, msg: %s",command->to,command->msg);
		    		pipe(client2chat);
					pipe(chat2client);
	    			pid_t pid = fork();
		    		if(pid == 0){ //child
		    			CreateChatWindow(client2chat,chat2client);
		    		}
		    		else{ //parent
						chat* t = malloc(sizeof(chatlist)); // TODO: wha?
		    			t->name = command->to;
		    			t->readfd = chat2client[READ];
		    			t->writefd = client2chat[WRITE];
		    			t->next = chatlist;
		    			t->pid = pid;
		    			chatlist = t;
		    			FD_SET(chat2client[READ], &rfds_init);
		    			maxfd = max(maxfd,chat2client[READ]);
		    			char* to_send = makeTo(command); //create TO <name> <msg>
		    			memset(linebuf,0,sizeof(linebuf));
		    			strcpy(linebuf,to_send);
		    			write(sockfd, linebuf, strlen(linebuf));
						blockuntilOT(sockfd);
		    		}
		    		break;
		    	default:
		    		puts("That is not a valid command");
		    		break;
		    } //end of switch
	    } //end of STDIN if

	    if(FD_ISSET(sockfd, &rfds)) { 
		    if((readcount = read(sockfd, linebuf, MAXLINE)) == 0) // read from server
			    err_quit("EOF\n"); 
		    linebuf[readcount] = 0; // null-terminate
			char *cmd = strtok(linebuf, " ");
			puts(cmd);
			//replyloop(cmd);
			if(strcmp(cmd, "FROM") == 0) { // handle FROM
				handlefrom(sockfd);
			}
			//else
			//	err_quit("Garbage, wasn't expecting %s\n", cmd);
		    //check for what it returns
		    /*server_cmd* command = parse_server_msg(linebuf, (Server_cmd_type)NULL);
		    //Switch based on command type
		    switch(command->cmdt){
				case OT:
					puts("read OT");
					break;
		    	case UTSIL:
		    		puts("Currently active users:");
		    		printf("%s",command->msg);
		    		char* i = strstr(linebuf,ENDLINE);
		    		while(i == NULL){
		    			memset(linebuf,0,sizeof(linebuf));
		    			read(sockfd,linebuf,MAXLINE);
		    			printf("%s",linebuf);
		    			i = strstr(linebuf,ENDLINE);
		    		}
		    		printf("\n");
		    		break;
		    	default:
		    		puts("Invalid server command. Quitting");
		    		exit(0);
		    		break;
		    }*/
		    //write(client2chat[WRITE], linebuf, strlen(linebuf)); // write to chat window
	    }	

	    chat* curr_chat = chatlist;
	    while(curr_chat){
	    	if(FD_ISSET(curr_chat->readfd, &rfds)) {
			    if((readcount = read(curr_chat->readfd, linebuf, MAXLINE)) == 0) // read from chat window
				    err_quit("EOF\n");
			    linebuf[readcount] = 0; // null-terminate
			    cmd* command = (cmd*)malloc(sizeof(cmd)); //utilize to and msg of command for makeTo() function
			    command->to = curr_chat->name;
			    command->msg = linebuf;
			    char* to_send = makeTo(command);
			    strcpy(linebuf,to_send);
			    write(sockfd, linebuf, strlen(linebuf)); // write to server 
			    free(command);
	   		}
	   		curr_chat = curr_chat->next;
	   	}
	}
}

void CreateChatWindow(int client2chat[2], int chat2client[2]) {
	char *args[6];
	args[0] = "xterm";
	args[1] = "-e";
	args[2] = "./chat";
	args[3] = calloc(FD_SZ_CHAR+1, sizeof(char));
	args[4] = calloc(FD_SZ_CHAR+1, sizeof(char));
	args[5] = NULL;
	snprintf(args[3], FD_SZ_CHAR, "%d", client2chat[READ]); 
	snprintf(args[4], FD_SZ_CHAR, "%d", chat2client[WRITE]);
	if(execvp(args[0], args) < 0) 
		perror("exec error"); 
}

void ConnectSocket(int sockfd, char **argv) {
	struct sockaddr_in servaddr;

	memset(&servaddr, 0, sizeof(servaddr));
	servaddr.sin_family = AF_INET;
	servaddr.sin_port = htons(atoi(argv[PORT_ARG]));
	if(strcmp(argv[IP_ARG], "localhost") == 0) argv[IP_ARG] = "127.0.0.1";
	if(inet_pton(AF_INET, argv[IP_ARG], &servaddr.sin_addr) <= 0)
		err_quit("inet_pton error for %s\n", argv[IP_ARG]);

	if(connect(sockfd, (struct sockaddr*)&servaddr, sizeof(servaddr)) < 0)
		err_quit("connect error\n");
}

int max(int a, int b) {
	if(a > b) return a;
	return b;
}

void Login(int sockfd, char *username) {
	sendme2u(sockfd);
	readme2u(sockfd);
	sendiam(sockfd, username);
	readuntilend(sockfd, linebuf);
	puts(linebuf);
	if(strcmp(linebuf, _ETAKEN) == 0)
		err_quit("username taken\n");
	if(strcmp(linebuf, _MAI) != 0)
		err_quit("read garbage, expected MAI\n");
	//readmai(sockfd);
	readmotd(sockfd);
}

void readuntil(int sockfd, char *buf, char *str) {
	memset(buf, 0, strlen(str));
	int n = 0;
	while(strcmp(str, buf) != 0) {
		n += read(sockfd, &buf[n], strlen(str)-n);
		buf[n] = 0;
		if(n > strlen(str)) {
			err_quit("Read garbage while reading until %s\n", str);
		}
	}
}
void readuntilend(int sockfd, char *buf) {
	int n = strlen(buf);
	memset(&buf[n], 0, MAXLINE-n);
	while(strcmp(&buf[n-strlen(ENDLINE)], ENDLINE) != 0) {
		n += read(sockfd, &buf[n], MAXLINE-strlen(buf)); // TODO: check bounds
		buf[n] = 0;
	}
}
void sendme2u(int sockfd) {
	int hello_len = strlen(_ME2U);
	linebuf[hello_len] = 0;
	strcat(linebuf, _ME2U);
	write(sockfd, linebuf, strlen(linebuf)); 
}
void readme2u(int sockfd) {
	int hello_len = strlen(_U2EM);
	readuntil(sockfd, linebuf, _U2EM);
	linebuf[hello_len] = 0;
	fputs(linebuf, stdout);
}
void sendiam(int sockfd, char *username) {
	memset(linebuf, 0, strlen(_IAM)+strlen(username)+strlen(ENDLINE)+1);
	strcpy(linebuf, _IAM);
	strcat(linebuf, username);
	strcat(linebuf, ENDLINE);
	write(sockfd, linebuf, strlen(linebuf));
	memset(linebuf, 0, strlen(linebuf));
}
void readmai(int sockfd) {
	readuntil(sockfd, linebuf, _MAI);
	printf("read mai\n");
}
void readmotd(int sockfd) {
	readuntil(sockfd, linebuf, _MOTD);
	printf("read motd\n");
	readuntilend(sockfd, linebuf);
	printf("read end\n");
	fputs(&linebuf[strlen(_MOTD)], stdout);
}

void printhelp() {
	printf("/help\n/chat <to> <msg>\n/listu\tlist users\n/logout\n");
}

typedef struct chat chat;

char* makeTo(cmd* command){
	char* string = malloc((strlen(command->to)+strlen(command->msg))*sizeof(char) + 16);
	memset(string,0,sizeof(string));
	strcat(string,"TO ");
	strcat(string,command->to);
	strcat(string," ");
	strcat(string,command->msg);
	strcat(string,ENDLINE);
	return string;

}

server_cmd* parse_server_msg(char* in, Server_cmd_type in_type){
	server_cmd* curr_cmd = (server_cmd*)malloc(sizeof(server_cmd));
	char* curr_token = (char*)malloc((strlen(in)+1)*sizeof(char));
	memset(curr_token, 0, sizeof(char));
	int pos = 0;
	char* currChar = in;
	curr_cmd->to = NULL;
	curr_cmd->msg = NULL;
	curr_cmd->users = NULL;
	curr_cmd->cmdt = in_type;
	while(*currChar != '\0'){
		while(*currChar == ' '){
			//go until no more spaces
			currChar++;
		}

		if(*currChar == '\0'){ //if end of line
			break;
		}

		if(curr_cmd->cmdt == UTSIL){
			char* string = strdup(currChar);
			curr_cmd->msg = string;
			return curr_cmd;
		}

		if(pos ==2 || curr_cmd->cmdt == MOTD){ //if reached 3rd section, it's just one remaining token.
			curr_cmd->msg = strdup(currChar);
			free(curr_token);
			return curr_cmd;
		}

		while(*currChar != ' ' && *currChar != '\n' && *currChar != '\0'){ //create token
			strncat(curr_token,currChar,1);	
			currChar++;
		}

		switch(pos){ //Depending on position, parse differently.
			case 0:
				if((strcmp(curr_token,"FROM"))==0){
				 	curr_cmd->cmdt = FROM;
				}
				else if((strcmp(curr_token,"U2EM"))==0){
				 	curr_cmd->cmdt = U2EM;
				 	return curr_cmd;
				}
				else if((strcmp(curr_token,"ETAKEN"))==0){
				 	curr_cmd->cmdt = ETAKEN;
				 	return curr_cmd;
				}
				else if((strcmp(curr_token,"MAI"))==0){
				 	curr_cmd->cmdt = MAI;
				 	return curr_cmd;
				}
				else if((strcmp(curr_token,"MOTD"))==0){
				 	curr_cmd->cmdt = MOTD;
				}
				else if((strcmp(curr_token,"UTSIL"))==0){
				 	curr_cmd->cmdt = UTSIL;
				}
				else if((strcmp(curr_token,"OT"))==0){
				 	curr_cmd->cmdt = OT;
				}
				else if((strcmp(curr_token,"EDNE"))==0){
				 	curr_cmd->cmdt = EDNE;
				}
				else if((strcmp(curr_token,"EYB"))==0){
				 	curr_cmd->cmdt = EYB;
				}
				else if((strcmp(curr_token,"UOFF"))==0){
				 	curr_cmd->cmdt = UOFF;
				}
				break;
			case 1:
				break;
			case 2:
				break;
			default:
				return NULL;
				break;
		}
	}
	free(curr_token);
	return NULL;
}

// char** make_users(char* string){
// 	char** users = malloc(strlen(string)*sizeof(char*)+sizeof(NULL));
// 	char* user = strtok(string," ");
// 	users[0] = user;
// 	int i = 1;
// 	while((user = strtok(NULL," ")) != NULL){
// 		users[i] = user;
// 		i++;
// 	}
// 	users[i] = "\0";
// 	return users;
// }

cmd* parse_cmsg(char* in){
	cmd* curr_cmd = (cmd*)malloc(sizeof(cmd));
	char* in_msg = (char*)malloc((strlen(in)+1)*sizeof(char));
	memset(in_msg, 0, sizeof(char));
	int pos = 0;
	char* currChar = in;
	while(*currChar != '\0'){
		while(*currChar == ' '){
			//go until no more spaces
			currChar++;
		}
		if(*currChar == '\0')
			break;

		if(pos == 2){
			curr_cmd->msg = strdup(currChar);
			free(in_msg);
			return curr_cmd;
		}
		while(*currChar != ' ' && *currChar != '\n' && *currChar != '\0'){
			strncat(in_msg,currChar,1);	
			currChar++;
		}

		switch(pos){
			case 0:
				curr_cmd->to = NULL;
				curr_cmd->msg = NULL;
				 if((strcmp(in_msg,"/help"))==0){
				 	curr_cmd->cmdt = HELP;
				 }
				 else if((strcmp(in_msg,"/logout")) == 0){
				 	curr_cmd->cmdt = LOG;
				 }
				 else if((strcmp(in_msg,"/listu")) == 0){
				 	curr_cmd->cmdt = LIST;
				 }
				 else if((strcmp(in_msg, "/chat")) == 0){
				 	curr_cmd->cmdt = CHAT;
				 }
				 else
				 	curr_cmd->cmdt = ERR;
				 if(curr_cmd->cmdt != CHAT){
				 	free(in_msg);
				 	return curr_cmd;
				 }
				 pos++;
				break;
			case 1:
				curr_cmd->to = strdup(in_msg);
				pos++;
				break;
			case 2:
				curr_cmd->msg = strdup(in_msg);
				break;
			default:
				return NULL;
				break;
		}

		memset(in_msg, 0, sizeof(char));
	}
	free(in_msg);
	return NULL;
}

void Logout(int sockfd, char *username) {
	puts("goodbye");
	strcpy(linebuf, _BYE);
	write(sockfd, linebuf, strlen(linebuf));
	chat* curr_chat = chatlist;
	while(curr_chat){
		kill(curr_chat->pid,SIGKILL);
		curr_chat = curr_chat->next;
	}
	//send close to server
	exit(0);
}

void sendlist(int sockfd) {
	strcpy(linebuf, _LISTU);
	linebuf[strlen(_LISTU)] = 0;
	write(sockfd, linebuf, sizeof(linebuf));
	//send request for users to server
}

void blockuntilOT(int sockfd) {
	while(1) {
		read(sockfd, linebuf, MAXLINE);
		char *cmd = strtok(linebuf, " ");
		if(strcmp(cmd, "OT")) {
			puts(linebuf);
			return;
		}
		else if(strcmp(cmd, "FROM")) {
			puts(linebuf);
			// reply MORF
		}
		else 
			err_quit("received garbage, expected OT or FROM\n");
	}
}

void handlefrom(int sockfd) {
	char *user = strtok(NULL, " ");
	char *msg = strtok(NULL, " ");
	strcpy(sendbuf, "MORF "); // reply MORF
	strcat(sendbuf, user);
	strcat(sendbuf, ENDLINE);
	write(sockfd, sendbuf, strlen(sendbuf));
	puts(msg); // print msg
}

/*void replyloop(int sockfd, char *cmd) {
	int n = 0;
	while(1) {
		write(sockfd, cmd, strlen(cmd)); // send cmd to server
		n = read(sockfd, recvbuf, MAXLINE); // read reply from server
		recvbuf[n] = 0;
		char *reply = strtok(recvbuf, " ");
		if(strcmp(reply, replymap(cmd)) == 0) { // if received expected reply
			recvbuf[strlen(reply)] = ' ';
			puts(recvbuf);
			return;
		}
		else if(strcmp(reply, "FROM") == 0) { // if received message while waiting for reply
			recvbuf[strlen(reply)] = ' ';
			puts(recvbuf);
		}
		else {
			puts("Garbage, unexpected reply from server %s\n", reply);
		}
	}
}*/

