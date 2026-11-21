#include <stdio.h>

void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

int main(void) {
    int n1, n2;
    printf("Enter n1: ");
    if (scanf("%d", &n1) != 1) return 1;
    printf("Enter n2: ");
    if (scanf("%d", &n2) != 1) return 1;

    swap(&n1, &n2);
    printf("After swap: n1 = %d, n2 = %d\n", n1, n2);

    return 0;
}
