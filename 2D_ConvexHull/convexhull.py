import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull

def load_data():
    df = pd.read_excel('data_movies_clean.xlsx')
    filtered_df = df[(df['budget'] > 0) & (df['popularity'] > 0)].dropna()
    return filtered_df

if __name__ == "__main__":
    filtered_df = load_data()
    points = filtered_df[['budget', 'popularity']].values
    if points is not None:
        print(f"Calculating Convex Hull for {len(points)} points...")
        hull = ConvexHull(points)
        
        hull_vertices_indices = hull.vertices
        hull_pts = points[hull_vertices_indices]
        hull_movies = filtered_df.iloc[hull_vertices_indices]
        
        print(f"Convex Hull has {len(hull_pts)} vertices.")
        print("Convex Hull vertices (Budget, Popularity):")
        for i, pt in enumerate(hull_pts):
            print(f"  Vertex {i+1}: Budget={pt[0]:.2f}, Popularity={pt[1]:.2f}")
        
        print("\nCorresponding Movie IDs:")
        for i, movie_id in enumerate(hull_movies['id']):
            print(f"  Vertex {i+1}: ID={movie_id}")
        
        plt.figure(figsize=(10, 6))
        plt.scatter(points[:, 0], points[:, 1], s=1, color='gray', alpha=0.3, label='Movies Data')
        
        # design Convex Hull edges
        for simplex in hull.simplices:
            plt.plot(points[simplex, 0], points[simplex, 1], 'r-', linewidth=2)
            
        plt.plot(points[hull.vertices, 0], points[hull.vertices, 1], 'ro', label='CH Vertices')
        plt.xlabel('Budget (USD)')
        plt.ylabel('Popularity Score')
        plt.title('Convex Hull (CH(P1)) Calculation')
        plt.xscale('log')
        plt.legend()
        plt.show()
