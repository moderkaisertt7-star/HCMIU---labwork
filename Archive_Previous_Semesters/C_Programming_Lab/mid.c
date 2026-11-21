#include <stdio.h>
#include <stdlib.h>
#include <time.h>
int sumArray(int a[], int n){
    int sum = 0;
    for (int z = 0; z<n;z++){
        sum += a[z];
    }
return sum;
}
int main() {
    int score[5] = {0};
    printf("Enter 5 scores: ");
    for (int i = 0; i<5; i++){
        scanf("%d",&score[i]);
    }
int total = sumArray(score,5);
printf("Total score: %d",total);
int average = total/5;
printf("\nAverage score: %d",average);
return 0;
    
}