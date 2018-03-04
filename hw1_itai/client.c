#include "incl.h"
#include "client.h"

char linebuf[MAXLINE+1], sendbuf[MAXLINE+1], recvbuf[MAXLINE+1];
chat* chatlist = NULL;
char *username;
int sockfd;

int main(int argc, char** argv) {
	int client2chat[2], chat2client[2]; // pipes
	pipe(client2chat);
	pipe(chat2client);

	if(argc != ARGC)
		Err_quit("usage: client <Name> <IPaddress> <port>\n");

	if(strlen(argv[NAME_ARG]) > MAXNAME)
		Err_quit("username too long\n");
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

		/*STDIN PART*/
	    if(FD_ISSET(fileno(stdin), &rfds)) { 
			puts("FD_ISSET(stdin)");
		    if((readcount = read(fileno(stdin), linebuf, MAXLINE)) == 0) // read from stdin
			    Err_quit("EOF\n"); 
		    linebuf[readcount] = 0; // null-terminate
		    cmd* command = parse_cmsg(linebuf);
			switch(command->cmdt) {
				case HELP:
					printhelp();
					break;
				case LOG: 
					Logout(sockfd, username);
					break;
				case LIST:
					printf("calling sendlist\n");
					sendlist(sockfd);
					break;
				case CHAT:
					pipe(client2chat);
					pipe(chat2client);
					pid_t pid = fork();
					if(pid == 0) { // child
						strtok(linebuf, " ");
						strtok(NULL, " ");
						char *msg = strtok(NULL, " ");
						CreateChatWindow(client2chat, chat2client, command->to, msg);
					}
					else { // parent
						chat* t = malloc(sizeof(chat));
						t->name = command->to;
						t->readfd = chat2client[READ];
						t->writefd = client2chat[WRITE];
						t->next = chatlist;
						t->pid = pid;
						chatlist = t;
						FD_SET(chat2client[READ], &rfds_init);
						maxfd = max(maxfd,chat2client[READ]);
						char* to_send = makeTo(command->to, command->msg); //create TO <name> <msg>
						memset(linebuf,0,MAXLINE);
						strcpy(linebuf,to_send);
						write(sockfd, linebuf, strlen(linebuf));
						if(blockuntil(sockfd, "OT") == -1){ //IF USER DOESN'T EXIST ON STARTUP
							kill(pid,SIGKILL);
							chatlist = removeChat(chatlist,t);
						}
					}
					break;
				default:
					Err_quit("Invalid cmdt\n");
			}
	    } //end of STDIN if

	    /*SERVER PART */
	    if(FD_ISSET(sockfd, &rfds)) { 
			puts("FD_ISSET(sockfd)");
			memset(linebuf,0,sizeof(linebuf));
		    if((readcount = read(sockfd, linebuf, MAXLINE)) == 0) // read from server
			    Err_quit("EOF\n"); 
		    linebuf[readcount] = 0; // null-terminate
			puts(linebuf);
			//char *cmd = strtok(linebuf, " ");
			//puts(cmd);
			//replyloop(cmd);
			/*if(strcmp(cmd, "FROM") == 0) { // handle FROM
				handlefrom(sockfd);
			}*/
			//else
			//	Err_quit("Garbage, wasn't expecting %s\n", cmd);
		    //check for what it returns
		    server_cmd* command = parse_server_msg(linebuf, (Server_cmd_type)NULL);
		    //Switch based on command type
		    switch(command->cmdt){
				/*case OT:
					puts("read OT");
					break;*/
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
		    	case UOFF:;
			    	char *ptr = strstr(command->msg,ENDLINE);
			    	*ptr = 0;
		    		printf("%s has logged off!",command->msg);
		    		break;
		    	case FROM:;
		    		char* name = command->to;
		    		char* msg = command->msg;
		    		chat* curr_chat = chatlist;
		    		int hasChat = 0;
		    		while(curr_chat){
		    			if(strcmp(curr_chat->name,name) == 0){
		    				hasChat = 1;
		    				write(curr_chat->writefd, msg, strlen(msg));
		    				break;
		    			}
		    			curr_chat = curr_chat->next;
		    		}
		    		if(hasChat == 0){
		    			pipe(client2chat);
						pipe(chat2client);
						pid_t pid = fork();
						if(pid == 0) { // child
							CreateChatWindow(client2chat, chat2client, name, ""); 
						}
						else{ //parent
							chat* t = malloc(sizeof(chat));
							t->name = command->to;
							t->readfd = chat2client[READ];
							t->writefd = client2chat[WRITE];
							t->next = chatlist;
							t->pid = pid;
							chatlist = t;
							FD_SET(chat2client[READ], &rfds_init);
							maxfd = max(maxfd,chat2client[READ]);
							write(client2chat[WRITE], msg, strlen(msg));
						}
		    		}
		    		sendmrof(sockfd,name);
		    		break;
		    	default:
		    		puts("Invalid server command. Quitting");
		    		Exit(0);
		    		break;
		    }
		    //write(client2chat[WRITE], linebuf, strlen(linebuf)); // write to chat window
	    }	

	    /*CHAT PART*/
	    chat* curr_chat = chatlist;
	    while(curr_chat){
	    	if(FD_ISSET(curr_chat->readfd, &rfds)) {
				puts("FD_ISSET(curr_chat->readfd)");
			    if((readcount = read(curr_chat->readfd, linebuf, MAXLINE)) == 0) // read from chat window
				    Err_quit("EOF\n");
			    linebuf[readcount] = 0; // null-terminate
			    cmd* command = (cmd*)malloc(sizeof(cmd)); //utilize to and msg of command for makeTo() function
			    char *to = curr_chat->name;
			    char *msg = linebuf;
			    char* to_send = makeTo(to, msg);
			    strcpy(linebuf,to_send);
			    write(sockfd, linebuf, strlen(linebuf)); // write to server 
				blockuntil(sockfd, "OT"); // problem
				//curr_chat->waiting = true;
			    free(command);
	   		}
	   		curr_chat = curr_chat->next;
	   	}
	}
}

