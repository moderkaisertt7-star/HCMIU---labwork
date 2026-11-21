#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void generate(int m[][50], int rows, int cols) {
    for (int i = 0; i < rows; i++)
        for (int j = 0; j < cols; j++)
            m[i][j] = rand() % 101;
}

void printMatrix(int m[][50], int rows, int cols) {
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            if (j > 0)
                printf("\t");
            printf("%d", m[i][j]);
        }
        printf("\n");
    }
}

void sortRowsAscending(int m[][50], int rows, int cols) {
    for (int i = 0; i < rows; i++) {
        for (int p = 0; p < cols - 1; p++) {
            for (int q = 0; q < cols - 1 - p; q++) {
                if (m[i][q] > m[i][q + 1]) {
                    int temp = m[i][q];
                    m[i][q] = m[i][q + 1];
                    m[i][q + 1] = temp;
                }
            }
        }
    }
}

void sortColumnsDescending(int m[][50], int rows, int cols) {
    for (int j = 0; j < cols; j++) {
        for (int p = 0; p < rows - 1; p++) {
            for (int q = 0; q < rows - 1 - p; q++) {
                if (m[q][j] < m[q + 1][j]) {
                    int temp = m[q][j];
                    m[q][j] = m[q + 1][j];
                    m[q + 1][j] = temp;
                }
            }
        }
    }
}

int main() {
    srand(time(NULL));

    int m[50][50];
    int M, N;

    printf("M = ");
    scanf("%d", &M);

    printf("N = ");
    scanf("%d", &N);

    generate(m, M, N);

    printf("Original matrix:\n");
    printMatrix(m, M, N);

    sortRowsAscending(m, M, N);
    printf("Rows ascending:\n");
    printMatrix(m, M, N);

    sortColumnsDescending(m, M, N);
    printf("Columns descending:\n");
    printMatrix(m, M, N);

    return 0;
}
