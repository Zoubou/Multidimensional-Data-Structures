import time
import math
from rtree_structure import Node, MBR
from data_loader import load_dataset

class RTree:
    def __init__(self, max_capacity=4):
        # Δημιουργία της ρίζας (αρχικά είναι φύλλο)
        self.root = Node(is_leaf=True)
        self.max_capacity = max_capacity

    def insert(self, point):
        """Εισάγει ένα σημείο (x, y, t) στο δέντρο."""
        # Η αναδρομική insert επιστρέφει (new_node, new_mbr) αν έγινε split
        split_result = self._insert_recursive(self.root, point)
        
        if split_result is not None:
            # Αν η ρίζα έσπασε, φτιάχνουμε νέα ρίζα που δείχνει στην παλιά και την καινούρια
            new_child, _ = split_result
            new_root = Node(is_leaf=False)
            new_root.entries = [self.root, new_child]
            new_root.update_mbr()
            self.root = new_root

    def _insert_recursive(self, node, point):
        """Αναδρομική διαδικασία εισαγωγής."""
        # 1. Αν δεν είναι φύλλο, πρέπει να διαλέξουμε σε ποιο παιδί θα πάμε (ChooseLeaf)
        if not node.is_leaf:
            best_child = self._choose_leaf(node, point)
            split_result = self._insert_recursive(best_child, point)
            
            # Αν το παιδί έσπασε, προσθέτουμε το νέο αδερφάκι του εδώ
            if split_result:
                new_child, _ = split_result
                node.entries.append(new_child)
                node.update_mbr()
                
                if node.is_full(self.max_capacity):
                    return self._split(node)
            else:
                # Αν δεν έσπασε, απλά ενημερώνουμε το MBR (ίσως μεγάλωσε)
                node.update_mbr()
            
            return None

        # 2. Αν είναι φύλλο, απλά βάζουμε το σημείο
        else:
            node.entries.append(point)
            node.update_mbr()
            
            # Αν γέμισε, κάνουμε Split
            if node.is_full(self.max_capacity):
                return self._split(node)
            return None

    def _choose_leaf(self, node, point):
        """Επιλέγει το παιδί που χρειάζεται τη μικρότερη μεγέθυνση."""
        best_child = node.entries[0]
        min_enlargement = float('inf')
        
        x, y, t = point
        
        for child in node.entries:
            # Υπολογισμός τρέχοντος όγκου
            current_area = child.mbr.area()
            
            # Υπολογισμός νέου όγκου αν βάζαμε το σημείο
            new_x1 = min(child.mbr.x1, x)
            new_x2 = max(child.mbr.x2, x)
            new_y1 = min(child.mbr.y1, y)
            new_y2 = max(child.mbr.y2, y)
            new_t1 = min(child.mbr.t1, t)
            new_t2 = max(child.mbr.t2, t)
            
            new_area = (new_x2 - new_x1) * (new_y2 - new_y1) * (new_t2 - new_t1)
            enlargement = new_area - current_area
            
            if enlargement < min_enlargement:
                min_enlargement = enlargement
                best_child = child
                
        return best_child

    def _split(self, node):
        """Χωρίζει τον κόμβο στα δύο (Linear Split Logic)."""
        # Στρατηγική: Ταξινομούμε τα αντικείμενα στον άξονα Χ και κόβουμε στη μέση.
        mid = len(node.entries) // 2
        
        if node.is_leaf:
            node.entries.sort(key=lambda p: p[0]) # Sort by X coordinate
        else:
            node.entries.sort(key=lambda n: n.mbr.x1) # Sort by MBR X
            
        # Δημιουργία νέου κόμβου
        new_node = Node(is_leaf=node.is_leaf)
        
        # Μεταφορά των μισών στοιχείων στο νέο κόμβο
        new_node.entries = node.entries[mid:]
        node.entries = node.entries[:mid]
        
        # Ενημέρωση MBRs
        node.update_mbr()
        new_node.update_mbr()
        
        return new_node, new_node.mbr

    def query(self, search_mbr):
        """Range Query: Βρες όλα τα σημεία μέσα στο search_mbr."""
        results = []
        self._query_recursive(self.root, search_mbr, results)
        return results

    def _query_recursive(self, node, search_mbr, results):
        # 1. Αν δεν τέμνονται τα κουτιά, δεν χρειάζεται να ψάξουμε εδώ
        if not node.mbr or not node.mbr.intersects(search_mbr):
            return

        # 2. Αν είναι φύλλο, ελέγχουμε τα σημεία
        if node.is_leaf:
            for p in node.entries:
                x, y, t = p
                if search_mbr.contains_point(x, y, t):
                    results.append(p)
        else:
            # 3. Αν είναι κόμβος, ψάχνουμε στα παιδιά
            for child in node.entries:
                self._query_recursive(child, search_mbr, results)

# --- ΠΕΙΡΑΜΑΤΙΚΗ ΑΞΙΟΛΟΓΗΣΗ (Evaluation) ---
if __name__ == "__main__":
    print("--- 1. Φόρτωση Δεδομένων ---")
    # Διάβασε 10 αρχεία για το Demo
    points = load_dataset(max_files=10) 
    
    if not points:
        print("Δεν βρέθηκαν δεδομένα. Έλεγξε τον φάκελο 'dataset'.")
        exit()

    print(f"\n--- 2. Χτίσιμο R-tree (Build) ---")
    rtree = RTree(max_capacity=20) # Κάθε κόμβος χωράει μέχρι 20 σημεία
    
    start_time = time.time()
    for p in points:
        rtree.insert(p)
    end_time = time.time()
    
    print(f"Build Time: {end_time - start_time:.4f} seconds")
    print(f"Total Points Inserted: {len(points)}")
    
    # --- Δημιουργία ενός Ερωτήματος (Query) ---
    # Παίρνουμε το 1ο σημείο ως κέντρο για να είμαστε σίγουροι ότι θα βρούμε κάτι
    sample = points[0]
    sx, sy, st = sample
    
    # Φτιάχνουμε ένα "κουτί" αναζήτησης γύρω από αυτό
    # Περιοχή: +/- 0.01 μοίρες (περίπου 1km), Χρόνος: +/- 1 ώρα (3600 sec)
    query_mbr = MBR(sx - 0.01, sx + 0.01, 
                    sy - 0.01, sy + 0.01, 
                    st - 3600, st + 3600)
                    
    print(f"\n--- 3. Εκτέλεση Range Query ---")
    print(f"Ψάχνουμε περιοχή γύρω από το ({sx:.4f}, {sy:.4f}) στο χρόνο {st}")
    
    start_time = time.time()
    results = rtree.query(query_mbr)
    end_time = time.time()
    
    print(f"Βρέθηκαν {len(results)} σημεία.")
    print(f"Query Time: {end_time - start_time:.6f} seconds")