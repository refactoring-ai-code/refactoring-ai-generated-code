package example;

class FirstDuplicate /* 😀 */	{
    int total(int n) {
        int spare = n + 5;
        int value = n + 17;
        value = value * 3 + 19;
        value = value * 5 + 23;
        value = value * 7 + 29;
        value = value * 11 + 31;
        value = value * 13 + 37;
        value = value * 17 + 41;
        value = value * 19 + 43;
        value = value * 23 + 47;
        return value;
    }
}
