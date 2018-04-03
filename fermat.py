import random

# Should return one of two values: 'prime' or 'composite'
def prime_test(N, k):

    # if k > n, just make k = (n-2) to avoid picking a ton of duplicates or useless numbers (0, 1)
    if k > N:
        k = (N - 2)

    used_a_values = []
    for i in range(0, k):  # loop for as many a-values as they told us to do

        a = random.randint(1, N-1)  # pick a random value in the Z-set of N (aka P)
        while a in used_a_values:
            a = random.randint(1, N-1)

        used_a_values.append(a)

        result = mod_exp(a, N-1, N)

        #check if it's NOT a 1 - if so, this number N can't be prime
        if result != 1:
            return 'composite'
        elif carmichael_test(N, a): # if carmichael_test says true, then the number was a "fake prime"
            return 'composite'

    # finished all the random a-values, so it must be prime
    return 'prime'


# Called by prime_test for every a-value (passed in by K)
def mod_exp(x, y, N):
    if y == 0:
        return 1        # BASE CASE
    z = mod_exp(x, y//2, N)
    if y % 2 == 0:      # if y is even
        return (z * z) % N
    else:               # if y is odd
        return x * (z * z) % N


# Returns true if the number is probably a carmichael number, false otherwise (so N is prime)
def carmichael_test(N, a):

    # Calculate t and u:
    u = N-1
    t = 0   # counter variable
    while u % 2 != 1:   # while u is even, keep dividing it in half and keep track of how many times we did it
        u = u / 2
        t += 1

    # Repeatedly square the u-value, and put (a, u, and N) through the mod_exp function until you get a 1
    prev_result = N-1  # setting this to N-1 allows for the case when mod_exp returns 1 first time
    for i in range(0, t+1):  # loop this t number of times
        result = mod_exp(a, u, N)  # square the u value and run it through mod_exp again

        # If we got a 1, look at the previous value to see if it equals N-1.
        # If so, then N is prime. If not, then N is composite.
        if result == 1:
            if prev_result == (N - 1):
                # N is prime, so N cannot be a carmichael number
                return False
            else:
                # N is composite, so N is probably a carmichael number
                return True

        prev_result = result
        u = u*2

    # N is not prime, so N is probably a carmichael number
    return True



# Calculates the probability that this number, which we're reporting is prime, is actually a composite.
def probability(k):
    return 1.0 - (1.0/(2.0 ** k))