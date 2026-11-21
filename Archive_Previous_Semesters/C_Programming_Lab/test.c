#include <stdio.h>
int main(){
    int a[5],count=0;
    printf("Enter 5 integers: ");
scanf("%d %d %d %d %d",&a[0],&a[1],&a[2],&a[3],&a[4]);

    for (int i=0;i<5;i++){
        if (a[i]<0){
            count = count + 1;
        }
    }
    printf("Number of negative integers: %d\n", count);
    return 0;
}