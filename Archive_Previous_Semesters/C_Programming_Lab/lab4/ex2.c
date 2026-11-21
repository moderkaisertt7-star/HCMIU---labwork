#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void sortAscending(int a[], int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - 1 - i; j++) {
            if (a[j] > a[j + 1]) {
                int temp = a[j];
                a[j] = a[j + 1];
                a[j + 1] = temp;
            }
        }
    }
}

void sortDescending(int a[], int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - 1 - i; j++) {
            if (a[j] < a[j + 1]) {
                int temp = a[j];
                a[j] = a[j + 1];
                a[j + 1] = temp;
            }
        }
    }
}

int countOccurrence(int a[], int n, int x) {
    int count = 0;
    for (int i = 0; i < n; i++) {
        if (a[i] == x)
            count++;
    }
    return count;
}

void printArray(int a[], int n) {
    for (int i = 0; i < n; i++) {
        if (i > 0)
            printf(" ");
        printf("%d", a[i]);
    }
    printf("\n");
}

int main() {
    srand(time(NULL));

    int a[100], b[100], c[100];
    int n, x;

    printf("Enter size of array: ");
    scanf("%d", &n);

    printf("Enter x: ");
    scanf("%d", &x);

    for (int i = 0; i < n; i++) {
        a[i] = rand() % 11;
        b[i] = a[i];
        c[i] = a[i];
    }

    printf("Original array: ");
    printArray(a, n);

    sortAscending(b, n);
    printf("Ascending:  ");
    printArray(b, n);

    sortDescending(c, n);
    printf("Descending: ");
    printArray(c, n);

    printf("x occurs %d time(s).\n", countOccurrence(a, n, x));

    return 0;
}
