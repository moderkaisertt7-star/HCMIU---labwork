#include <stdio.h>

float minVal(float a[], int n) {
    float min = a[0];
    for (int i = 1; i < n; i++) {
        if (a[i] < min)
            min = a[i];
    }
    return min;
}

float maxVal(float a[], int n) {
    float max = a[0];
    for (int i = 1; i < n; i++) {
        if (a[i] > max)
            max = a[i];
    }
    return max;
}

float average(float a[], int n) {
    float sum = 0;
    for (int i = 0; i < n; i++)
        sum += a[i];
    return sum / n;
}

void printForward(float a[], int n) {
    for (int i = 0; i < n; i++) {
        if (i > 0)
            printf(" ");
        printf("%.1f", a[i]);
    }
    printf("\n");
}

void printBackward(float a[], int n) {
    for (int i = n - 1; i >= 0; i--) {
        if (i < n - 1)
            printf(" ");
        printf("%.1f", a[i]);
    }
    printf("\n");
}

int main() {
    float a[100];
    int n;

    printf("Array size: ");
    scanf("%d", &n);

    for (int i = 0; i < n; i++) {
        printf("Element [%d]: ", i);
        scanf("%f", &a[i]);
    }

    printf("Min: %.2f   Max: %.2f   Average: %.2f\n",
           minVal(a, n), maxVal(a, n), average(a, n));

    printf("Forward: ");
    printForward(a, n);

    printf("Backward: ");
    printBackward(a, n);

    return 0;
}
