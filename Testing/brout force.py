import time


def notz(strForAdd):
    return strForAdd[:-1] + chr(ord(strForAdd[-1]) + 1)


def last_is_z(strForAdd):
    if len(strForAdd) == 1:
        return 'aa'
    index = -2
    while True:
        if index * -1 > len(strForAdd):
            t = 'a'
            for i in range(len(strForAdd)):
                t += 'a'
            return t
        if strForAdd[index] != 'z':
            t = strForAdd[:index] + chr(ord(strForAdd[index]) + 1)
            index *= -1
            index -= 1
            for i in range(index):
                t += 'a'
            return t
        else:
            index -= 1


def generate_password(site_name: str):
    password = 'fsdjkfhf dfsdf23 678609 GJHKd dsdfe2ed 2e144 swd'  # gotta have at list 5 spaces
    for i in range(5):
        index = password.index(' ')
        password = password[:index] + site_name[i % len(site_name)] + password[index+1:]
    return password


def main():
    passw = generate_password('tanki')
    print(passw)
    # st = 'a'
    # t = time.time()
    # while st != 'zzzzzzz':
    #     print(st)
    #     if st[-1] != 'z':
    #         st = notz(st)
    #     else:
    #         st = last_is_z(st)
    # print(time.time() - t)


if __name__ == '__main__':
    main()
