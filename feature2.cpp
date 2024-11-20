#include <iostream>
#include <vector>


std::vector<int> num_to_vec(long long num) {
    std::vector<int> vec;
    while (num > 0) {
        vec.push_back(num % 10);
        num = num / 10;
    }
    for (auto &a : vec) {
        std::cout << a << ' ';
    }
    return vec;
}



int main() {
    int a,b;
    std::cin >> a >> b;
    for (int i = 0; i < std::max(a,b); ++i) {
        std::cout << a << ' ' << b;
    }

    return 0;
}