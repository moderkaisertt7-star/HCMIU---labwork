#include <stdio.h>

void decompose(double x, int *intPart, double *fracPart) {
    *intPart = (int)x;
    *fracPart = x - (double)(*intPart);
}

int main(void) {
    double x;
    int intPart;
    double fracPart;

    printf("Enter a number: ");
    if (scanf("%lf", &x) != 1) return 1;

    decompose(x, &intPart, &fracPart);

    printf("Original: %g\n", x);
    printf("Integer part: %d\n", intPart);
    printf("Fractional part: %.6f\n", fracPart);

    return 0;
}
