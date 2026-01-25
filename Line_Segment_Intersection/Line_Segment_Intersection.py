import os
import heapq
import math
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib import colormaps
from sortedcontainers import SortedList
import networkx as nx

# =======================
# CONFIG
# =======================

USE_GRID_PREFILTER = True
GRID_SIZE = 0.01

USE_ANGLE_FILTER = True
MIN_ANGLE_DEG = 10

USE_MIN_LENGTH = True
MIN_SEGMENT_LENGTH = 0.0005

SHOW_HEATMAP = True
BUILD_GRAPH = True

EPS = 1e-9
CURRENT_SWEEP_X = 0.0

# =======================
# GEOMETRY
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
    if abs(denom) < EPS:
        return None

    ua = ((x4 - x3)*(y1 - y3) - (y4 - y3)*(x1 - x3)) / denom
    ub = ((x2 - x1)*(y1 - y3) - (y2 - y1)*(x1 - x3)) / denom

    if 0 <= ua <= 1 and 0 <= ub <= 1:
        return (x1 + ua*(x2-x1), y1 + ua*(y2-y1))
    return None

# =======================
# GRID PREFILTER
# =======================

def grid_key(pt):
    return (int(pt[0] // GRID_SIZE), int(pt[1] // GRID_SIZE))

def grid_prefilter(segments):
    grid = defaultdict(list)
    for s in segments:
        k1 = grid_key(s['start'])
        k2 = grid_key(s['end'])
        grid[k1].append(s)
        grid[k2].append(s)

    result = set()
    for cell in grid.values():
        if len(cell) > 1:
            for s in cell:
                result.add(s['id'])

    return [segments[i] for i in result]

# =======================
# SWEEP STRUCTURES
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
        if self.m is None:
            return self.y
        return self.m * x + self.b

    def __lt__(self, other):
        y1 = self.get_y(CURRENT_SWEEP_X)
        y2 = other.get_y(CURRENT_SWEEP_X)
        if abs(y1 - y2) > EPS:
            return y1 < y2
        return self.id < other.id

# =======================
# BENTLEY–OTTMANN
# =======================

def run_bentley_ottmann(segments, events):
    global CURRENT_SWEEP_X
    heapq.heapify(events)
    status = SortedList()
    active = {}
    intersections = []

    def valid_pair(s1, s2):
        if s1['taxi_id'] == s2['taxi_id']:
            return False
        if USE_MIN_LENGTH:
            if segment_length(s1) < MIN_SEGMENT_LENGTH or segment_length(s2) < MIN_SEGMENT_LENGTH:
                return False
        if USE_ANGLE_FILTER:
            if angle_diff(segment_angle(s1), segment_angle(s2)) < MIN_ANGLE_DEG:
                return False
        return True

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
            if not w:
                continue
            i = status.bisect_left(w)
            if i < len(status):
                status.pop(i)
            active.pop(data, None)

        else:  # INTERSECTION
            id1, id2 = data
            intersections.append((id1, id2))

    return intersections

# =======================
# VISUALIZATION
# =======================

def plot_all(segments, intersections, n):
    plt.figure(figsize=(10, 8))
    cmap = colormaps['tab10']
    colors = {f"{i}.txt": cmap(i % 10) for i in range(1, 11)}

    pts = []

    for s in segments:
        plt.plot(
            [s['start'][0], s['end'][0]],
            [s['start'][1], s['end'][1]],
            color=colors[s['taxi_id']], alpha=0.3
        )

    for a, b in intersections:
        pt = get_intersection_point(segments[a], segments[b])
        if pt:
            pts.append(pt)
            plt.plot(pt[0], pt[1], 'rx')

    plt.title(f"Intersections: {len(intersections)} (N={n})")
    plt.show()

    if SHOW_HEATMAP and pts:
        xs, ys = zip(*pts)
        plt.hist2d(xs, ys, bins=50)
        plt.colorbar()
        plt.title(f"Intersection Heatmap (N={n})")
        plt.show()

# =======================
# GRAPH
# =======================

def build_graph(segments, intersections):
    G = nx.Graph()
    for a, b in intersections:
        pt = get_intersection_point(segments[a], segments[b])
        if pt:
            G.add_node(pt)
    print(f"Graph nodes: {G.number_of_nodes()}")

# =======================
# PARSING
# =======================

def parse_data(path, n):
    segments = []
    events = []

    for i in range(1, 91):     #Εξετάζονται εώς και 90 logs 
        fn = f"{i}.txt"
        fp = os.path.join(path, fn)
        if not os.path.exists(fp):
            continue

        with open(fp) as f:
            pts = [(float(p[2]), float(p[3])) for p in
                   (line.strip().split(',') for line in f) if len(p) >= 4]

        for j in range(len(pts)-1):
            if len(segments) >= n:
                break
            p1, p2 = pts[j], pts[j+1]
            s, e = (p1, p2) if p1[0] <= p2[0] else (p2, p1)
            sid = len(segments)
            segments.append({'id': sid, 'taxi_id': fn, 'start': s, 'end': e})
            events.append((s[0], s[1], 'LEFT', sid))
            events.append((e[0], e[1], 'RIGHT', sid))

    return segments, events

# =======================
# MAIN
# =======================

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(base_path, "Data Set")
    
    # Έλεγχος αν ο φάκελος υπάρχει όντως
    if not os.path.exists(folder):
        print(f"Προσοχή: Ο φάκελος {folder} δεν βρέθηκε!")
    else:
        n = int(input("Επίλεξε πόσα segments θέλεις να δημιουργηθούν:"))

    segs, evs = parse_data(folder, n)

    if USE_GRID_PREFILTER:
        segs = grid_prefilter(segs)

    inters = run_bentley_ottmann(segs, evs)
    print(f"Βρέθηκαν {len(inters)} intersections")

    plot_all(segs, inters, n)

    if BUILD_GRAPH:
        build_graph(segs, inters)