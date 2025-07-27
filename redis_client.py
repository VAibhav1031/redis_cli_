import socket
import threading
import sys
import time
import os
import readline
import atexit
from redis_cli import SimpleCompleter


histfile = os.path.join(
    os.path.expanduser("~/redis_cli/log/history/"), ".redis_net_history"
)
os.makedirs(os.path.dirname(histfile), exist_ok=True)

try:
    readline.read_history_file(histfile)
except FileNotFoundError:
    pass


atexit.register(readline.write_history_file, histfile)


completer = SimpleCompleter()
readline.set_completer(completer.complete)
readline.parse_and_bind("tab: complete")


def receive(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break

            # We are clearing current line for the output,
            # current line was the input redis so if there is data we will clear that
            # , and promt again, mean rewrite the text for the prompt we have cleared
            sys.stdout.write("\r" + " " * 80 + "\r")

            print(data.decode(), end="")

            # this  is  the  rewwrite thing mannn,
            sys.stdout.write("redis> ")
            sys.stdout.flush()
        except:
            break


sock_client = socket.socket()
sock_client.connect(("localhost", 6379))

threading.Thread(target=receive, args=(sock_client,), daemon=True).start()
time.sleep(0.1)
while True:
    try:
        msg = input("redis> ")
        if not msg:
            continue
        if msg.strip():
            sock_client.send(msg.encode())

    except KeyboardInterrupt:
        print("\nExiting Client!!!")
        break
