import random


def run():
    BASE = 100000
    base = BASE
    balance = 1000000
    mid = 50
    for i in range(50):
        value = int(random.random() * 100)
        if value < mid:
            balance += base
            base = BASE
        if value >= mid:
            balance -= base
            base *= 2
        if balance < 0:
            break
    return balance


fail_count = 0
success_count = 0
zero_count = 0
ball = 0
for i in range(100000):
    b = run()
    if b < 0:
        zero_count += 1
        continue
    if b > 1000000:
        success_count += 1
    else:
        fail_count += 1
    ball += b
print(zero_count, fail_count, success_count)
print(zero_count * 1000000, ball, ball - zero_count * 1000000)
