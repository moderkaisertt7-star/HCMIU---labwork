#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main() {
    srand(time(NULL));
    int roll, count = 0;
    while (roll !=6){
    roll =1+ rand() % 6;
        count ++;
        printf("Roll %d: %d\n", count, roll);
    }
    printf("\nYou got a 6 after %d rolls",count);
return 0;
}