chat* removeChat(chat* chats, chat* remChat){
	chat* curr_chat = chats;
	chat* prev_chat = NULL;
	while(curr_chat){
		if(curr_chat == remChat){
			if(prev_chat){
				prev_chat->next = curr_chat->next;
				return chats;
			}
			else{
				return curr_chat->next;
			}
		}
	}
}

void CreateChatWindow(int client2chat[2], int chat2client[2], char *to_name, char *msg) {
	char *args[11];
	args[0] = "xterm";
	args[1] = "-xrm";
	args[2] = "XTerm.vt100.allowTitleOps: false";
	args[3] = "-T";
	char *title = calloc(strlen("FROM ") + strlen(username) + strlen(" TO ") + strlen(to_name) + 1, sizeof(char));
	strcpy(title, "FROM ");
	strcat(title, username);
	strcat(title, " TO ");
	strcat(title, to_name);
	printf("Creating chat window %s\n", title);
	args[4] = title;
	args[5] = "-e";
	args[6] = "./chat";
	args[7] = calloc(FD_SZ_CHAR+1, sizeof(char));
	args[8] = calloc(FD_SZ_CHAR+1, sizeof(char));
	args[9] = calloc(strlen(msg)+1, sizeof(char));
	strcpy(args[9], msg);
	args[10] = NULL;
	snprintf(args[7], FD_SZ_CHAR, "%d", client2chat[READ]); 
	snprintf(args[8], FD_SZ_CHAR, "%d", chat2client[WRITE]);
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
		Err_quit("inet_pton error for %s\n", argv[IP_ARG]);

	if(connect(sockfd, (struct sockaddr*)&servaddr, sizeof(servaddr)) < 0)
		Err_quit("connect error\n");
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
		Err_quit("username taken\n");
	if(strcmp(linebuf, _MAI) != 0)
		Err_quit("read garbage, expected MAI\n");
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
			Err_quit("Read garbage while reading until %s\n", str);
		}
	}
}
void readuntilend(int sockfd, char *buf) {
	int n = strlen(buf);
	memset(&buf[n], 0, MAXLINE-n);
	while(strcmp(&buf[n-strlen(ENDLINE)], ENDLINE) != 0) { // while buffer does not end in ENDLINE
		n += read(sockfd, &buf[n], MAXLINE-strlen(buf)); // TODO: check bounds
		buf[n] = 0;
	}
}

