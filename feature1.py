a = int(input("Enter the first number"))
b = int(input("Enter the second number"))

def gcd(a : int,b :int) -> int:
    arr1 = [i for i in range(2,a) if a % i == 0]
    arr2 = [i for i in range(2,b) if b % i == 0]
    gcd = 1
    for d in arr1:
        if d in arr2:
            gcd *= d
    return d

print(gcd(a,b))
