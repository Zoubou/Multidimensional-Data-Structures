class Interval:
    def __init__(self, low, high, data=None):
        self.low = low
        self.high = high
        self.data = data 

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
    

    def insert(self, interval):
        """Insert a new interval into the interval tree."""
        self.root = self._insert(self.root, interval)


    def _insert(self, node, interval):
        if node is None:
            return Node(interval)

        if interval.low < node.interval.low:
            node.left = self._insert(node.left, interval)
        else:
            node.right = self._insert(node.right, interval)

        # Update max value
        node.max = max(
            node.interval.high,
            node.left.max if node.left else float("-inf"),
            node.right.max if node.right else float("-inf"),
        )

        return node
    

    def delete(self, interval):
        """Delete an interval from the interval tree."""
        self.root = self._delete(self.root, interval)


    def _delete(self, node, interval):
        if node is None:
            return None

        # Traverse BST
        if interval.low < node.interval.low:
            node.left = self._delete(node.left, interval)

        elif interval.low > node.interval.low:
            node.right = self._delete(node.right, interval)

        else:
            # Found candidate node — verify exact interval
            if node.interval.low == interval.low and node.interval.high == interval.high:

                # Case 1: no children
                if node.left is None and node.right is None:
                    return None

                # Case 2: one child
                if node.left is None:
                    return node.right
                if node.right is None:
                    return node.left

                # Case 3: two children
                # Replace with inorder successor (min of right subtree)
                successor = self._min_node(node.right)
                node.interval = successor.interval
                node.right = self._delete(node.right, successor.interval)

            else:
                # Same low, different interval — go right
                node.right = self._delete(node.right, interval)

        # Update max after deletion
        node.max = max(
            node.interval.high,
            node.left.max if node.left else float("-inf"),
            node.right.max if node.right else float("-inf"),
        )

        return node


