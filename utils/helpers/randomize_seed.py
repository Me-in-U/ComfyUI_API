import random


def generate_random_15_digit_number():
    return random.randint(10**14, 10**15 - 1)


def generate_random_int():
    return random.randint(0, 2147483647)
