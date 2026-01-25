import os
import heapq
import math
import time
import matplotlib.pyplot as plt
from sortedcontainers import SortedList

# =======================
# CONFIG & CONSTANTS
# =======================
EPS = 1e-9
CURRENT_SWEEP_X = 0.0

# Ρυθμίσεις φίλτρων 
USE_ANGLE_FILTER = True
MIN_ANGLE_DEG = 10
USE_MIN_LENGTH = True
MIN_SEGMENT_LENGTH = 0.0005

# =======================
# GEOMETRY LOGIC
# =======================
def segment_length(seg):
    (x1, y1), (x2, y2) = seg['start'], seg['end']
    return math.hypot(x2 - x1, y2 - y1)

def segment_angle(seg):
    (x1, y1), (x2, y2) = seg['start'], seg['end']
    return math.degrees(math.atan2(y2 - y1, x2 - x1))

def angle_diff(a, b):
    d = abs(a - b)
    return min(d, 180 - d)

def get_intersection_point(s1, s2):
    (x1, y1), (x2, y2) = s1['start'], s1['end']
    (x3, y3), (x4, y4) = s2['start'], s2['end']
    denom = (y4 - y3)*(x2 - x1) - (x4 - x3)*(y2 - y1)
    if abs(denom) < EPS: return None
    ua = ((x4 - x3)*(y1 - y3) - (y4 - y3)*(x1 - x3)) / denom
    ub = ((x2 - x1)*(y1 - y3) - (y2 - y1)*(x1 - x3)) / denom
    if 0 <= ua <= 1 and 0 <= ub <= 1:
        return (x1 + ua*(x2-x1), y1 + ua*(y2-y1))
    return None

def valid_pair(s1, s2):
    if s1['taxi_id'] == s2['taxi_id']: return False
    if USE_MIN_LENGTH:
        if segment_length(s1) < MIN_SEGMENT_LENGTH or segment_length(s2) < MIN_SEGMENT_LENGTH:
            return False
    if USE_ANGLE_FILTER:
        if angle_diff(segment_angle(s1), segment_angle(s2)) < MIN_ANGLE_DEG:
            return False
    return True

# =======================
# BENTLEY–OTTMANN
# =======================
class SegmentWrapper:
    def __init__(self, seg):
        self.seg = seg
        self.id = seg['id']
        (x1, y1), (x2, y2) = seg['start'], seg['end']
        dx = x2 - x1
        if abs(dx) < EPS:
            self.m = None
            self.y = min(y1, y2)
        else:
            self.m = (y2 - y1) / dx
            self.b = y1 - self.m * x1

    def get_y(self, x):
        return self.m * x + self.b if self.m is not None else self.y

    def __lt__(self, other):
        y1 = self.get_y(CURRENT_SWEEP_X)
        y2 = other.get_y(CURRENT_SWEEP_X)
        if abs(y1 - y2) > EPS: return y1 < y2
        return self.id < other.id

def run_bentley_ottmann(segments, events):
    global CURRENT_SWEEP_X
    heapq.heapify(events)
    status = SortedList()
    active = {}
    intersections = []
    seen = set()

    while events:
        x, _, etype, data = heapq.heappop(events)
        CURRENT_SWEEP_X = x
        if etype == 'LEFT':
            seg = segments[data]
            w = SegmentWrapper(seg)
            active[seg['id']] = w
            status.add(w)
            i = status.bisect_left(w)
            for nb in [i-1, i+1]:
                if 0 <= nb < len(status):
                    s2 = status[nb].seg
                    key = tuple(sorted((seg['id'], s2['id'])))
                    if key not in seen and valid_pair(seg, s2):
                        pt = get_intersection_point(seg, s2)
                        if pt:
                            heapq.heappush(events, (pt[0], pt[1], 'X', key))
                            seen.add(key)
        elif etype == 'RIGHT':
            w = active.get(data)
            if not w: continue
            i = status.bisect_left(w)
            if i < len(status): status.pop(i)
            active.pop(data, None)
        else: # INTERSECTION
            intersections.append(data)
    return intersections

# =======================
# ANALYSIS TOOLS
# =======================
def brute_force_baseline(segments):
    
    start_time = time.time()
    count = 0
    # Χρήση των πρώτων 1000 segments για το baseline
    sample = segments[:1000]
    n_sample = len(sample)
    for i in range(n_sample):
        for j in range(i + 1, n_sample):
            if valid_pair(sample[i], sample[j]):
                get_intersection_point(sample[i], sample[j])
    end_time = time.time()
    duration = end_time - start_time
    # C = Time / N^2
    return duration / (n_sample**2)

def parse_data(path, n):
    segments, events = [], []
    for i in range(1, 21):
        fp = os.path.join(path, f"{i}.txt")
        if not os.path.exists(fp): continue
        with open(fp) as f:
            pts = [(float(p[2]), float(p[3])) for p in (line.strip().split(',') for line in f) if len(p) >= 4]
        for j in range(len(pts)-1):
            if len(segments) >= n: break
            p1, p2 = pts[j], pts[j+1]
            s, e = (p1, p2) if p1[0] <= p2[0] else (p2, p1)
            sid = len(segments)
            segments.append({'id': sid, 'taxi_id': f"{i}.txt", 'start': s, 'end': e})
            events.append((s[0], s[1], 'LEFT', sid))
            events.append((e[0], e[1], 'RIGHT', sid))
        if len(segments) >= n: break
    return segments, events

# =======================
# MAIN EXECUTION
# =======================
if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(base_path, "Data Set")
    
    n_values = [4000, 5000, 10000, 20000, 50000]
    bo_times = []
    bf_theoretical_times = []
    
    print(f"{'N':<10} | {'Intersections':<15} | {'BO Time (s)':<15} | {'BF Theoretical (s)':<15}")
    print("-" * 65)

    # Υπολογισμός σταθεράς Brute Force από ένα δείγμα 1000 στοιχείων
    temp_segs, _ = parse_data(folder, 1000)
    C_bf = brute_force_baseline(temp_segs)

    for n in n_values:
        segs, evs = parse_data(folder, n)
        
        # Μέτρηση Bentley-Ottmann
        start_bo = time.time()
        inters = run_bentley_ottmann(segs, evs)
        end_bo = time.time()
        
        duration_bo = end_bo - start_bo
        # Θεωρητικός Brute Force: T = C * n^2
        duration_bf = C_bf * (n**2)
        
        bo_times.append(duration_bo)
        bf_theoretical_times.append(duration_bf)
        
        print(f"{n:<10} | {len(inters):<15} | {duration_bo:<15.4f} | {duration_bf:<15.4f}")

    # Παραγωγή Διαγράμματος
    plt.figure(figsize=(10, 6))
    plt.plot(n_values, bo_times, marker='o', label='Bentley-Ottmann (Measured)')
    plt.plot(n_values, bf_theoretical_times, marker='s', linestyle='--', label='Brute Force (Theoretical $O(n^2)$)')
    
    plt.xlabel('Number of Segments (n)')
    plt.ylabel('Time (seconds)')
    plt.title('Time Complexity Comparison: Bentley-Ottmann vs Brute Force')
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.5)
    
    # Χρήση λογαριθμικής κλίμακας αν οι διαφορές είναι τεράστιες
    if max(bf_theoretical_times) / (max(bo_times) + 1e-6) > 100:
        plt.yscale('log')
        plt.ylabel('Time (seconds) - Log Scale')

    plt.savefig('performance_comparison.png') 
    plt.show()