from redis_cli import CustomExecutor
import socket
import threading


def handle_client(conn):
    process_cli_call(conn)


def process_cli_call(conn):
    executor = CustomExecutor()
    while True:
        try:
            # conn.send(b"redis> ") # this was my repl problem , it cause many ....
            data = conn.recv(1024)
            if not data:
                break

            inp = data.decode().strip()
            if not inp:
                continue

            if inp.upper() in ["CLR", "CLEAR"]:
                conn.send(b"\033[2J\033[H")  # clear screen
                continue
            elif inp.upper() == "EXIT":
                conn.send(b"Bye!\n")
                break
            elif inp.startswith("script"):
                _, path = inp.split(maxsplit=1)
                scr = executor.run_script(path)
                conn.send(scr.encode())
                continue
            else:
                response = executor.parser(inp)
                if isinstance(response, str):
                    response = response + "\n"
                elif isinstance(response, list):
                    response = (
                        "\n".join(f"{i + 1}) {item}" for i, item in enumerate(response))
                        + "\n"
                    )
                else:
                    response = str(response) + "\n"

                conn.send(response.encode())
        except Exception as e:
            conn.send(f"Error: {e}\n".encode())
            break

    print(f"Connection closed with : {addr}")
    conn.close()


server = socket.socket()
server.bind(("localhost", 6379))
server.listen()

while True:
    conn, addr = server.accept()
    if conn:
        print(f"Connected to : {addr} ")
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()
