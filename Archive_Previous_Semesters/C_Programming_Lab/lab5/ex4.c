#include <stdio.h>

#define PI 3.14159265358979323846

void calcCircle(double radius, double *circ, double *area) {
    *circ = 2.0 * PI * radius;
    *area = PI * radius * radius;
}

int main(void) {
    double radius;
    double circ, area;

    printf("Enter radius: ");
    if (scanf("%lf", &radius) != 1) return 1;

    calcCircle(radius, &circ, &area);

    printf("Radius: %.2f\n", radius);
    printf("Circumference: %.2f\n", circ);
    printf("Area: %.2f\n", area);

    return 0;
}
