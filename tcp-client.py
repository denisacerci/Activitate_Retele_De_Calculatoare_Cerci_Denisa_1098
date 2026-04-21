import socket

HOST = "127.0.0.1"
PORT = 3333
BUFFER_SIZE = 1024


def receive_full_message(sock):
    data = sock.recv(BUFFER_SIZE)
    if not data:
        return None

    text = data.decode("utf-8")
    first_space = text.find(" ")

    if first_space == -1:
        return "ERROR invalid response format"

    length_part = text[:first_space]
    if not length_part.isdigit():
        return "ERROR invalid response length"

    message_length = int(length_part)
    message = text[first_space + 1:]

    while len(message) < message_length:
        chunk = sock.recv(BUFFER_SIZE)
        if not chunk:
            return None
        message += chunk.decode("utf-8")

    return message[:message_length]


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Conectat la server.")
        print("Comenzi: ADD, GET, REMOVE, LIST, COUNT, CLEAR, UPDATE, POP, QUIT")

        while True:
            command = input("client> ").strip()
            if not command:
                continue

            s.sendall(command.encode("utf-8"))
            response = receive_full_message(s)

            if response is None:
                print("Conexiunea a fost inchisa de server.")
                break

            print("Server:", response)

            if command.upper() == "QUIT":
                break


if __name__ == "__main__":
    main()