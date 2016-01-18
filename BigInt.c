//Big Integer implementation in C

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MIN(a,b) (((a)<(b))?(a):(b))
#define MAX(a,b) (((a)>(b))?(a):(b))


//modulo and integer division defined so that
//the modulo part is always positive
int mmod(int n, int d) {
    int k = n%d;
    if (k>=0) {return k;}
    else {return k+d;}
}

int mdiv(int n, int d) {
    if (n>=0) {return n/d;}
    else {return n/d - 1;}
}


char *strrev(char *s){
    int i,n;
    char *reverse; 
    for(i=0;s[i]!='\0';i++)
        ;
    reverse=malloc(i*sizeof(char));
    n=i-1;
    for(i=n;i>=0;i--) {
        reverse[n-i]=s[i];
    }
    reverse[n+1]='\0';
    return reverse;
}

typedef struct BigInt {
    int *digits;
    int sign;
    int length;
    int size;
} BigInt;

int eq(BigInt *a, BigInt *b);
int geq(BigInt *a, BigInt *b);


BigInt *fromString(char* str) {
    int ifnegative = 0;
    int sign = 1;
    if(str[0]=='-') {
        ifnegative = 1;
        sign = -1;
    }
    str = strrev(str);
    int size=16;
    int *digits = (int*) malloc(size*sizeof(int));
    int length = 0;
    int i=0;
    if(str)
    while(str[i++ + ifnegative]) {
        digits[i-1] = str[i-1] - '0';
        length++;
        if (length==size-2) {
            size *= 2;
            digits = realloc(digits, size*sizeof(int));
        }
    }
    if (digits[0]==0 && length==1) {
        sign = 0;
    }
    BigInt *num = (BigInt*)malloc(sizeof(BigInt));
    num->length=length;
    num->size=size;
    num->digits=digits;
    num->sign=sign;
    return num; 
}

//removes leading zeroes
BigInt *trim(BigInt *num) {
    int i = num->length-1;
    while(num->digits[i]==0 && i!=0) {
        --num->length; --i;
    }
    return num;
}

char *toString(BigInt *num) {
    num = trim(num);
    char *result = calloc(num->length+1, sizeof(char));
    int i;
    int ifnegative = 0;
    if (num->sign == -1) {
        ifnegative = 1;
        result[num->length] = '-';
    }
    for (i=0; i<= num->length-1 ;i++) {
        result[i] = '0' + num->digits[i];
    }
    return strrev(result);
}

BigInt *balance(BigInt *num) {
    //makes sure every entry in digits is a digit
    int length = num->length;
    int *digits = num->digits;
    int sign = num->sign;
    int i=0;
    int needs_repeating = 0;
    for(i=0; i<length-1;++i) {
        digits[i+1] += mdiv(digits[i], 10);
        digits[i] = mmod(digits[i], 10);
    }
    if (digits[length-1] >= 10) {
        int a = mdiv(digits[length-1], 10);
        int b = mmod(digits[length-1], 10);
        digits[length] = a;
        digits[length-1] = b;
        ++length;
    }
    if(digits[length-1]<0) {
        digits[length-1] *= -1;
        sign *= -1;
        //perform k*10^length - rest = (k-1)*10^length + 999..99 - rest + 1
        digits[length-1] -= 1;
        for(i=0; i<length-1; ++i) {
            digits[i] = 9 - digits[i];
        }
        digits[0] += 1; //may cause digits[0] to become unbalanced again
        needs_repeating = 1;
    }

    num->digits = digits;
    num->length = length;
    num->sign = sign;
    num->size = num->size;
    if (needs_repeating) {num = balance(num);} //won't have the same problem again
    if(!strcmp(toString(num), "0")) {
        num->sign = 0;
    }
    return num;
    //TODO add 0
}

BigInt *add(BigInt *a, BigInt *b) {
    int size = MAX(a->size, b->size) + 5;
    int longer = MAX(a->length, b->length);
    int shorter = MIN(a->length, b->length);
    BigInt *bigger;
    if (longer==a->length) {
        bigger = a;
    }
    else {
        bigger = b;
    }
    int length = longer;
    int *digits = (int*)malloc(size*sizeof(int));
    int i;
    for(i=0;i<length;i++) {
        if(i>=shorter) {
            digits[i]=bigger->digits[i]*bigger->sign;
        }
        else {
            digits[i] = a->digits[i]*a->sign + b->digits[i]*b->sign;
        }
    }
    BigInt *result = (BigInt*)malloc(sizeof(BigInt));
    result->sign = 1;
    result->size = size;
    result->length = length;
    result->digits = digits;
    result = balance(result);
    return result;
}

BigInt *subtract(BigInt *a, BigInt *b) {
    b->sign *= -1;
    BigInt *sum = add(a,b);
    b->sign *= -1;
    return sum;
}

BigInt *mult(BigInt *a, BigInt *b) {
    int size = a->size * b->size + 2;
    int length = a->length + b->length;
    int sign = a->sign * b->sign;
    int *digits = (int*) calloc(size, sizeof(int));

    BigInt *result = (BigInt*) malloc(sizeof(BigInt));
    result->size = size;
    result->length = length;
    result->sign = sign;
    result->digits = digits;
    int i, j;
    for (i=0; i < a->length ;i++) {
        digits = result->digits;
        for(j=0; j < b->length ;j++) {
            digits[i+j] += a->digits[i] * b->digits[j];
            if(i+j >= result->length) {result->length = i+j+1;}
        }
        result->digits = digits;
        result = balance(result);
    }
    return result;
}


int geq(BigInt *a, BigInt *b) {
    BigInt *diff = subtract(a,b);
    if (diff->sign == 1 || diff->sign == 0) {
        return 1;
    }
    else {
        return 0;
    }
}

int eq(BigInt *a, BigInt *b) {
    if (geq(a,b) && geq(b,a)) {
        return 1;
    }
    else {
        return 0;
    }
}

BigInt *bigabs(BigInt *a) {
    BigInt *zero = fromString("0");
    BigInt *result = add(a, zero); //to copy the object
    if (eq(result, zero)) {
        return result;
    }
    result->sign=1;
    return result;
}

BigInt *divide(BigInt *bigger, BigInt *smaller) {
    if (eq(smaller, fromString("0"))) {
        fprintf(stderr, "division by 0\n");
        return NULL;
    }
    int sign = bigger->sign * smaller->sign;
    bigger = bigabs(bigger);
    smaller = bigabs(smaller);
    BigInt *ten = fromString("10");
    BigInt *divisor = smaller;
    if (eq(smaller, bigger)) {
        return fromString("1");
    }
    if (geq(smaller, bigger)) {
        return fromString("0");
    }

    BigInt *tens = fromString("1");
    while(geq(mult(divisor, ten), bigger)) {
        divisor = mult(divisor, ten);
        tens = mult(tens, ten);
    }
    BigInt *result = add(tens,divide(subtract(bigger, divisor), smaller));
    result->sign = sign;
    return result;
}

int main() {
    BigInt *num1 = fromString("111111111111111111111");
    BigInt *num2 = fromString("111111111111111111111");
    printf("%s * %s = %s\n", toString(num1), toString(num2), toString(mult(num1, num2)));
    exit(0);
}