void sendmrof(int sockfd, char* name){
	memset(linebuf, 0, strlen(_MORF)+strlen(name)+strlen(ENDLINE)+1);
	strcpy(linebuf, _MORF);
	strcat(linebuf, name);
	strcat(linebuf, ENDLINE);
	write(sockfd, linebuf, strlen(linebuf));
	memset(linebuf, 0, strlen(linebuf));
}

void sendDNE(int sockfd, char* name){
	memset(linebuf, 0, strlen(_EDNE)+strlen(name)+strlen(ENDLINE)+1);
	strcpy(linebuf, _EDNE);
	strcat(linebuf, name);
	strcat(linebuf, ENDLINE);
	write(sockfd, linebuf, strlen(linebuf));
	memset(linebuf, 0, strlen(linebuf));

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
	readuntilend(sockfd, linebuf);
	fputs(&linebuf[strlen(_MOTD)], stdout);
}

void printhelp() {
	printf("/help\n/chat <to> <msg>\n/listu\tlist users\n/logout\n");
}

typedef struct chat chat;

char* makeTo(char *to, char *msg){
	char* string = malloc((strlen(to)+strlen(msg))*sizeof(char) + 16);
	memset(string,0,sizeof(string));
	strcat(string,"TO ");
	strcat(string,to);
	strcat(string," ");
	strcat(string,msg);
	strcat(string,ENDLINE);
	return string;

}

/* For reference:
typedef enum server_cmd_type{U2EM, ETAKEN, MAI, MOTD, UTSIL, FROM, OT, EDNE, EYB, UOFF} Server_cmd_type;
typedef struct {
    enum server_cmd_type cmdt;
    char* to; //NULL when not FROM or EDNE or UOFF or OT
    char* msg; //NULL when not FROM or MOTD
    char** users; //NULL when not UTSIL
} server_cmd;
 */
