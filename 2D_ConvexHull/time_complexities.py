import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull

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

    for n in sizes:
        subset = points[:n]
        # convex hull time
        t0 = time.time()
        if len(subset) > 2: ConvexHull(subset)
        results_ch.append(time.time() - t0)
        
        # skyline time
        t0 = time.time()
        compute_skyline(subset)
        results_sky.append(time.time() - t0)
        print(f"N={n:7} | CH: {results_ch[-1]:.4f}s | Sky: {results_sky[-1]:.4f}s")

    plt.figure(figsize=(10, 6))
    plt.plot(sizes, results_ch, 'o-', label='Convex Hull $O(N \log N)$')
    plt.plot(sizes, results_sky, 's-', label='Skyline $O(N \log N)$')
    plt.xlabel('Number of Points (N)')
    plt.ylabel('Execution Time (sec)')
    plt.title('Experimental Proof of Theoretical Complexity')
    plt.legend(); plt.grid(True); plt.show()