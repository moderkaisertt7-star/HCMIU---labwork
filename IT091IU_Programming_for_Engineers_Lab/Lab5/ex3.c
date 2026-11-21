#include <stdio.h>

void convert(int total, int *h, int *m, int *s) {
    *h = total / 3600;
    *m = (total % 3600) / 60;
    *s = total % 60;
}

int main(void) {
    int total;
    int h, m, s;

    printf("Enter time in seconds: ");
    if (scanf("%d", &total) != 1) return 1;

    convert(total, &h, &m, &s);
    printf("%d hr %d min %d s\n", h, m, s);

    return 0;
}