server_cmd* parse_server_msg(char* in, Server_cmd_type in_type) { // TODO: can we remove 2nd arg?
	server_cmd* curr_cmd = (server_cmd*)malloc(sizeof(server_cmd));
	char* curr_token = (char*)malloc(strlen(in)+1);
	int pos = 0;
	char* currChar = in;
	curr_cmd->to = NULL;
	curr_cmd->msg = NULL;
	curr_cmd->users = NULL;
	curr_cmd->cmdt = in_type;
	while(*currChar != '\0') {
		memset(curr_token, 0, strlen(in)+1); // clear curr_token
		while(*currChar == ' ') { // go until no more spaces
			currChar++;
		}
		if(*currChar == '\0') { // if end of line
			break;
		}
		if(curr_cmd->cmdt == UTSIL || curr_cmd->cmdt == UOFF) {
			char* string = strdup(currChar);
			curr_cmd->msg = string;
			return curr_cmd;
		}
		if(pos == 2 || curr_cmd->cmdt == MOTD) { // if reached 3rd section, it's just one remaining token.
			curr_cmd->msg = strdup(currChar);
			free(curr_token);
			return curr_cmd;
		}
		while(*currChar != ' ' && *currChar != '\n' && *currChar != '\0') { // create token
			strncat(curr_token,currChar,1);	
			currChar++;
		}
		switch(pos) { // Depending on position, parse differently.
			case 0: // set cmdt
				if(strcmp(curr_token,"FROM") == 0) {
				 	curr_cmd->cmdt = FROM;
				 	pos = 1;
				}
				else if(strcmp(curr_token,"U2EM") == 0) {
				 	curr_cmd->cmdt = U2EM;
				 	return curr_cmd;
				}
				else if(strcmp(curr_token,"ETAKEN") == 0) {
				 	curr_cmd->cmdt = ETAKEN;
				 	return curr_cmd;
				}
				else if(strcmp(curr_token,"MAI") == 0) {
				 	curr_cmd->cmdt = MAI;
				 	return curr_cmd;
				}
				else if(strcmp(curr_token,"MOTD") == 0) {
				 	curr_cmd->cmdt = MOTD;
				}
				else if(strcmp(curr_token,"UTSIL") == 0) {
				 	curr_cmd->cmdt = UTSIL;
				}
				else if(strcmp(curr_token,"OT") == 0) {
				 	curr_cmd->cmdt = OT;
				}
				else if(strcmp(curr_token,"EDNE") == 0) {
				 	curr_cmd->cmdt = EDNE;
				}
				else if(strcmp(curr_token,"EYB") == 0) {
				 	curr_cmd->cmdt = EYB;
				}
				else if(strcmp(curr_token,"UOFF") == 0) {
				 	curr_cmd->cmdt = UOFF;
				}
				break;
			case 1:
				//FROM 
				curr_cmd->to = strdup(curr_token);
				pos=2;
				break;
			case 2: //MSG FOR FROM
				curr_cmd->msg = strdup(currChar);
				return curr_cmd;
				break;
			default:
				return NULL;
				break;
		}
		//pos++;
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

/* For reference:
typedef struct {
	enum cmd_type cmdt;
	char* to; //NULL when anything but CHAT
	char* msg; //NULL when anything but CHAT
} cmd;
*/
cmd* parse_cmsg(char* in){
	cmd* curr_cmd = (cmd*)malloc(sizeof(cmd));
	char* in_msg = (char*)malloc((strlen(in)+1)); 
	//memset(in_msg, 0, sizeof(char)); // wut
	int pos = 0;
	char* currChar = in; // cursor
	while(*currChar != '\0') {
		memset(in_msg, 0, strlen(in)+1); // clear in_msg
		while(*currChar == ' ') // go until no more spaces
			currChar++;
		if(*currChar == '\0')
			break;
		if(pos == 2){
			curr_cmd->msg = strdup(currChar);
			free(in_msg);
			return curr_cmd;
		}
		while(*currChar != ' ' && *currChar != '\n' && *currChar != '\0'){ // go until whitespace or null
			strncat(in_msg,currChar,1);	// fill in_msg
			currChar++;
		}
		switch(pos){
			case 0: // set cmdt
				curr_cmd->to = NULL; 
				curr_cmd->msg = NULL;
				 if(strcmp(in_msg,"/help") == 0){
				 	curr_cmd->cmdt = HELP;
				 }
				 else if(strcmp(in_msg,"/logout") == 0){
				 	curr_cmd->cmdt = LOG;
				 }
				 else if(strcmp(in_msg,"/listu") == 0){
				 	curr_cmd->cmdt = LIST;
				 }
				 else if(strcmp(in_msg, "/chat") == 0){
				 	curr_cmd->cmdt = CHAT;
				 }
				 else
				 	curr_cmd->cmdt = ERR;
				 if(curr_cmd->cmdt != CHAT){ // only chat requires to and msg
				 	free(in_msg); // nice
				 	return curr_cmd;
				 }
				 pos++;
				break;
			case 1: // set to
				curr_cmd->to = strdup(in_msg);
				pos++;
				break;
			case 2: // set msg // TODO: this code is unreachable??
				curr_cmd->msg = strdup(in_msg); // TODO: this is incorrect for msg with spaces
				break;
			default:
				return NULL;
				break;
		}

		// memset(in_msg, 0, sizeof(char)); // wut
	}
	free(in_msg); // code is unreachable (or should be)
	Err_quit("Error: unexpected execution flow in parse_cmsg\n");
	return NULL;
}

void killchats() {
	chat* curr_chat = chatlist;
	while(curr_chat){
		kill(curr_chat->pid,SIGKILL);
		close(curr_chat->readfd);
		close(curr_chat->writefd);
		curr_chat = curr_chat->next;
	}
}
void Logout(int sockfd, char *username) {
	puts("goodbye");
	strcpy(linebuf, _BYE);
	write(sockfd, linebuf, strlen(linebuf));
	killchats();	
	shutdown(sockfd, SHUT_RDWR);
	close(sockfd);
	//send close to server
	Exit(0);
}

//send request for users to server
void sendlist(int sockfd) {
	printf("in sendlist\n");
	strcpy(sendbuf, _LISTU);
	sendbuf[strlen(_LISTU)] = 0;
	printf("sending %s\n", sendbuf);
	write(sockfd, sendbuf, strlen(sendbuf));
	//blockuntil(sockfd, "UTSIL");
}

int blockuntil(int sockfd, char *reply) {
	//TODO: Fix this. Doesn't work as intended.
	while(1) {
		int n = read(sockfd, recvbuf, MAXLINE);
		recvbuf[n] = 0;
		char *cmd = strtok(recvbuf, " ");
		if(strcmp(cmd, reply) == 0) { // if got expected reply
//			puts(&recvbuf[strlen(cmd)+1]);
			readuntilend(sockfd, &recvbuf[strlen(cmd)+1]);
			puts(&recvbuf[strlen(cmd)+1]);
			return 0;
		}
		else if(strcmp(cmd, "FROM") == 0) {
			puts(recvbuf);
			// TODO: reply MORF
		}
		else if(strcmp(cmd, "EDNE")==0){
			char *name = strtok(linebuf, " ");
			printf("User %s does not exist.",name);
			return -1;
		}
		else 
			Err_quit("received garbage, expected TO or FROM\n");
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

void replyloop(int sockfd, char *comd) {
	int n = 0;
	write(sockfd, comd, strlen(comd)); // send cmd to server
	while(1) {
		n = read(sockfd, recvbuf, MAXLINE); // read reply from server
		recvbuf[n] = 0;
		char *reply = strtok(recvbuf, " ");
		if(strcmp(reply, strrev(comd)) == 0) { // if received expected reply
			recvbuf[strlen(reply)] = ' ';
			puts(recvbuf);
			return;
		}
		else if(strcmp(reply, "FROM") == 0) { // if received message while waiting for reply
			recvbuf[strlen(reply)] = ' ';
			puts(recvbuf);
		}
		else {
			Err_quit("Garbage, unexpected reply from server %s\n", reply);
		}
	}
}


char *strrev(char *str)
{
    int i = strlen(str) - 1, j = 0;

    char ch;
    while (i > j)
    {
        ch = str[i];
        str[i] = str[j];
        str[j] = ch;
        i--;
        j++;
    }
    return str;
}
void Err_sys(const char* fmt, ...) {
	killchats();
	printf("shutting down sockfd\n");
	shutdown(sockfd, SHUT_RDWR);
	close(sockfd);
	err_sys(fmt);
}
void Err_quit(const char* fmt, ...) {
	killchats();
	printf("shutting down sockfd\n");
	shutdown(sockfd, SHUT_RDWR);
	close(sockfd);
	err_quit(fmt);
}
void Exit(int x) {
	killchats();
	printf("shutting down sockfd\n");
	shutdown(sockfd, SHUT_RDWR);
	close(sockfd);
	exit(x);
}
