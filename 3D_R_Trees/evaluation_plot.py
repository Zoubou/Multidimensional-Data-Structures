import time
import matplotlib.pyplot as plt
import random
from data_loader import load_dataset
from rtree_index import RTree, MBR

def run_experiment():
    # Ορίζουμε τα βήματα του πειράματος (πόσα αρχεία θα φορτώνουμε κάθε φορά)
    # Ξεκινάμε χαλαρά και ανεβαίνουμε.
    file_counts = [10, 50, 100, 200, 400] 
    
    build_times = []
    query_times = []
    total_points_log = []

    print("--- Έναρξη Πειραματικής Αξιολόγησης ---")

    for count in file_counts:
        print(f"\nΤρέξιμο για {count} αρχεία...")
        
        # 1. Φόρτωση
        points = load_dataset(max_files=count)
        n_points = len(points)
        total_points_log.append(n_points)
        
        if n_points == 0:
            build_times.append(0)
            query_times.append(0)
            continue

        # 2. Μέτρηση Χρόνου Build (Insert)
        rtree = RTree(max_capacity=20)
        
        start_build = time.perf_counter() # Μεγάλη ακρίβεια
        for p in points:
            rtree.insert(p)
        end_build = time.perf_counter()
        
        build_time = end_build - start_build
        build_times.append(build_time)
        print(f" -> Build: {build_time:.4f} sec (Points: {n_points})")

        # 3. Μέτρηση Χρόνου Query (Μέσος όρος 100 τυχαίων αναζητήσεων)
        # Παίρνουμε τυχαία δείγματα για να είναι ρεαλιστικό το πείραμα
        avg_query_time = 0
        num_queries = 100
        
        start_query = time.perf_counter()
        for _ in range(num_queries):
            # Διαλέγουμε ένα τυχαίο σημείο από τα υπάρχοντα ως κέντρο
            center = random.choice(points)
            cx, cy, ct = center
            
            # Φτιάχνουμε μικρό παράθυρο αναζήτησης
            q_mbr = MBR(cx - 0.01, cx + 0.01, 
                        cy - 0.01, cy + 0.01, 
                        ct - 3600, ct + 3600)
            rtree.query(q_mbr)
            
        end_query = time.perf_counter()
        
        # Ο συνολικός χρόνος για 100 queries
        total_q_time = end_query - start_query
        # Μέσος χρόνος ανά query
        avg_query_time = total_q_time / num_queries
        
        query_times.append(avg_query_time)
        print(f" -> Avg Query: {avg_query_time:.6f} sec")

    # --- 4. Σχεδίαση Γραφημάτων ---
    print("\nΔημιουργία Γραφημάτων...")
    
    plt.figure(figsize=(12, 5))

    # Γράφημα 1: Build Time vs Number of Points
    plt.subplot(1, 2, 1)
    plt.plot(total_points_log, build_times, marker='o', color='b', label='Build Time')
    plt.title('R-tree Construction Time')
    plt.xlabel('Number of Points (N)')
    plt.ylabel('Time (seconds)')
    plt.grid(True)
    plt.legend()

    # Γράφημα 2: Query Time vs Number of Points
    plt.subplot(1, 2, 2)
    plt.plot(total_points_log, query_times, marker='s', color='r', label='Avg Query Time')
    plt.title('R-tree Range Query Performance')
    plt.xlabel('Number of Points (N)')
    plt.ylabel('Time (seconds)')
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.show()
    print("Ολοκληρώθηκε!")

if __name__ == "__main__":
    run_experiment()