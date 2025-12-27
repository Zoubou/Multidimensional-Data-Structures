import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def compute_skyline(pts):
    # sort: ascending budget, descending popularity
    sorted_indices = np.lexsort((-pts[:, 1], pts[:, 0]))
    sorted_pts = pts[sorted_indices]
    
    skyline_indices = []
    max_popularity_so_far = -1.0
    for i, p in enumerate(sorted_pts):
        if p[1] > max_popularity_so_far:
            skyline_indices.append(sorted_indices[i])
            max_popularity_so_far = p[1]
    return skyline_indices

if __name__ == "__main__":
    df = pd.read_excel('data_movies_clean.xlsx')
    filtered_df = df[(df['budget'] > 0) & (df['popularity'] > 0)].dropna()
    points = filtered_df[['budget', 'popularity']].values
    
    skyline_indices = compute_skyline(points)
    skyline_pts = points[skyline_indices]
    skyline_movies = filtered_df.iloc[skyline_indices]
    
    print(f"Skyline has {len(skyline_pts)} optimal points.")
    print("Skyline points (Budget, Popularity):")
    for i, pt in enumerate(skyline_pts):
        print(f"  Point {i+1}: Budget={pt[0]:.2f}, Popularity={pt[1]:.2f}")
    
    print("\nCorresponding Movie IDs:")
    for i, movie_id in enumerate(skyline_movies['id']):
        print(f"  Point {i+1}: ID={movie_id}")
    
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
