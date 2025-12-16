import sys

class MBR:
    """
    Αναπαριστά ένα 3D κουτί (Minimum Bounding Rectangle).
    Διαστάσεις: x (long), y (lat), t (time)
    """
    def __init__(self, x1, x2, y1, y2, t1, t2):
        self.x1 = min(x1, x2)
        self.x2 = max(x1, x2)
        self.y1 = min(y1, y2)
        self.y2 = max(y1, y2)
        self.t1 = min(t1, t2)
        self.t2 = max(t1, t2)

    def area(self):
        """Υπολογίζει τον όγκο του κουτιού (Volume)"""
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        dt = self.t2 - self.t1
        return dx * dy * dt

    def perimeter(self):
        """Υπολογίζει την περίμετρο (χρήσιμο για μετρικές βελτιστοποίησης)"""
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        dt = self.t2 - self.t1
        return 4 * (dx + dy + dt)

    def intersects(self, other):
        """Ελέγχει αν τέμνεται με άλλο MBR (για αναζήτηση)"""
        return not (self.x2 < other.x1 or self.x1 > other.x2 or
                    self.y2 < other.y1 or self.y1 > other.y2 or
                    self.t2 < other.t1 or self.t1 > other.t2)

    def contains_point(self, x, y, t):
        """Ελέγχει αν ένα σημείο είναι μέσα στο κουτί"""
        return (self.x1 <= x <= self.x2 and
                self.y1 <= y <= self.y2 and
                self.t1 <= t <= self.t2)

    @staticmethod
    def from_points(points):
        """Δημιουργεί ένα MBR που περικλείει μια λίστα σημείων"""
        if not points:
            return None
        
        # Αρχικοποίηση με το πρώτο σημείο
        min_x, max_x = points[0][0], points[0][0]
        min_y, max_y = points[0][1], points[0][1]
        min_t, max_t = points[0][2], points[0][2]

        for p in points[1:]:
            min_x = min(min_x, p[0])
            max_x = max(max_x, p[0])
            min_y = min(min_y, p[1])
            max_y = max(max_y, p[1])
            min_t = min(min_t, p[2])
            max_t = max(max_t, p[2])

        return MBR(min_x, max_x, min_y, max_y, min_t, max_t)

class Node:
    """
    Κόμβος του R-tree.
    """
    def __init__(self, is_leaf=True):
        self.is_leaf = is_leaf
        self.entries = [] # Αν είναι Leaf: περιέχει tuples (x,y,t, obj_id)
                          # Αν είναι Internal: περιέχει αντικείμενα Node
        self.mbr = None   # Το MBR που καλύπτει όλα τα entries

    def update_mbr(self):
        """Ενημερώνει το MBR του κόμβου με βάση τα περιεχόμενά του"""
        if not self.entries:
            self.mbr = None
            return

        if self.is_leaf:
            # Αν είμαστε φύλλο, τα entries είναι σημεία (x, y, t)
            # Φτιάχνουμε MBR που τα καλύπτει όλα
            self.mbr = MBR.from_points(self.entries)
        else:
            # Αν είμαστε εσωτερικός κόμβος, τα entries είναι άλλοι Nodes
            # Πρέπει να βρούμε τα min/max από τα MBR των παιδιών
            first_mbr = self.entries[0].mbr
            if not first_mbr: return # Safety check

            min_x, max_x = first_mbr.x1, first_mbr.x2
            min_y, max_y = first_mbr.y1, first_mbr.y2
            min_t, max_t = first_mbr.t1, first_mbr.t2

            for child in self.entries[1:]:
                c_mbr = child.mbr
                min_x = min(min_x, c_mbr.x1)
                max_x = max(max_x, c_mbr.x2)
                min_y = min(min_y, c_mbr.y1)
                max_y = max(max_y, c_mbr.y2)
                min_t = min(min_t, c_mbr.t1)
                max_t = max(max_t, c_mbr.t2)
            
            self.mbr = MBR(min_x, max_x, min_y, max_y, min_t, max_t)

    def is_full(self, max_capacity):
        return len(self.entries) >= max_capacity

# --- Μικρό τεστ για να δούμε αν δουλεύει ---
if __name__ == "__main__":
    # Δημιουργούμε 3 τυχαία σημεία
    p1 = (10, 10, 100)
    p2 = (20, 20, 200)
    p3 = (15, 15, 150)

    # Φτιάχνουμε έναν κόμβο (Leaf) και τα βάζουμε μέσα
    node = Node(is_leaf=True)
    node.entries = [p1, p2, p3]
    
    # Ζητάμε να υπολογίσει το κουτί του
    node.update_mbr()

    print("--- Test Node MBR ---")
    print(f"X range: {node.mbr.x1} - {node.mbr.x2}")
    print(f"Y range: {node.mbr.y1} - {node.mbr.y2}")
    print(f"T range: {node.mbr.t1} - {node.mbr.t2}")
    
    