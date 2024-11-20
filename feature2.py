a = int(input("Enter your number"))

def is_prime(a) :
    d = 2
    while d*d <= a:
        if a % d == 0:
            return True
    return False