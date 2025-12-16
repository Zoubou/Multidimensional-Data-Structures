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
    file_path = 'dataset/HydroRIVERS_v10_gr.shp'
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

        # ---------------------------------------------------------
    # TEST INSERT
    # ---------------------------------------------------------
    test_interval = Interval(-25.0, -10.0, "TEST_INTERVAL")
    print("\nInserting test interval:", test_interval)

    start = time.time()
    tree.insert(test_interval)
    end = time.time()
    print(f"Insert time: {end - start:.6f} seconds")

    # Query again to verify insert
    start = time.time()
    res_after_insert = tree.interval_query(query)
    end = time.time()

    print(f"After insert: {len(res_after_insert)} intervals")
    print("Test interval present:", test_interval in res_after_insert)
    print("Only test interval:",
      [iv for iv in res_after_insert if iv == test_interval])
    print(f"Query time: {end - start:.6f} seconds")

    # ---------------------------------------------------------
    # TEST DELETE
    # ---------------------------------------------------------
    print("\nDeleting test interval:", test_interval)

    start = time.time()
    tree.delete(test_interval)
    end = time.time()
    print(f"Delete time: {end - start:.6f} seconds")

    # Query again to verify delete
    start = time.time()
    res_after_delete = tree.interval_query(query)
    end = time.time()

    print(f"After delete: {len(res_after_delete)} intervals")
    print("Test interval present:", test_interval in res_after_delete)
    print("Only test interval:",
      [iv for iv in res_after_delete if iv == test_interval])
    print(f"Query time: {end - start:.6f} seconds")



if __name__ == "__main__":
    main()
