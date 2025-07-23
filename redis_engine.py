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

        node.height = 1 + max(self.height_tree(node.left), self.height_tree(node.right))

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

        node.height = 1 + max(self.height_tree(node.left), self.height_tree(node.right))

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
            raise Exception("self_balancing got None — this should never happen!")
            return node

        if self._is_balanced(node):
            return node

        height_diff = self.height_tree(node.left) - self.height_tree(node.right)
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
