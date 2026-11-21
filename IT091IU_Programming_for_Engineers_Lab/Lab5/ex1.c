#include <stdio.h>

int main(void) {
    int num = 10;
    int *ptr = &num;

    printf("Address of num: %p\n", (void *)ptr);
    printf("Value using pointer: %d\n", *ptr);

    *ptr = 20;
    printf("New value of num: %d\n", num);

    return 0;
}
