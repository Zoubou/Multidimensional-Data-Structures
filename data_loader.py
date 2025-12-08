import os
from datetime import datetime

def load_dataset(max_files=5):
    """
    Διαβάζει αρχεία T-Drive από τον φάκελο 'dataset'.
    :param max_files: Μέγιστος αριθμός αρχείων που θα διαβαστούν (για δοκιμή).
    :return: Λίστα με σημεία (x, y, t).
    """
    # Βρίσκουμε τον φάκελο 'dataset' αυτόματα
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(current_dir, 'dataset')
    
    all_points = []
    files_processed = 0

    print(f"--- Έλεγχος φακέλου: {dataset_path} ---")

    # Έλεγχος αν υπάρχει ο φάκελος
    if not os.path.exists(dataset_path):
        print(f"ΣΦΑΛΜΑ: Δεν βρέθηκε ο φάκελος 'dataset'.")
        return []

    # Διάβασμα των αρχείων
    files_list = [f for f in os.listdir(dataset_path) if f.endswith(".txt")]
    
    if not files_list:
        print("Δεν βρέθηκαν .txt αρχεία μέσα στον φάκελο dataset!")
        return []

    print(f"Βρέθηκαν {len(files_list)} αρχεία. Θα διαβαστούν τα πρώτα {max_files}.")

    for filename in files_list:
        file_path = os.path.join(dataset_path, filename)
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    # Format: taxi_id, date time, long, lat
                    
                    # 1. Parsing Χρόνου (Time t)
                    dt_str = parts[1]
                    dt_obj = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                    t = dt_obj.timestamp()
                    
                    # 2. Parsing Χώρου (x, y)
                    x = float(parts[2]) # Longitude
                    y = float(parts[3]) # Latitude
                    
                    # Προσθήκη στη λίστα
                    all_points.append((x, y, t))
            
            files_processed += 1
            print(f"OK: {filename}")

            if files_processed >= max_files:
                break
                
        except Exception as e:
            print(f"Σφάλμα στο αρχείο {filename}: {e}")

    print(f"--- Τέλος ---")
    print(f"Συνολικά φορτώθηκαν {len(all_points)} σημεία.")
    return all_points

# --- Αυτό το κομμάτι τρέχει μόνο αν πατήσεις Run σε αυτό το αρχείο ---
if __name__ == "__main__":
    # Δοκιμαστική εκτέλεση για 2 αρχεία
    points = load_dataset(max_files=2)
    
    # Εκτύπωση των πρώτων 5 σημείων για επιβεβαίωση
    if points:
        print("\nΔείγμα δεδομένων (πρώτα 5 σημεία):")
        for p in points[:5]:
            print(p)