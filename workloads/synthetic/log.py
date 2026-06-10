with open("temp_log.txt", "w") as f:
    for i in range(10000):
        f.write(f"{i}\n")