# Generated Python code

def main():
    a = 5
    t0 = a == 2
    if t0:
        print("Level 1 - Branch 1")
    else:
        t1 = a == 3
        if t1:
            print("Level 2 - Branch 1")
        else:
            t2 = a == 4
            if t2:
                print("Level 3 - Branch 1")
            else:
                t3 = a == 5
                if t3:
                    print("Level 4 - Branch 1")
                else:
                    print("Level 4 - Branch 2")
    return

if __name__ == '__main__':
    main()