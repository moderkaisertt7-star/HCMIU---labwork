#include <stdio.h>

int sumDigits(int n) {
    int sum = 0;
    while (n != 0) {
        sum += n % 10;
        n /= 10;
    }
    return sum;
}

int reverse(int n) {
    int reversed = 0;
    while (n != 0) {
        reversed = reversed * 10 + n % 10;
        n /= 10;
    }
    return reversed;
}

int isPalindrome(int n) {
    int original = n;
    int reversed = reverse(n);
    return original == reversed;
}

int main() {
    int n;
    char choice;

    do {
        printf("Enter an integer: ");
        scanf("%d", &n);

        printf("Sum of digits: %d\n", sumDigits(n));
        printf("Reversed: %d\n", reverse(n));
        printf("Palindrome: %s\n", isPalindrome(n) ? "Yes" : "No");

        printf("Continue? (y/n): ");
        scanf(" %c", &choice);
    } while (choice == 'y');

    printf("Exit program...\n");
    return 0;
}
