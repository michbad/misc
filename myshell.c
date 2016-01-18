// Michal Badura, pair-programmed with Daniel Rubenstein
// Implementation of a Unix-style shell with redirection
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <ctype.h>


char error_message[30] = "An error has occurred\n";

int isEmpty(char* str) {
  while (*str!='\0') {
    if (!isspace(*str)) {
      return 0;
    }
    str++;
  }
  return 1; 
}

typedef struct command_input {
  char input[514];
  struct command_input *next; 
} command_input, *command;

command create_command_input(char *token); 
command create_command_input(char *token){

  command result = (command) malloc(sizeof(command_input)); 

  strncpy(result->input, token, 514); 
  result-> next = NULL; 

  return result; 
}

void func_exit(int argc, char **args) {
  if (argc!=1) {
    write(STDOUT_FILENO, error_message, strlen(error_message));
    return;
  }
  exit(0);
}

void func_cd(int argc, char **args) {
  if (argc==1) {
    const char *dir = getenv("HOME");
    int ret = chdir(dir);
    if (ret == -1) {
      write(STDOUT_FILENO, error_message, strlen(error_message));      
    }
    return;
  }
  if (argc!=2) {
    write(STDOUT_FILENO, error_message, strlen(error_message));
    return;
  }
  int ret = chdir(args[1]);
  if (ret == -1) {
    write(STDOUT_FILENO, error_message, strlen(error_message));
    return;
  }
} 

void func_pwd(int argc, char **args) {
  if (argc!=1) {
    write(STDOUT_FILENO, error_message, strlen(error_message));
    return;
  }
  char pPath[512];
  getcwd(pPath, 512);
  write(STDOUT_FILENO, (char*)pPath, strlen(pPath));
  write(STDOUT_FILENO, "\n", 1);
}

void func_other(int argc, char **argv) {
  int pid = fork();
  if (pid==0) {
    int ret =execvp(argv[0], argv);
    if (ret==-1) {
      write(STDOUT_FILENO, error_message, strlen(error_message));
    }
    exit(0); 
  }
  else {
    wait(0);
  }
  return;
}


void executeCommand(char* cmd) {
    char copycmd[512];
    strcpy(copycmd,cmd);

    if (copycmd[strlen(copycmd)-1] == '>') {
      write(STDOUT_FILENO, error_message, strlen(error_message));
      return;
    }

    if (copycmd[0] == '>') {
      write(STDOUT_FILENO, error_message, strlen(error_message));
      return;
    }


    // here we need to split by >, assume this is already done
    char *tokptr;
    char *first = strtok_r(copycmd,">", &tokptr); 
    char *second = strtok_r(NULL,">",&tokptr);
    char *third = strtok_r(NULL, ">", &tokptr);
    int saved_stdin = dup(STDOUT_FILENO);
    int redirected = 0;
    
    // printf("%s\n", first);
    if (third!=NULL) {
      write(STDOUT_FILENO, error_message, strlen(error_message));
      return;
    }
    
    if (second!=NULL) {
      redirected = 1;
      if (isEmpty(second) || isEmpty(first)) {
        write(STDOUT_FILENO, error_message, strlen(error_message));
        return;
      }
      char *redir_path = strtok_r(second, " \t", &tokptr);
      
      char *fifth = strtok_r(NULL, " \t", &tokptr);
      if (fifth!=NULL) {
        write(STDOUT_FILENO, error_message, strlen(error_message));
        return;
      }
      
      int fd = open(redir_path, O_WRONLY | O_CREAT | O_EXCL, S_IRUSR|S_IWUSR);
      if (fd==-1) {
        write(STDOUT_FILENO, error_message, strlen(error_message));
        return;
      }
      int ret = dup2(fd, STDOUT_FILENO);
      // int ret = dup2(STDOUT_FILENO, fd);
      if (ret==-1) {
        write(STDOUT_FILENO, error_message, strlen(error_message));
        return;
      }

      close(fd);
    }


    char *name;
    char *args[512]; //stupid allocation, but should work
    char *word = strtok(first, " \t");
    

    args[0] = word;
    int i=1;
    while(word != NULL) {
      word = strtok(NULL, " \t");
      args[i] = word;
      i++;
    }
    int argc = i-1;

    name = args[0];
    if (name==NULL) {
      return;
    }

    if (!strcmp(name, "cd")) {
      // printf("%d\n", redirected);
      if (redirected) {
        write(STDOUT_FILENO, error_message, strlen(error_message));
        return;
      }
      func_cd(argc, args);
    }
    else if (!strcmp(name, "pwd")) {
      func_pwd(argc, args);
    }
    else if (!strcmp(name, "exit")) {
      if (redirected) {
        write(STDOUT_FILENO, error_message, strlen(error_message));
        return;
      }
      func_exit(argc, args);
    }
    else {
      func_other(argc, args);
    }

    if(second!=NULL) {
      // close(STDOUT_FILENO);
      dup2(saved_stdin,STDOUT_FILENO);
      close(saved_stdin);
    }
}

void divideIntoCommands(char *msg)
{

  char* new = (char *) malloc(514); 
  // struct command_input *test;
  // struct command_input *test2;   
  char *tokptr;
  new = strtok_r (msg, ";", &tokptr);   
  while(new != NULL)  {
    char line[512];
    strcpy(line, new);
    executeCommand(line);    
    new = strtok_r(NULL, ";", &tokptr);
   }
   return;
}




int main(int argc, char *argv[]) 
{
    char cmd_buff[514];
    char *pinput;

    if(argc == 1){
      while (1) {
        write(STDOUT_FILENO, "myshell> ", strlen("myshell> "));
        
        pinput = fgets(cmd_buff, 514, stdin);                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
        if(strlen(pinput)==513 && pinput[512]!='\n') {
          pinput = fgets(cmd_buff, 514, stdin);
          write(STDOUT_FILENO, error_message, strlen(error_message));
          // write(STDOUT_FILENO, "\n", 1);
          continue; 
        }

        pinput = strtok(pinput, "\n");
        //need checking for length
        if (!pinput || isEmpty(pinput)) {
            continue;
        }
        
        divideIntoCommands(cmd_buff);
      }
    }
    //char str[512]; 
    if (argc ==2){
      FILE *fp; 
      char * line = NULL; 
      size_t len = 0; 
      ssize_t read; 

      fp = fopen(argv[1],"r"); 

      if (fp == NULL){
        write(STDOUT_FILENO, error_message, strlen(error_message));
        return 0; 
      }
      while ((read = getline (&line, &len, fp))!= -1)
      {
        if (isEmpty(line)) {
          continue;
        }
        if (read > 512){
          write(STDOUT_FILENO, line, strlen(line));
          write(STDOUT_FILENO, error_message, strlen(error_message));
        }
        
        else if (read > 1){
          write(STDOUT_FILENO, line, strlen(line));
          line = strtok(line,"\n");  
          divideIntoCommands(line); 
        }
      }
    }
    else {
      write(STDOUT_FILENO, error_message, strlen(error_message));
    }
    return 0;  
}
