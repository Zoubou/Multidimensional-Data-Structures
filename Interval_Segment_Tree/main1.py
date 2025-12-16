import geopandas as gpd
import time

from segment_tree import SegmentTree   # your segment tree implementation


# -------------------------------------------------------------
# Create 1D intervals from each LineString (min_x, max_x)
# -------------------------------------------------------------
def generate_intervals_from_segments(gdf):
    intervals = []

    for idx, geometry in enumerate(gdf["geometry"]):
        if geometry is None:
            continue
        
        # Extract all x-coordinates from LineString
        x_coords = [p[0] for p in geometry.coords]
        if not x_coords:
            continue
        
        low = min(x_coords)
        high = max(x_coords)

        if low < high:
            intervals.append((low, high, idx))  # interval + river ID

    return intervals


# -------------------------------------------------------------
# MAIN EXECUTION
# -------------------------------------------------------------
def main():
    file_path = "dataset/HydroRIVERS_v10_gr.shp"
    print("Loading shapefile...")
    rivers_gdf = gpd.read_file(file_path)

    print(f"Total river segments loaded: {len(rivers_gdf)}")

    # Convert each LineString into 1D interval
    intervals = generate_intervals_from_segments(rivers_gdf)
    print(f"Total intervals created: {len(intervals)}")
    print("First 5 intervals:", intervals[:5])

    # Compute global bounding range
    all_low = min(iv[0] for iv in intervals)
    all_high = max(iv[1] for iv in intervals)
    print("X-range:", all_low, "to", all_high)

    print("\nBuilding Segment Tree...")
    start = time.time()
    tree = SegmentTree(intervals)
    end = time.time()
    print(f"Segment Tree built in {end - start:.4f} seconds")

    # ---------------------------------------------------------
    # Perform a stabbing query:
    # “Which river intervals contain x = some_value?”
    # ---------------------------------------------------------
    query_x = -20.0
    print(f"\nStabbing query at x = {query_x}")

    start = time.time()
    result = tree.stabbing_query(query_x)
    end = time.time()

    print(f"Found {len(result)} river intervals covering x = {query_x}")
    print("First 10 results:", result[:10])
    print(f"Query time: {end - start:.6f} seconds")


if __name__ == "__main__":
    main()
