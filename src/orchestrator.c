#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <string.h>

int main(int argc, char **argv) {
    setvbuf(stdout,NULL,_IONBF,0);
    const char *input = argc > 1 ? argv[1] : "data/sensor_readings.csv";
    printf("[WORKFLOW] Parent process PID %ld is coordinating three independent tasks.\n",(long)getpid());
    printf("[FILE CHECK] Opening sensor file: %s\n",input);
    int fd=open(input,O_RDONLY);
    if(fd<0){perror("[FILE ERROR] Cannot open input");return 1;}
    char buf[128];ssize_t n=read(fd,buf,sizeof(buf));close(fd);
    if(n<=0){fprintf(stderr,"[FILE ERROR] Input empty/unreadable\n");return 1;}
    printf("[FILE CHECK] Successfully read %ld bytes with read(); closed input descriptor.\n",(long)n);
    int logfd=open("logs/orchestrator.log",O_WRONLY|O_CREAT|O_APPEND,0644);
    if(logfd<0){perror("[FILE ERROR] Cannot open log");return 1;}
    const char *stages[]={"acquire","predict","report"};
    const char *desc[]={"Validate raw sensor readings", "Train demo ML model and estimate water needs", "Write plot-wise irrigation recommendations"};
    for(int i=0;i<3;i++){
        printf("\n[WORKFLOW %d/3] %s\n",i+1,desc[i]);
        char line[200];int len=snprintf(line,sizeof(line),"stage %s start, parent PID %ld\n",stages[i],(long)getpid());
        if(write(logfd,line,(size_t)len)!=len){perror("write log");close(logfd);return 1;}
        pid_t pid=fork();
        if(pid<0){perror("fork");close(logfd);return 1;}
        if(pid==0){
            printf("[CHILD PID %ld] Starting Python %s task using exec()...\n",(long)getpid(),stages[i]);
            if(i==0)execlp("python3","python3","-u","src/irrigation.py",stages[i],"--input",input,(char*)NULL);
            else execlp("python3","python3","-u","src/irrigation.py",stages[i],(char*)NULL);
            perror("exec python3");_exit(127);
        }
        printf("[PARENT] Created child PID %ld. Waiting for it to finish before proceeding.\n",(long)pid);
        int status;
        if(waitpid(pid,&status,0)<0){perror("waitpid");close(logfd);return 1;}
        len=snprintf(line,sizeof(line),"stage %s child PID %ld status %d\n",stages[i],(long)pid,WIFEXITED(status)?WEXITSTATUS(status):-1);
        if(write(logfd,line,(size_t)len)!=len){perror("write log");close(logfd);return 1;}
        if(!WIFEXITED(status)||WEXITSTATUS(status)!=0){fprintf(stderr,"[FAILED] %s task exited with an error. Stopping workflow.\n",stages[i]);close(logfd);return 2;}
        printf("[PARENT] %s task completed successfully. Child reaped by waitpid().\n",stages[i]);
    }
    close(logfd);puts("\n[WORKFLOW COMPLETE] Validated data -> model predictions -> irrigation report.");return 0;
}
