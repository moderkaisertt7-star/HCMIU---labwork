#include <stdio.h>

int main(void) {
    char grade;
    char choice;

    do {
        printf("Enter a grade: ");
        if (scanf(" %c", &grade) != 1) {
            return 1;
        }

        if (grade == 'A' || grade == 'a') {
            printf("Excellent!\n");
        } else if (grade == 'B' || grade == 'b') {
            printf("Good!\n");
        } else if (grade == 'C' || grade == 'c') {
            printf("Fair!\n");
        } else if (grade == 'D' || grade == 'd') {
            printf("Average!\n");
        } else if (grade == 'F' || grade == 'f') {
            printf("Weak!\n");
        } else {
            printf("Invalid grade entered.\n");
        }

        printf("Continue? (y/n): ");
        if (scanf(" %c", &choice) != 1) {
            return 1;
        }
    } while (choice == 'y' || choice == 'Y');

    printf("Exit program...\n");
    return 0;
}