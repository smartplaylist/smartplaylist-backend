import time

for count in range(50):
    print(time.ctime())
    # Prints the current time with a five second difference
    time.sleep(5)
