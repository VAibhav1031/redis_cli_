import atexit
import readline

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
        self.commands = ["SET", "GET", "DEL", "EXIT"]

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
                self.matches = self.options[:]

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
readline.set_completer(SimpleCompleter.complete)
readline.parse_and_bind("tab: complete")


class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.height = 1


class RedisEngine:
    def __init__(self):
        self.root = None

    def height_tree(self, node):
        if node is None:
            return -1
        return node.height

    def put(self, key, value) -> None:
        self.root = self._put(key, value, self.root)

    def _put(self, key, value, node):
        if node is None:
            node = Node(key, value)
            return node

        if key < node.key:
            node.left = self._put(key, value, node.left)

        elif key > node.key:
            node.right = self._put(key, value, node.right)

        else:
            node.value = value
            return node

        node.height = 1 + max(self.height_tree(node.left),
                              self.height_tree(node.right))

        return self.self_balancing(node)

    def remove(self, key):
        # cause we will reassign it man
        self.root = self._remove(key, self.root)

    def _remove(self, key, node):
        if node is None:
            return None

        if key < node.key:
            node.left = self._remove(key, node.left)

        elif key > node.key:
            node.right = self._remove(key, node.right)

        else:
            if node.left is None and node.right is None:
                return None

            if node.left is None:
                return node.right

            if node.right is None:
                return node.left

            else:
                sucessor = self.get_min(node.right)
                node.key = sucessor.key
                node.right = self._remove(sucessor.key, node.right)

        node.height = 1 + max(self.height_tree(node.left),
                              self.height_tree(node.right))

        return self.self_balancing(node)

    def get_min(self, node):
        while node.left:
            node = node.left
        return node

    def get(self, key, default=None):
        return self._get(key, self.root, "(nil)")

    def _get(self, key, node, default=None):
        if node is None:
            return default

        if key < node.key:
            return self._get(key, node.left, default)

        elif key > node.key:
            return self._get(key, node.right, default)

        else:
            return node.value

    def contains(self, key) -> bool:
        return self._contains(key, self.root)

    def _contains(self, key, node) -> bool:
        if node is None:
            return False

        if node.key == key:
            return True

        elif key < node.key:
            return self._contains(key, node.left)

        else:
            return self._contains(key, node.right)

    def isbalanced(self, node) -> bool:
        return self._is_balanced(node)

    def _is_balanced(self, node) -> bool:
        if node is None:
            return True

        return (
            abs(self.height_tree(node.left) - self.height_tree(node.right)) <= 1
            and self._is_balanced(node.left)
            and self._is_balanced(node.right)
        )

    def self_balancing(self, node):
        if node is None:
            raise Exception(
                "self_balancing got None — this should never happen!")
            return node

        if self._is_balanced(node):
            return node

        height_diff = self.height_tree(
            node.left) - self.height_tree(node.right)
        # you think how it will go
        if height_diff > 1:
            # left heavy
            if self.height_tree(node.left.left) >= self.height_tree(node.left.right):
                # left-left heavy
                return self.right_rotate(node)
                # cause we have to  reassign the  tree node , if we dont it will destroy tree

            else:
                # left-right heavy
                node.left = self.left_rotate(node.left)
                return self.right_rotate(node)

        if height_diff < -1:
            # Right heavy
            if self.height_tree(node.right.right) >= self.height_tree(node.right.left):
                # right-right heavy
                return self.left_rotate(node)
                # cause we have to  reassign the  tree node , if we dont it will destroy tree

            else:
                # right-left heavy
                # we need to conver this to the right-right (in simple straight main motive )
                node.right = self.right_rotate(node.right)
                return self.left_rotate(node)

        return node  # Dont get mad, if you think why this is needed , if  we are taking a safe for every exit, but still there is one situation, when there is imabalance
        # but no rotation , at that time we must return the node normally ,  either it will be none, and our Tree will become nothing

    def right_rotate(self, p):
        c = p.left
        t = c.right

        c.right = p
        p.left = t

        p.height = max(self.height_tree(p.left), self.height_tree(p.right)) + 1
        c.height = max(self.height_tree(c.left), self.height_tree(c.right)) + 1

        return c

    def left_rotate(self, c):
        p = c.right
        t = p.left

        p.left = c
        c.right = t

        p.height = max(self.height_tree(p.left), self.height_tree(p.right)) + 1
        c.height = max(self.height_tree(c.left), self.height_tree(c.right)) + 1

        return p

    def inorder(self):
        return self._inorder(self.root)

    def _inorder(self, node):
        if node is None:
            return []

        return (
            self._inorder(node.left)
            + [(node.key, node.value)]
            + self._inorder(node.right)
        )

    def items(self):
        yield from self._in_order(self.root)

    def _in_order(self, node):
        if node:
            yield from self._in_order(node.left)
            yield (node.key, node.value)
            yield from self._in_order(node.right)


class CustomExecutor(RedisEngine):
    # This will be a parser  type of thing where will parse the
    # input and send the input to right command
    def __init__(self):
        super().__init__()

        self.command_registry = {
            "SET": self.set_handlers,
            "GET": self.get_handlers,
            "DEL": self.del_handlers,
            "HELP": self.help,
        }

    def parser(self, input):
        new_up = input.split()
        if not new_up:
            return "Empty Command"
        cmd = new_up[0].upper()
        handlers = self.command_registry.get(cmd)
        args = new_up[1:]

        if not handlers:
            return f"Err: Unkown Command {cmd}"
        try:
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

    def cli_call(self):
        while True:
            inp = input("redis > ")
            if not inp:
                continue
            if inp.split()[0].upper() == "EXIT":
                print("Bye! ")
                break
            print(self.parser(inp))


com = CustomExecutor()
com.cli_call()
