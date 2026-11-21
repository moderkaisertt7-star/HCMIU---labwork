#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main() {
    srand(time(NULL));
    char choices[] = {'H', 'T'};
    char a[10];
    int H = 0, T = 0;
    printf("coin flip: ");
    for (int i = 0; i < 10; i++) {
        char random_choice = choices[rand() % 2];
        a[i] = random_choice;
        printf("%c", a[i]);
        if (a[i] == 'H') {
            H++;
        } else {
            T++;
        }
    }
    printf("\nHeads: %d\n", H);
    printf("Tails: %d\n", T);
    

    return 0;
}