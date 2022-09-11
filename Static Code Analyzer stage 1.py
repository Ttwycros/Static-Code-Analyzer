if __name__ == '__main__':
    name = input()
    with open(name, 'r') as file:
        for counter, line in enumerate(file):
            if len(line) > 79:
                print(f"Line {counter + 1}: S001 Too long")
