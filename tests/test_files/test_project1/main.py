def add(a, b):
    return a + b

def add2(a, b):
    return a + b

def add3(a, b):
    return a + b


def main():
    total = 0
    for i in range(5):
        total = add(total, i)

    # this comment should not be counted
    print(total)


if __name__ == "__main__":
    main()
