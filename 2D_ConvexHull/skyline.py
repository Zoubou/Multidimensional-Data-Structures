import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def compute_skyline(pts):
    # sort: accending budget, descending popularity
    sorted_indices = np.lexsort((-pts[:, 1], pts[:, 0]))
    sorted_pts = pts[sorted_indices]
    
    skyline = []
    max_popularity_so_far = -1.0
    for p in sorted_pts:
        if p[1] > max_popularity_so_far:
            skyline.append(p)
            max_popularity_so_far = p[1]
    return np.array(skyline)

if __name__ == "__main__":
    df = pd.read_excel('data_movies_clean.xlsx')
    points = df[(df['budget'] > 0) & (df['popularity'] > 0)][['budget', 'popularity']].dropna().values
    
    skyline_pts = compute_skyline(points)
    print(f"Skyline has {len(skyline_pts)} optimal points.")
    
    plt.figure(figsize=(10, 6))
    plt.scatter(points[:, 0], points[:, 1], s=1, color='gray', alpha=0.3, label='Movies Data')
    plt.step(skyline_pts[:, 0], skyline_pts[:, 1], 'b-', where='post', label='Skyline', linewidth=2)
    plt.scatter(skyline_pts[:, 0], skyline_pts[:, 1], color='blue', s=30)
    plt.xlabel('Budget (USD)')
    plt.ylabel('Popularity Score')
    plt.title('Skyline Operator (MIN Budget & MAX Popularity)')
    plt.xscale('log')
    plt.legend()
    plt.show()