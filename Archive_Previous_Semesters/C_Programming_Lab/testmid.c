#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main() {
srand(time(NULL));
int passed = 0, a[10] = {0};
printf("Scores: ");
for (int i = 0; i < 10; i++){
    int scores = rand() %11;
printf("%4d",a[i]+scores);
if (scores >= 5){
    passed ++;
    }
};
printf("\nPassed: %d of 10 students",passed);
return 0;
}
