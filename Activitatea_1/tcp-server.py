import socket
import threading

HOST = "127.0.0.1"
PORT = 3333
BUFFER_SIZE = 1024


class State:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

    def add(self, key, value):
        with self.lock:
            self.data[key] = value
        return "OK record added"

    def get(self, key):
        with self.lock:
            if key not in self.data:
                return "ERROR invalid key"
            return f"DATA {self.data[key]}"

    def remove(self, key):
        with self.lock:
            if key not in self.data:
                return "ERROR invalid key"
            del self.data[key]
        return "OK value deleted"

    def list_all(self):
        with self.lock:
            if not self.data:
                return "DATA|"
            items = [f"{k}={v}" for k, v in self.data.items()]
            return "DATA|" + ",".join(items)

    def count(self):
        with self.lock:
            return f"DATA {len(self.data)}"

    def clear(self):
        with self.lock:
            self.data.clear()
        return "OK all data deleted"

    def update(self, key, value):
        with self.lock:
            if key not in self.data:
                return "ERROR invalid key"
            self.data[key] = value
        return "OK data updated"

    def pop(self, key):
        with self.lock:
            if key not in self.data:
                return "ERROR invalid key"
            value = self.data.pop(key)
        return f"DATA {value}"


state = State()


def encode_response(message: str) -> bytes:
    # Protocol text: "<lungime> <mesaj>"
    return f"{len(message)} {message}".encode("utf-8")


def process_command(command: str):
    parts = command.strip().split()

    if not parts:
        return "ERROR empty command", False

    cmd = parts[0].upper()

    if cmd == "ADD":
        if len(parts) < 3:
            return "ERROR usage: ADD key value", False
        key = parts[1]
        value = " ".join(parts[2:])
        return state.add(key, value), False

    elif cmd == "GET":
        if len(parts) != 2:
            return "ERROR usage: GET key", False
        key = parts[1]
        return state.get(key), False

    elif cmd == "REMOVE":
        if len(parts) != 2:
            return "ERROR usage: REMOVE key", False
        key = parts[1]
        return state.remove(key), False

    elif cmd == "LIST":
        if len(parts) != 1:
            return "ERROR usage: LIST", False
        return state.list_all(), False

    elif cmd == "COUNT":
        if len(parts) != 1:
            return "ERROR usage: COUNT", False
        return state.count(), False

    elif cmd == "CLEAR":
        if len(parts) != 1:
            return "ERROR usage: CLEAR", False
        return state.clear(), False

    elif cmd == "UPDATE":
        if len(parts) < 3:
            return "ERROR usage: UPDATE key new_value", False
        key = parts[1]
        value = " ".join(parts[2:])
        return state.update(key, value), False

    elif cmd == "POP":
        if len(parts) != 2:
            return "ERROR usage: POP key", False
        key = parts[1]
        return state.pop(key), False

    elif cmd == "QUIT":
        return "OK PA BOSS", True

    else:
        return "ERROR unknown command", False


def handle_client(client_socket, addr):
    print(f"[SERVER] Client conectat: {addr}")

    with client_socket:
        while True:
            try:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break

                command = data.decode("utf-8").strip()
                print(f"[SERVER] Comanda primita de la {addr}: {command}")

                response, should_close = process_command(command)
                client_socket.sendall(encode_response(response))

                if should_close:
                    break

            except Exception as e:
                error_message = f"ERROR server exception: {str(e)}"
                try:
                    client_socket.sendall(encode_response(error_message))
                except Exception:
                    pass
                break

    print(f"[SERVER] Client deconectat: {addr}")


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"[SERVER] Listening on {HOST}:{PORT}")

        while True:
            client_socket, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True)
            thread.start()


if __name__ == "__main__":
    start_server()