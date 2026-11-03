#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>
#define CAP 3
#define N 12
static int queue[CAP],in=0,out=0,count=0,produced=0,consumed=0;
static sem_t empty,full;
static pthread_mutex_t mutex=PTHREAD_MUTEX_INITIALIZER;
void *producer(void *p){(void)p;
    for(int i=1;i<=N;i++){
        sem_wait(&empty);
        pthread_mutex_lock(&mutex);
        queue[in]=i;in=(in+1)%CAP;count++;produced++;
        printf("[SENSOR THREAD] Received reading #%02d -> placed in shared queue (%d/%d slots used).\n",i,count,CAP);
        pthread_mutex_unlock(&mutex);
        sem_post(&full);
    }return NULL;
}
void *consumer(void *p){(void)p;
    for(int i=1;i<=N;i++){
        sem_wait(&full);
        pthread_mutex_lock(&mutex);
        int id=queue[out];out=(out+1)%CAP;count--;consumed++;
        printf("[ANALYTICS THREAD] Took reading #%02d for processing -> %d/%d slots remain occupied.\n",id,count,CAP);
        pthread_mutex_unlock(&mutex);
        sem_post(&empty);
    }return NULL;
}
int main(void){pthread_t a,b;
    setvbuf(stdout,NULL,_IONBF,0);
    puts("[SHARED QUEUE] A sensor thread generates 12 example readings.");
    puts("[SHARED QUEUE] An analytics thread consumes them from a 3-slot buffer.");
    puts("[PROTECTION] Semaphores block writes when full and reads when empty.");
    puts("[PROTECTION] A mutex keeps the queue indexes and count consistent.");
    if(sem_init(&empty,0,CAP)||sem_init(&full,0,0)){perror("sem_init");return 1;}
    if(pthread_create(&a,NULL,producer,NULL)||pthread_create(&b,NULL,consumer,NULL)){perror("pthread_create");return 1;}
    pthread_join(a,NULL);pthread_join(b,NULL);
    sem_destroy(&empty);sem_destroy(&full);pthread_mutex_destroy(&mutex);
    printf("[SUMMARY] Received %d, processed %d, still in buffer %d.\n",produced,consumed,count);
    if(produced==N&&consumed==N&&count==0)puts("[SUCCESS] Every reading processed exactly once; no queue entries left behind.");
    else puts("[ERROR] Sensor packet accounting mismatch.");
    return !(produced==N&&consumed==N&&count==0);
}
