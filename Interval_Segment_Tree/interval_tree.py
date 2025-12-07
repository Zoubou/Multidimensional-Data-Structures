class Interval:
    def __init__(self, low, high, data=None):
        self.low = low
        self.high = high
        self.data = data  # optional: store river name etc.

    def overlaps(self, other):
        return self.low <= other.high and other.low <= self.high

    def __repr__(self):
        return f"[{self.low:.3f}, {self.high:.3f}]"


class Node:
    def __init__(self, interval):
        self.interval = interval
        self.max = interval.high
        self.left = None
        self.right = None


class IntervalTree:
    def __init__(self, intervals=None):
        self.root = None
        if intervals:
            self.build(intervals)

    # -------------------------------------------------------------------
    # BUILD A BALANCED INTERVAL TREE
    # -------------------------------------------------------------------
    def build(self, intervals):
        intervals = sorted(intervals, key=lambda iv: iv.low)

        def build_balanced(iv_list):
            if not iv_list:
                return None
            mid = len(iv_list) // 2
            node = Node(iv_list[mid])
            node.left = build_balanced(iv_list[:mid])
            node.right = build_balanced(iv_list[mid+1:])

            # update max value
            left_max = node.left.max if node.left else float("-inf")
            right_max = node.right.max if node.right else float("-inf")
            node.max = max(node.interval.high, left_max, right_max)

            return node

        self.root = build_balanced(intervals)

    # -------------------------------------------------------------------
    # INTERVAL QUERY: return all intervals overlapping with Q
    # -------------------------------------------------------------------
    def interval_query(self, query_interval):
        """
        Complexity: O(log n + k), where k = number of results
        """
        result = []
        stack = [self.root]

        while stack:
            node = stack.pop()
            if not node:
                continue

            # Check overlap
            if node.interval.overlaps(query_interval):
                result.append(node.interval)

            # Go left if useful
            if node.left and node.left.max >= query_interval.low:
                stack.append(node.left)

            # Always check right
            if node.right:
                stack.append(node.right)

        return result

    # ---------------------------------------------------------------
    # INSERT A NEW INTERVAL INTO THE TREE
    # ---------------------------------------------------------------
    def insert(self, interval):

        def insert_rec(node, interval):
            # Base case: empty spot → create new node
            if not node:
                return Node(interval)

            # BST insert using interval.low as the key
            if interval.low < node.interval.low:
                node.left = insert_rec(node.left, interval)
            else:
                node.right = insert_rec(node.right, interval)

            # Recompute max after insertion
            left_max = node.left.max if node.left else float('-inf')
            right_max = node.right.max if node.right else float('-inf')
            node.max = max(node.interval.high, left_max, right_max)

            return node

        self.root = insert_rec(self.root, interval)
        
    # ---------------------------------------------------------------
    # DELETE AN INTERVAL FROM THE TREE (by low & high)
    # ---------------------------------------------------------------
    def delete(self, interval):

        def delete_rec(node, interval):
            if not node:
                return None

            # BST traversal by low endpoint
            if interval.low < node.interval.low:
                node.left = delete_rec(node.left, interval)

            elif interval.low > node.interval.low:
                node.right = delete_rec(node.right, interval)

            else:
                # low matches → now confirm same interval
                if node.interval.low == interval.low and node.interval.high == interval.high:
                    
                    # ---------- CASE 1: NO CHILD ----------
                    if not node.left and not node.right:
                        return None

                    # ---------- CASE 2: ONE CHILD ----------
                    if not node.left:
                        return node.right
                    if not node.right:
                        return node.left

                    # ---------- CASE 3: TWO CHILDREN ----------
                    # Find inorder successor (smallest in right subtree)
                    successor = node.right
                    while successor.left:
                        successor = successor.left
                    
                    # Replace current node's interval with successor's
                    node.interval = successor.interval

                    # Delete successor recursively
                    node.right = delete_rec(node.right, successor.interval)

                else:
                    # same low but different interval → treat as right child
                    node.right = delete_rec(node.right, interval)

            # After deletion, update max values
            left_max = node.left.max if node.left else float("-inf")
            right_max = node.right.max if node.right else float("-inf")
            node.max = max(node.interval.high, left_max, right_max)

            return node

        self.root = delete_rec(self.root, interval)
