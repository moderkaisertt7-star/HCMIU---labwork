#include <stdio.h>

void func1(void)
{
    float a, b, c, minimum;
    printf("Enter a, b, c: ");
    if (scanf("%f %f %f", &a, &b, &c) != 3)
        return;

    minimum = a;
    if (b < minimum) minimum = b;
    if (c < minimum) minimum = c;
    printf("%g\n", (double)minimum);
}

void func2(void)
{
    int n;
    char c;

    printf("Enter n and c: ");
    if (scanf("%d %c", &n, &c) != 2)
        return;

    for (int row = 0; row < n; ++row) {
        for (int col = 0; col < n; ++col)
            putchar(c);
        putchar('\n');
    }
}

void func3(void)
{
    int i;
    float f;
    double d;
    printf("Enter i, f, d: ");
    if (scanf("%d %f %lf", &i, &f, &d) != 3)
        return;

    printf("%g\n", ((double)i + (double)f + d) / 3.0);
}

int main(void)
{
    int option = 0;
    while (1) {
printf("Select an option:\n");
scanf("%d", &option);
    if (option == 1) {
        func1();
    } else if (option == 2) {
        func2();
    } else if (option == 3) {
        func3();
    } else {
        printf("Invalid option\n");
        break;
    }
    
}
    return 0;
}