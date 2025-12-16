class SegmentTreeNode:
    def __init__(self, left, right):
        self.left = left      # interval left boundary
        self.right = right    # interval right boundary
        self.mid = (left + right) / 2
        self.left_child = None
        self.right_child = None
        
        # Intervals that fully cover this node's range:
        # These intervals are stored only at nodes fully covered by the interval.
        self.intervals = []


class SegmentTree:
    def __init__(self, intervals):
        """
        intervals = list of (low, high, data)
        """
        # Step 1: collect unique sorted boundary points
        points = sorted({p for interval in intervals for p in interval[:2]})
        
        # Build tree
        self.root = self._build(points, 0, len(points) - 1)
        
        # Insert intervals into the tree
        for interval in intervals:
            self._insert(self.root, interval)

    def _build(self, points, l, r):
        """Builds the segment tree over sorted coordinate points."""
        if l == r:
            return SegmentTreeNode(points[l], points[r])
        
        node = SegmentTreeNode(points[l], points[r])
        mid = (l + r) // 2
        node.left_child = self._build(points, l, mid)
        node.right_child = self._build(points, mid + 1, r)
        return node

    def delete(self, interval):
        """Remove an interval from the segment tree."""
        self._delete(self.root, interval)

    def _delete(self, node, interval):
        low, high, _ = interval

        # Interval fully covers this node → remove if present
        if low <= node.left and high >= node.right:
            if interval in node.intervals:
                node.intervals.remove(interval)
            return

        # Otherwise propagate to children
        if node.left_child and low <= node.left_child.right:
            self._delete(node.left_child, interval)
        if node.right_child and high >= node.right_child.left:
            self._delete(node.right_child, interval)


    def _insert(self, node, interval):
        low, high, data = interval
        
        # If interval fully covers this node range -> store here
        if low <= node.left and high >= node.right:
            node.intervals.append(interval)
            return
        
        # Otherwise propagate to children
        if node.left_child and low <= node.left_child.right:
            self._insert(node.left_child, interval)
        if node.right_child and high >= node.right_child.left:
            self._insert(node.right_child, interval)

    def stabbing_query(self, x):
        """Return all intervals that contain point x."""
        result = []
        self._stabbing(self.root, x, result)
        return result

    def _stabbing(self, node, x, result):
        # Outside range, stop
        if x < node.left or x > node.right:
            return
        
        # Add all intervals stored at this node
        for interval in node.intervals:
            result.append(interval)
        
        # Explore children
        if node.left_child and x <= node.left_child.right:
            self._stabbing(node.left_child, x, result)
        if node.right_child and x >= node.right_child.left:
            self._stabbing(node.right_child, x, result)
