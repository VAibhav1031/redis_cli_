import atexit
import readline
from redis_engine import RedisEngine

# Optional: persist history across sessions (if you want this)
import os

histfile = os.path.join(os.path.expanduser("~"), ".redis_shell_history")
try:
    readline.read_history_file(histfile)
except FileNotFoundError:
    pass

atexit.register(readline.write_history_file, histfile)


class SimpleCompleter:
    def __init__(self):
        self.commands = ["SET", "GET", "DEL", "KEYS", "EXIT"]

    def complete(self, text, state):
        response = None
        if state == 0:
            # This is the first time for this text,
            # so build a match list.
            if text:
                self.matches = [
                    cmd for cmd in self.commands if cmd.startswith(text.upper())
                ]

            else:
                self.matches = self.commands[:]

        # Return the state'th item from the match list,
        # if we have that many.
        try:
            response = self.matches[state]
        except IndexError:
            response = None

        return response


# example  telling you why we use the state, it is basically tells us
# with every tab it will go for next state meaning next command with same startswith
# , if it is their
#     Now if you type:
#
# g <Tab>
#
# The flow is:
#
#     completer("g", 0) → returns "GET"
#
#     completer("g", 1) → returns "GIVE"
#
#     completer("g", 2) → returns "GROW"
#
#     completer("g", 3) → returns None → readline stops
#


# 2. Attach the completer to readline
#
completer = SimpleCompleter()
readline.set_completer(completer.complete)
readline.parse_and_bind("tab: complete")


class CustomExecutor(RedisEngine):
    # This will be a parser  type of thing where will parse the
    # input and send the input to right command
    def __init__(self):
        super().__init__()

        self.command_registry = {
            "SET": self.set_handlers,
            "GET": self.get_handlers,
            "DEL": self.del_handlers,
            "KEYS": self.key_handlers,
            "HELP": self.help,
        }

    def parser(self, input):
        new_up = input.split()
        if not new_up:
            return "Empty Command"
        cmd = new_up[0].strip().upper()
        handlers = self.command_registry.get(cmd)
        args = new_up[1:]

        if not handlers:
            return f"Err: Unkown Command {cmd}"
        try:
            if handlers == self.key_handlers:
                return handlers()
            return handlers(args)

        except ValueError as e:
            print(f"Error : {e}")

    def set_handlers(self, args):
        if len(args) != 2:
            return "ERR: SET needs key and value"
        self.put(args[0], args[1])
        return "OK"

    def get_handlers(self, args):
        if len(args) != 1:
            return "ERR: GET only needs key"
        return self.get(args[0])

    def del_handlers(self, args):
        if len(args) != 1:
            return "ERR: DEL only needs key"

        if not self.contains(args[0]):
            return "0"

        else:
            self.remove(args[0])
            return "1"

    def help(self, args=None):
        if not args:
            return "Usage: help [command/function]\nIt will try to give you simple usage of that command "

        else:
            if len(args) != 1:
                return "ERR: It only need one command"
            cmd_help = args[0].upper()
            if cmd_help == "SET":
                return "Usage: SET [key] [value]"

            elif cmd_help == "GET":
                return "Usage: GET [key]\nIT basically retrieves the value of Key"

            elif cmd_help == "DEL":
                return "Usage: DEL [Key]\nThis command deletes the key value"

            else:
                return "Unkown Command\n Usage: help [command/function]\n It will try to give you simple usage of that command "

    def key_handlers(self):
        return [k for k, _ in self.inorder()]

    def clear_screen(self):
        os.system("clear")

    def run_script(self, file_path):
        try:
            with open(file_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("#"):
                        continue
                    if line == "":
                        continue
                    output = self.parser(line)
                    if output is not None:
                        print(output)
        except FileNotFoundError:
            print("Script file not found.")

    def cli_call(self):
        while True:
            inp = input("redis > ")
            if not inp:
                continue

            if inp.startswith("script"):
                _, path = inp.split(maxsplit=1)
                self.run_script(path)
                continue
            if inp.split()[0].upper() in ["CLR", "CLEAR"]:
                self.clear_screen()
                continue
            if inp.split()[0].upper() == "EXIT":
                print("Bye! ")
                break
            print(self.parser(inp))


com = CustomExecutor()
com.cli_call()
