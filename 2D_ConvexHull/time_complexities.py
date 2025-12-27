import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
import tracemalloc

def compute_skyline(pts):
    sorted_indices = np.lexsort((-pts[:, 1], pts[:, 0]))
    sorted_pts = pts[sorted_indices]
    skyline = []
    max_pop = -1.0
    for p in sorted_pts:
        if p[1] > max_pop:
            skyline.append(p)
            max_pop = p[1]
    return np.array(skyline)

if __name__ == "__main__":
    df = pd.read_excel('data_movies_clean.xlsx')
    points = df[(df['budget'] > 0) & (df['popularity'] > 0)][['budget', 'popularity']].dropna().values
    
    sizes = [1000, 5000, 10000, 50000, 100000, 200000, 400000, len(points)]
    results_ch, results_sky = [], []
    mem_ch, mem_sky = [], []

    for n in sizes:
        subset = points[:n]
        # convex hull time and memory
        tracemalloc.start()
        t0 = time.time()
        if len(subset) > 2: ConvexHull(subset)
        t_ch = time.time() - t0
        _, peak_ch = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        results_ch.append(t_ch)
        mem_ch.append(peak_ch / 1024 / 1024)  # MB
        
        # skyline time and memory
        tracemalloc.start()
        t0 = time.time()
        compute_skyline(subset)
        t_sky = time.time() - t0
        _, peak_sky = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        results_sky.append(t_sky)
        mem_sky.append(peak_sky / 1024 / 1024)  # MB
        
        print(f"N={n:7} | CH: {t_ch:.4f}s {mem_ch[-1]:.2f}MB | Sky: {t_sky:.4f}s {mem_sky[-1]:.2f}MB")

    # Time plot
    plt.figure(figsize=(10, 6))
    plt.plot(sizes, results_ch, 'o-', label='Convex Hull $O(N \log N)$')
    plt.plot(sizes, results_sky, 's-', label='Skyline $O(N \log N)$')
    plt.xlabel('Number of Points (N)')
    plt.ylabel('Execution Time (sec)')
    plt.title('Time Complexity: Experimental Proof')
    plt.legend(); plt.grid(True); plt.show()

    # Space plot
    plt.figure(figsize=(10, 6))
    plt.plot(sizes, mem_ch, 'o-', label='Convex Hull')
    plt.plot(sizes, mem_sky, 's-', label='Skyline')
    plt.xlabel('Number of Points (N)')
    plt.ylabel('Peak Memory Usage (MB)')
    plt.title('Space Complexity: Memory Usage')
    plt.legend(); plt.grid(True); plt.show()
