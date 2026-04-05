# Virtual Memory Management Simulator

A Python-based GUI application for visualizing and simulating virtual memory management techniques including paging, segmentation, and algorithm comparison.

## Features

- **Paging & Demand Paging Tab**
  - LRU (Least Recently Used) page replacement algorithm
  - Optimal page replacement algorithm
  - Visual table showing frame states at each step
  - Real-time page fault graph with cumulative fault tracking

- **Segmentation & Fragmentation Tab**
  - Add multiple memory segments with custom names and sizes
  - Visual memory allocation diagram
  - External fragmentation calculation and display
  - Support for custom total memory size (default 512 KB)

- **Algorithm Comparison Tab**
  - Side-by-side comparison of LRU vs Optimal
  - Performance metrics: Total Faults, Hit Ratio, Efficiency
  - Bar chart visualization comparing page faults
  - Step-by-step execution table for both algorithms

## How to Run

### Browser Version (Recommended)
Simply open `index.html` in any web browser - no installation required!

### Python Version
Requires Python with tkinter and matplotlib:

### Installation (Python version)

```bash
pip install matplotlib
```

### Running the Python Application

```bash
python virtual_memory_sim.py
```

## Screenshots

The application features a modern dark-themed UI with:
- Tab-based navigation for different simulation modes
- Animated buttons with hover effects
- Real-time visualization using Matplotlib
- Scrollable results tables
- Status bar showing last action performed

## Technologies Used

- **HTML/CSS/JS** - Main web-based version (runs in browser)
- **Python** - Alternative desktop version (Tkinter)
- **Matplotlib** - Graph visualization (Python version)
- **Canvas API** - Graph visualization (HTML version)

## Git Commit Log Summary

- **Day 7**: Final polish - Added input validation, reset/clear buttons, status bar, and algorithm info panels
- **Day 6**: Rebuilt UI with HTML/CSS/JS, enhanced graphs with gradients and comparison tab
- **Day 5**: Added Segmentation & Fragmentation tab with memory allocation simulation and visualization
- **Day 4**: Added scrollable results table, styled scrollbar, improved layout and UI fixes
- **Day 3**: Added Optimal page replacement algorithm with algorithm selection dropdown
- **Day 2**: Implemented LRU page replacement algorithm with Treeview visualization
- **Day 1**: Initial skeleton with modern UI for Virtual Memory Management Simulator

## Input Validation

The application includes comprehensive input validation:
- Page reference strings must be space-separated integers
- Number of frames must be a positive integer (at least 1)
- Segment names cannot be empty
- Segment sizes must be positive integers

## Usage Tips

1. **Paging Tab**: Enter a page reference string (e.g., `7 0 1 2 0 3 0 4 2 3`) and the number of frames to simulate page replacement.

2. **Segmentation Tab**: Add segments with names (Code, Data, Stack) and sizes in KB to see how they are allocated in memory.

3. **Comparison Tab**: Compare LRU and Optimal algorithms side-by-side to understand the difference between practical and optimal solutions.

## License

MIT License
