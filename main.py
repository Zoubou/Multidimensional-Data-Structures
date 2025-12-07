import geopandas as gpd
import time

from interval_tree import Interval, IntervalTree


# -------------------------------------------------------------
# YOUR FUNCTION — UNCHANGED
# Converts each LineString → (min_x, max_x)
# -------------------------------------------------------------
def generate_intervals_from_segments(gdf):
    intervals = []
    
    for geometry in gdf['geometry']:
        if geometry is None:
            continue
        
        x_coords = [p[0] for p in geometry.coords]
        if not x_coords:
            continue

        min_x = min(x_coords)
        max_x = max(x_coords)

        if min_x < max_x:   # avoid degenerate intervals
            intervals.append((min_x, max_x))

    return intervals


# -------------------------------------------------------------
# MAIN EXECUTION
# -------------------------------------------------------------
def main():
    # Load your shapefile
    file_path = 'HydroRIVERS_v10_gr.shp'
    print("Loading shapefile...")
    rivers_gdf = gpd.read_file(file_path)

    print(f"Total river segments loaded: {len(rivers_gdf)}")

    # Convert to intervals
    interval_data = generate_intervals_from_segments(rivers_gdf)
    print(f"Total 1D intervals created: {len(interval_data)}")
    print("First 5 intervals:", interval_data[:5])

    # Convert tuples → Interval objects
    interval_objects = [Interval(a, b) for (a, b) in interval_data]

    print("\nBuilding Interval Tree...")
    start = time.time()
    tree = IntervalTree(interval_objects)
    end = time.time()
    print(f"Tree built in {end - start:.4f} seconds")

    # Example interval query
    query = Interval(-30.0, -20.0)
    print(f"\nQuerying overlap with: {query}")

    start = time.time()
    res = tree.interval_query(query)
    end = time.time()

    print(f"Found {len(res)} overlapping river segments")
    print("First 10 results:", res[:10])
    print(f"Query time: {end - start:.6f} seconds")

    #Testing Insertion

    print("\nTesting insertion...")

    new_interval = Interval(100.0, 150.0)
    tree.insert(new_interval)

    print("Inserted:", new_interval)

    # Now query around it to verify it exists
    test_query = Interval(120.0, 130.0)
    res2 = tree.interval_query(test_query)
    print("Query after insertion:", res2[:5])

    #Testing Deletion

    print("\nTesting deletion...")

    to_delete = Interval(-25.696, -25.631)
    tree.delete(to_delete)

    res_after_delete = tree.interval_query(Interval(-30, -20))
    print("Query after deletion:", res_after_delete[:5])
    print("After delete:", to_delete, "found?" , to_delete in res_after_delete)


if __name__ == "__main__":
    main()
