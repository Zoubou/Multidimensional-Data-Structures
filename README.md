# Multi-Dimensional Data Structures

This project focuses on the implementation and experimental evaluation of various **multi-dimensional and geometric data structures**. The primary objective is to validate that the **empirical performance** of these data structures aligns with their **theoretical time and space complexities**.

---

## Project Overview

The project explores data structures commonly used in computational geometry and spatial databases. Each component includes both implementation and experimental evaluation, with a focus on query performance and scalability.

---

## 1. 3D R-Trees

This module implements **3-dimensional R-Trees** for indexing **planar trajectories of moving objects**.

### Key Features

* Each data point is represented in **(x, y, t)** format:

  * `x`, `y`: spatial coordinates
  * `t`: time dimension
* Supports **spatio-temporal range queries**, such as:

  * Finding objects within a given spatial area
  * Restricting results to a specific time interval

### Purpose

* Efficient indexing of moving objects
* Experimental validation of expected R-Tree performance characteristics

---

## 2. Interval Trees and Segment Trees

This component implements and evaluates **Interval Trees** and **Segment Trees**.

### Supported Operations

* Interval insertion and deletion
* Interval queries
* Stabbing queries

### Evaluation Goals

* Measure query response times
* Demonstrate that experimental performance follows the theoretical
  **O(log n)** time complexity

---

## 3. 2D Convex Hull and Skyline Operator

This module performs geometric analysis using the **Movies Metadata dataset**.

### Data Representation

* Each movie is modeled as a 2D point:

  * **(budget, popularity)**

### Convex Hull

* Computes the **Convex Hull (CH(P₁))** of the 2D point set
* Identifies the boundary points enclosing all movies

### Skyline Operator

* Implements a skyline predicate to identify movies that:

  * Minimize **budget**
  * Maximize **popularity**
* Filters out dominated points

---

## 4. Line Segment Intersection

This module implements **Line Segment Intersection** detection algorithms using the **Sweep Line Technique**.

### Features

* Efficient detection of all intersecting line segment pairs
* Utilizes event queues and balanced search structures

### Evaluation

* Compares practical time and space usage against theoretical benchmarks
* Verifies expected performance for large input sizes

