def check_prime(n) :
    d = 2
    while d * d <= n :
        if n % d == 0 :
            return True
        d += 1
    return False