import socket

try:
    ip = input("ip: ")
    port = 8080

    variant = int(input("variant: "))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip, port))
    sock.listen(2)
    
    p_1 = sock.accept()[0] # connecting player 1
    p_1.send(bytes([variant, 0]))
    print("player_1 connected")
    p_2 = sock.accept()[0] # connecting player 2
    p_2.send(bytes([variant, 1]))
    print("player_2 connected")

    p_1.send(b"start")
    p_2.send(b"start")
    print("Started")

    players = (p_1, p_2)
    turn = 0
    while True:
        data = players[turn].recv(256)
        data_d = data.decode()
        print(data_d)
        if data_d == "disconect":
            players[turn ^ 1].send(b"disconnect")
            break
        elif data_d == "end":
            break
        else:
            turn ^= 1
            players[turn].send(data)


except Exception as error:
    print(f"error: {error}")