import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull

def load_data():
    df = pd.read_excel('data_movies_clean.xlsx')
    data = df[(df['budget'] > 0) & (df['popularity'] > 0)][['budget', 'popularity']]
    return data.dropna().values

if __name__ == "__main__":
    points = load_data()
    if points is not None:
        print(f"Calculating Convex Hull for {len(points)} points...")
        hull = ConvexHull(points)
        
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
