

def formatInput(input):

    temp = input.removesuffix(".")
    parts = temp.split('.')

    result = []
    for i in range(1, len(parts) + 1):
        current_part = ".".join(parts[-i:])
        result.append(current_part)

    return result


def listCache():




if __name__ == '__main__':
    print(formatInput('1.2.3.4.'))