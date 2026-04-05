"""
Virtual Memory Management Simulator
A Tkinter-based GUI application for visualizing and simulating
virtual memory management techniques.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
from collections import OrderedDict
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt


def simulate_lru(pages, num_frames):
    """
    Simulate LRU page replacement algorithm.
    
    Args:
        pages: List of page numbers (integers)
        num_frames: Number of memory frames
        
    Returns:
        tuple: (frame_snapshots, fault_flags, total_faults)
            - frame_snapshots: list of lists showing frame contents at each step
            - fault_flags: list of booleans (True = page fault, False = hit)
            - total_faults: total count of page faults
    """
    frames = []
    frame_snapshots = []
    fault_flags = []
    total_faults = 0
    recent_use = OrderedDict()
    
    for page in pages:
        if page in frames:
            fault_flags.append(False)
            recent_use.move_to_end(page)
        else:
            total_faults += 1
            fault_flags.append(True)
            
            if len(frames) < num_frames:
                frames.append(page)
            else:
                lru_page = next(iter(recent_use))
                idx = frames.index(lru_page)
                frames[idx] = page
                del recent_use[lru_page]
            
            recent_use[page] = True
        
        frame_snapshots.append(frames.copy())
    
    return frame_snapshots, fault_flags, total_faults


def simulate_optimal(pages, num_frames):
    """
    Simulate Optimal page replacement algorithm.
    
    Args:
        pages: List of page numbers (integers)
        num_frames: Number of memory frames
        
    Returns:
        tuple: (frame_snapshots, fault_flags, total_faults)
            - frame_snapshots: list of lists showing frame contents at each step
            - fault_flags: list of booleans (True = page fault, False = hit)
            - total_faults: total count of page faults
    """
    frames = []
    frame_snapshots = []
    fault_flags = []
    total_faults = 0
    
    for i, page in enumerate(pages):
        if page in frames:
            fault_flags.append(False)
        else:
            total_faults += 1
            fault_flags.append(True)
            
            if len(frames) < num_frames:
                frames.append(page)
            else:
                future_refs = pages[i + 1:]
                replace_idx = 0
                max_distance = -1
                
                for j, frame_page in enumerate(frames):
                    try:
                        distance = future_refs.index(frame_page)
                    except ValueError:
                        distance = len(future_refs) + 1
                    
                    if distance > max_distance:
                        max_distance = distance
                        replace_idx = j
                
                frames[replace_idx] = page
        
        frame_snapshots.append(frames.copy())
    
    return frame_snapshots, fault_flags, total_faults


ALGORITHMS = {
    "LRU": simulate_lru,
    "Optimal": simulate_optimal
}


def simulate_segmentation(segments, total_memory=512):
    """
    Simulate segmentation memory allocation.
    
    Args:
        segments: List of (name, size) tuples where size is in KB
        total_memory: Total memory size in KB (default 512 KB)
        
    Returns:
        tuple: (allocations, stats)
            - allocations: list of dicts with segment info and allocation status
            - stats: dict with used_memory, free_memory, external_fragmentation
    """
    allocations = []
    current_address = 0
    
    for name, size in segments:
        if current_address + size <= total_memory:
            allocation = {
                'name': name,
                'size': size,
                'base_address': current_address,
                'end_address': current_address + size,
                'status': 'Allocated'
            }
            current_address += size
        else:
            allocation = {
                'name': name,
                'size': size,
                'base_address': '-',
                'end_address': '-',
                'status': 'Allocation Failed'
            }
        allocations.append(allocation)
    
    used_memory = sum(a['size'] for a in allocations if a['status'] == 'Allocated')
    free_memory = total_memory - used_memory
    external_fragmentation = free_memory
    
    stats = {
        'total_memory': total_memory,
        'used_memory': used_memory,
        'free_memory': free_memory,
        'external_fragmentation': external_fragmentation
    }
    
    return allocations, stats


def parse_page_reference(page_str):
    """Parse page reference string into list of integers."""
    try:
        pages = [int(p.strip()) for p in page_str.replace(',', ' ').split() if p.strip()]
        return pages
    except ValueError:
        return None


class AnimatedButton(tk.Canvas):
    """Animated button with smooth hover and click effects."""

    def __init__(self, parent, text="", command=None, width=200, height=48, **kwargs):
        super().__init__(parent, width=width, height=height)
        self.command = command
        self._text = text
        self.base_bg = "#1a6bff"
        self.hover_bg = "#3388ff"
        self.active_bg = "#0055dd"
        self.text_color = "white"
        self.corner_radius = 10
        self.current_bg = self.base_bg
        self.hovered = False
        self.clicked = False

        self.configure(highlightthickness=0, bg="#0f172a", cursor="hand2")
        self._text_id = None
        self._draw_button()

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)

        self.bind("<Configure>", lambda e: self._draw_button())

    def _draw_button(self):
        """Draw the rounded rectangle and text."""
        self.delete("all")
        w = max(self.winfo_width(), 200)
        h = max(self.winfo_height(), 48)
        self.create_rounded_rect(2, 2, w - 2, h - 2, self.corner_radius, fill=self.current_bg, outline="")
        self._text_id = self.create_text(w // 2, h // 2, text=self._text, fill=self.text_color, font=("Segoe UI", 12, "bold"))

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = []
        r = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)
        points = [x1 + r, y1, x2 - r, y1, x2, y1 + r, x2, y2 - r, x2 - r, y2, x1 + r, y2, x1, y2 - r, x1, y1 + r]
        return self.create_polygon(points, smooth=True, joinstyle=tk.ROUND, **kwargs)

    def _on_enter(self, event):
        self.hovered = True
        self.current_bg = self.hover_bg
        self._draw_button()

    def _on_leave(self, event):
        self.hovered = False
        self.current_bg = self.base_bg
        self._draw_button()

    def _on_click(self, event):
        self.clicked = True
        self.current_bg = self.active_bg
        self._draw_button()

    def _on_release(self, event):
        self.clicked = False
        if self.hovered:
            self.current_bg = self.hover_bg
        else:
            self.current_bg = self.base_bg
        self._draw_button()
        if self.command:
            self.command()


class ModernEntry(tk.Frame):
    """Modern styled entry with animated focus border and placeholder text."""

    def __init__(self, parent, placeholder="", width=40, **kwargs):
        super().__init__(parent, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = "#6e7681"
        self.text_color = "#ffffff"
        self.border_color = "#374151"
        self.focus_color = "#1a6bff"
        self.current_border_color = self.border_color
        self._has_focus = False
        self._has_value = False

        self.configure(bg="#1f2937", highlightthickness=2, highlightcolor=self.border_color, highlightbackground=self.border_color)

        self.entry = tk.Entry(
            self,
            font=("Segoe UI", 11),
            bg="#1f2937",
            fg=self.placeholder_color,
            insertbackground=self.text_color,
            relief=tk.FLAT,
            bd=0,
            width=width
        )
        self.entry.pack(fill="x", padx=12, pady=10)
        self.entry.insert(0, self.placeholder)

        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<Key>", self._on_key)

        self.after(100, self._update_border)

    def _update_border(self):
        """Update the border color."""
        self.configure(highlightbackground=self.current_border_color, highlightcolor=self.current_border_color)

    def _on_focus_in(self, event):
        self._has_focus = True
        self.current_border_color = self.focus_color
        self._update_border()
        if not self._has_value:
            self.entry.delete(0, tk.END)
            self.entry.configure(fg=self.text_color)

    def _on_focus_out(self, event):
        self._has_focus = False
        self.current_border_color = self.border_color
        self._update_border()
        value = self.entry.get()
        if value == "":
            self.entry.insert(0, self.placeholder)
            self.entry.configure(fg=self.placeholder_color)
            self._has_value = False
        else:
            self._has_value = True

    def _on_key(self, event):
        value = self.entry.get()
        if not self._has_value and not self._has_focus:
            self.entry.delete(0, tk.END)
            self.entry.configure(fg=self.text_color)
        if value and value != self.placeholder:
            self._has_value = True
        elif value == "":
            self._has_value = False

    def get(self):
        value = self.entry.get()
        return value if value != self.placeholder else ""

    def insert(self, index, text):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)
        self.entry.configure(fg=self.text_color)
        self._has_value = True


class ModernDropdown(tk.Frame):
    """Modern styled dropdown/combobox."""

    def __init__(self, parent, values=None, width=40, **kwargs):
        super().__init__(parent, **kwargs)
        self.values = values or ["Option 1", "Option 2"]
        self.selected_value = tk.StringVar(value=self.values[0])

        self.configure(bg="#1f2937", highlightthickness=2, highlightbackground="#374151", highlightcolor="#374151")

        self.dropdown = ttk.Combobox(
            self,
            textvariable=self.selected_value,
            values=self.values,
            state="readonly",
            width=width - 2,
            font=("Inter", 11)
        )
        self.dropdown.pack(fill="x", padx=12, pady=10)

        self._style_dropdown()

    def _style_dropdown(self):
        """Style the ttk combobox."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Modern.TCombobox",
                       fieldbackground="#1f2937",
                       background="#1f2937",
                       foreground="#ffffff",
                       borderwidth=0,
                       padding=0,
                       arrowsize=14)
        style.configure("Modern.Treeview",
                       background="#1f2937",
                       fieldbackground="#1f2937",
                       foreground="#ffffff")
        style.map("Modern.TCombobox",
                 fieldbackground=[("readonly", "#1f2937")],
                 foreground=[("readonly", "#ffffff")])
        self.dropdown.configure(style="Modern.TCombobox")
        self.dropdown.current(0)

    def get(self):
        return self.selected_value.get()


class ModernCard(tk.Frame):
    """Modern card widget with subtle shadow effect."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(
            bg="#1f2937",
            highlightthickness=0
        )


class VirtualMemoryApp:
    """Main application class for the Virtual Memory Management Simulator."""

    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Memory Management Simulator")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        self.root.configure(bg="#0f172a")

        self.bg_gradient = ["#0f172a", "#1e293b"]
        self.accent_blue = "#3b82f6"
        self.accent_purple = "#8b5cf6"
        self.text_primary = "#f1f5f9"
        self.text_secondary = "#94a3b8"
        self.card_bg = "#1e293b"
        self.card_border = "#334155"

        self.last_action = "Application started"
        
        self._create_ui()
        self._update_status_bar()

    def _create_ui(self):
        """Create the main UI structure."""
        self._create_header()
        self._create_main_content()

    def _create_header(self):
        """Create a modern gradient header."""
        header = tk.Frame(self.root, bg="#0f172a", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        title_container = tk.Frame(header, bg="#0f172a")
        title_container.pack(fill="both", expand=True, padx=30, pady=15)

        title = tk.Label(
            title_container,
            text="Virtual Memory Simulator",
            font=("Inter", 24, "bold"),
            bg="#0f172a",
            fg=self.text_primary
        )
        title.pack(side="left")

        subtitle = tk.Label(
            title_container,
            text="Day 5: Added Segmentation & Fragmentation tab with memory allocation simulation and visualization",
            font=("Inter", 12),
            bg="#0f172a",
            fg=self.text_secondary
        )
        subtitle.pack(side="left", padx=(15, 0), pady=(5, 0))

        badge = tk.Label(
            title_container,
            text="v1.0",
            font=("Inter", 9, "bold"),
            bg="#3b82f6",
            fg="white",
            padx=8,
            pady=2
        )
        badge.pack(side="left", padx=(15, 0), pady=(3, 0))

    def _create_main_content(self):
        """Create the main content area with tabs."""
        main_frame = tk.Frame(self.root, bg="#0f172a")
        main_frame.pack(fill="both", expand=True, padx=25, pady=(0, 25))

        tab_buttons_frame = tk.Frame(main_frame, bg="#0f172a")
        tab_buttons_frame.pack(fill="x", pady=(0, 20))

        self.tab_buttons = []
        self.active_tab = 0
        tab_names = ["Paging & Demand Paging", "Segmentation & Fragmentation", "LRU vs Optimal Comparison"]
        tab_icons = ["📄", "🧩", "⚡"]

        for i, (name, icon) in enumerate(zip(tab_names, tab_icons)):
            btn = self._create_tab_button(tab_buttons_frame, name, icon, i)
            self.tab_buttons.append(btn)
            btn["frame"].pack(side="left", padx=(0, 8))

        self.content_frame = tk.Frame(main_frame, bg="#0f172a")
        self.content_frame.pack(fill="both", expand=True)

        self.tab_contents = []
        self._create_paging_tab()
        self._create_segmentation_tab()
        self._create_comparison_tab()

        self._show_tab(0)
        self._create_status_bar()

    def _create_status_bar(self):
        """Create a status bar at the bottom of the window."""
        self.status_bar = tk.Frame(self.root, bg="#1e293b", height=30)
        self.status_bar.pack(fill="x", side="bottom")
        
        self.status_label = tk.Label(
            self.status_bar,
            text=self.last_action,
            font=("Inter", 10),
            bg="#1e293b",
            fg=self.text_secondary,
            anchor="w",
            padx=15
        )
        self.status_label.pack(side="left", fill="x", expand=True)

    def _update_status_bar(self, message=None):
        """Update the status bar with a new message."""
        if message:
            self.last_action = message
        self.status_label.configure(text=self.last_action)

    def _create_tab_button(self, parent, text, icon, index):
        """Create a modern tab button with hover effects."""
        btn_frame = tk.Frame(parent, bg="#1e293b", cursor="hand2")

        label = tk.Label(
            btn_frame,
            text=f"{icon}  {text}",
            font=("Inter", 12),
            bg="#1e293b",
            fg=self.text_secondary,
            padx=20,
            pady=12
        )
        label.pack(fill="both")
        label.bind("<Button-1>", lambda e, i=index: self._on_tab_click(i))
        btn_frame.bind("<Button-1>", lambda e, i=index: self._on_tab_click(i))

        def on_enter(e):
            if self.active_tab != index:
                btn_frame.configure(bg="#334155")
                label.configure(bg="#334155", fg=self.text_primary)

        def on_leave(e):
            if self.active_tab != index:
                btn_frame.configure(bg="#1e293b")
                label.configure(bg="#1e293b", fg=self.text_secondary)

        btn_frame.bind("<Enter>", on_enter)
        btn_frame.bind("<Leave>", on_leave)
        label.bind("<Enter>", on_enter)
        label.bind("<Leave>", on_leave)

        return {"frame": btn_frame, "label": label, "index": index}

    def _on_tab_click(self, index):
        """Handle tab click."""
        self._show_tab(index)

    def _show_tab(self, index):
        """Show the selected tab."""
        btn = self.tab_buttons[self.active_tab]
        btn["frame"].configure(bg="#1e293b")
        btn["label"].configure(bg="#1e293b", fg=self.text_secondary)

        self.active_tab = index
        btn = self.tab_buttons[index]
        btn["frame"].configure(bg="#3b82f6")
        btn["label"].configure(bg="#3b82f6", fg="white")

        for i, content in enumerate(self.tab_contents):
            if i == index:
                content.pack(fill="both", expand=True)
            else:
                content.pack_forget()

    def _create_paging_tab(self):
        """Create the Paging tab content."""
        content = tk.Frame(self.content_frame, bg="#0f172a")
        self.tab_contents.append(content)

        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=0)
        content.grid_columnconfigure(1, weight=1)

        left_panel = tk.Frame(content, bg="#0f172a")
        left_panel.grid(row=0, column=0, sticky="ns", padx=(0, 20))

        self._create_input_card(left_panel)
        self._create_run_button(left_panel)

        right_panel = tk.Frame(content, bg="#0f172a")
        right_panel.grid(row=0, column=1, sticky="nsew")

        scroll_canvas = tk.Canvas(right_panel, bg="#0f172a", highlightthickness=0, width=600)
        scroll_canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(right_panel, orient="vertical", command=scroll_canvas.yview)
        scrollbar.configure(bg="#334155", activebackground="#475569", troughcolor="#1e293b", bd=0, highlightthickness=0)
        scrollbar.grid(row=0, column=1, sticky="ns")

        scroll_canvas.configure(yscrollcommand=scrollbar.set)

        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        vis_container = tk.Frame(scroll_canvas, bg="#0f172a")
        vis_container_id = scroll_canvas.create_window((0, 0), window=vis_container, anchor="nw")

        def on_configure(event):
            scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
            scroll_canvas.itemconfig(vis_container_id, width=scroll_canvas.winfo_width())

        scroll_canvas.bind('<Configure>', on_configure)
        scroll_canvas.bind('<MouseWheel>', lambda e: scroll_canvas.yview_scroll(-1*(e.delta//120), "units"))

        self.vis_container = vis_container
        self.scroll_canvas = scroll_canvas
        self._create_output_area(vis_container)
        self._create_fault_graph(vis_container)

    def _create_input_card(self, parent):
        """Create input form card."""
        card = ModernCard(parent)
        card.pack(fill="x", pady=(0, 15))

        card_header = tk.Frame(card, bg="#1e293b")
        card_header.pack(fill="x", padx=20, pady=(15, 10))

        tk.Label(
            card_header,
            text="Configuration",
            font=("Inter", 14, "bold"),
            bg="#1e293b",
            fg=self.text_primary
        ).pack(side="left")

        tk.Label(
            card_header,
            text="●",
            font=("Inter", 10),
            bg="#1e293b",
            fg="#22c55e"
        ).pack(side="right")

        input_container = tk.Frame(card, bg="#1e293b")
        input_container.pack(fill="x", padx=20, pady=(0, 15))

        tk.Label(
            input_container,
            text="Page Reference String",
            font=("Inter", 10, "bold"),
            bg="#1e293b",
            fg=self.text_secondary
        ).grid(row=0, column=0, sticky="w", pady=(10, 5))

        self.page_ref_entry = ModernEntry(input_container, placeholder="e.g. 7 0 1 2 0 3 0 4 2 3", width=45)
        self.page_ref_entry.grid(row=1, column=0, sticky="ew", pady=(0, 15), columnspan=2)

        tk.Label(
            input_container,
            text="Number of Frames",
            font=("Inter", 10, "bold"),
            bg="#1e293b",
            fg=self.text_secondary
        ).grid(row=2, column=0, sticky="w", pady=(0, 5))

        self.frames_entry = ModernEntry(input_container, placeholder="e.g. 3", width=45)
        self.frames_entry.grid(row=3, column=0, sticky="ew", pady=(0, 15), columnspan=2)

        tk.Label(
            input_container,
            text="Algorithm",
            font=("Inter", 10, "bold"),
            bg="#1e293b",
            fg=self.text_secondary
        ).grid(row=4, column=0, sticky="w", pady=(0, 5))

        self.algorithm_dropdown = ModernDropdown(input_container, values=["LRU", "Optimal"], width=45)
        self.algorithm_dropdown.grid(row=5, column=0, sticky="ew", pady=(0, 10), columnspan=2)

        info_label = tk.Label(
            input_container,
            text="LRU: Replaces least recently used page\nOptimal: Replaces page used farthest in future",
            font=("Inter", 8),
            bg="#1e293b",
            fg="#64748b",
            justify="left"
        )
        info_label.grid(row=6, column=0, sticky="w", columnspan=2)

        input_container.columnconfigure(0, weight=1)

    def _create_run_button(self, parent):
        """Create the run simulation button."""
        btn_frame = tk.Frame(parent, bg="#0f172a")
        btn_frame.pack(fill="x", pady=(5, 0))

        self.run_button = AnimatedButton(
            btn_frame,
            text="▶  Run Simulation",
            command=self._on_run_clicked,
            width=200,
            height=48
        )
        self.run_button.pack(side="left")

        tk.Label(
            btn_frame,
            text="or press Enter",
            font=("Inter", 9),
            bg="#0f172a",
            fg=self.text_secondary
        ).pack(side="left", padx=(12, 0), pady=(0, 0))

        reset_btn = tk.Frame(parent, bg="#0f172a")
        reset_btn.pack(fill="x", pady=(10, 0))
        
        self.reset_button = AnimatedButton(
            reset_btn,
            text="↺  Reset / Clear",
            command=self._on_reset_paging,
            width=200,
            height=40
        )
        self.reset_button.pack(side="left")

        self.root.bind("<Return>", lambda e: self._on_run_clicked())

    def _create_output_area(self, parent):
        """Create the output visualization area with table."""
        parent.grid_rowconfigure(0, weight=0)
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        table_section = ModernCard(parent)
        table_section.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        card_header = tk.Frame(table_section, bg="#1e293b")
        card_header.pack(fill="x", padx=20, pady=(15, 10))

        tk.Label(
            card_header,
            text="Results Table",
            font=("Inter", 14, "bold"),
            bg="#1e293b",
            fg=self.text_primary
        ).pack(side="left")

        stats_frame = tk.Frame(card_header, bg="#1e293b")
        stats_frame.pack(side="right")

        self.page_faults_label = tk.Label(
            stats_frame,
            text="Faults: --",
            font=("Inter", 10, "bold"),
            bg="#1e293b",
            fg="#ef4444",
            padx=8
        )
        self.page_faults_label.pack(side="left", padx=(0, 8))

        self.hit_ratio_label = tk.Label(
            stats_frame,
            text="Hit: --",
            font=("Inter", 10, "bold"),
            bg="#1e293b",
            fg="#22c55e"
        )
        self.hit_ratio_label.pack(side="left")

        table_container = tk.Frame(table_section, bg="#1e293b")
        table_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.table_placeholder = tk.Label(
            table_container,
            text="Run a simulation to see results",
            font=("Inter", 12),
            bg="#1e293b",
            fg="#64748b",
            pady=40
        )
        self.table_placeholder.pack(fill="both", expand=True)

        table_inner = tk.Frame(table_container, bg="#1e293b")
        table_inner.pack(fill="both", expand=True)
        table_inner.pack_forget()

        scrollbar_y = ttk.Scrollbar(table_inner, orient="vertical")
        scrollbar_y.pack(side="right", fill="y")

        scrollbar_x = ttk.Scrollbar(table_inner, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")

        self.result_tree = ttk.Treeview(table_inner, show="headings", style="Modern.Treeview",
                                        yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        scrollbar_y.configure(command=self.result_tree.yview)
        scrollbar_x.configure(command=self.result_tree.xview)

        self.result_tree.pack(side="left", fill="both", expand=True)

        self.result_tree.tag_configure("fault", background="#7f1d1d", foreground="white")
        self.result_tree.tag_configure("hit", background="#14532d", foreground="white")

        self._style_treeview()

        self.table_container = table_container
        self.table_inner = table_inner

        summary_container = tk.Frame(table_section, bg="#1e293b")
        summary_container.pack(fill="x", padx=20, pady=(0, 15))

        self.summary_label = tk.Label(
            summary_container,
            text="Total References: --  |  Total Faults: --  |  Hit Ratio: --",
            font=("Inter", 11, "bold"),
            bg="#1e293b",
            fg=self.accent_blue,
            padx=10,
            pady=10
        )
        self.summary_label.pack(side="left")

    def _style_treeview(self):
        """Style the Treeview widget."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Modern.Treeview",
                        background="#1f2937",
                        fieldbackground="#1f2937",
                        foreground="#e5e7eb",
                        rowheight=28,
                        borderwidth=0)
        style.configure("Modern.Treeview.Heading",
                        background="#374151",
                        fieldbackground="#374151",
                        foreground="#f1f5f9",
                        font=("Inter", 10, "bold"),
                        borderwidth=0)
        style.map("Modern.Treeview", background=[("selected", "#3b82f6")])

    def _create_segmentation_tab(self):
        """Create the Segmentation tab content with scrollable canvas."""
        content = tk.Frame(self.content_frame, bg="#0f172a")
        self.tab_contents.append(content)

        scroll_canvas = tk.Canvas(content, bg="#0f172a", highlightthickness=0)
        scrollbar = tk.Scrollbar(content, orient="vertical", command=scroll_canvas.yview)
        scrollbar.configure(bg="#334155", activebackground="#475569", troughcolor="#1e293b", bd=0, highlightthickness=0)
        scroll_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        scroll_canvas.pack(side="left", fill="both", expand=True)

        inner_frame = tk.Frame(scroll_canvas, bg="#0f172a")
        inner_window = scroll_canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        def on_configure(event):
            scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
            scroll_canvas.itemconfig(inner_window, width=scroll_canvas.winfo_width())

        scroll_canvas.bind('<Configure>', on_configure)
        scroll_canvas.bind('<MouseWheel>', lambda e: scroll_canvas.yview_scroll(-1*(e.delta//120), "units"))

        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)

        inner_frame.grid_rowconfigure(0, weight=0)
        inner_frame.grid_rowconfigure(1, weight=0)
        inner_frame.grid_columnconfigure(0, weight=0, minsize=350)
        inner_frame.grid_columnconfigure(1, weight=1)

        left_panel = tk.Frame(inner_frame, bg="#0f172a")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 20), pady=(0, 15))

        self._create_segment_input_card(left_panel)

        right_panel = tk.Frame(inner_frame, bg="#0f172a")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 0), pady=(0, 15))

        self._create_segment_results_card(right_panel)

        bottom_panel = tk.Frame(inner_frame, bg="#0f172a")
        bottom_panel.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=(0, 0), pady=(0, 15))

        self._create_segment_memory_diagram(bottom_panel)

    def _create_segment_input_card(self, parent):
        """Create input form card for segmentation."""
        card = ModernCard(parent)
        card.pack(fill="both", expand=True, pady=(0, 15))

        card_header = tk.Frame(card, bg="#1e293b")
        card_header.pack(fill="x", padx=15, pady=(10, 5))

        tk.Label(
            card_header,
            text="Add Segments",
            font=("Inter", 12, "bold"),
            bg="#1e293b",
            fg=self.text_primary
        ).pack(side="left")

        tk.Label(
            card_header,
            text="●",
            font=("Inter", 9),
            bg="#1e293b",
            fg="#22c55e"
        ).pack(side="right")

        input_container = tk.Frame(card, bg="#1e293b")
        input_container.pack(fill="x", padx=15, pady=(0, 8))

        tk.Label(
            input_container,
            text="Segment Name",
            font=("Inter", 9, "bold"),
            bg="#1e293b",
            fg=self.text_secondary
        ).grid(row=0, column=0, sticky="w", pady=(5, 2))

        seg_name_frame = tk.Frame(input_container, bg="#1f2937", highlightthickness=1, highlightbackground="#374151")
        seg_name_frame.grid(row=1, column=0, sticky="ew", pady=(0, 6), columnspan=2)
        self.seg_name_entry = tk.Entry(seg_name_frame, font=("Segoe UI", 10), bg="#1f2937", fg="#6e7681",
                                        insertbackground="white", relief=tk.FLAT, bd=0, width=35)
        self.seg_name_entry.pack(fill="x", padx=10, pady=6)
        self.seg_name_entry.insert(0, "e.g. Code, Data, Stack")
        self.seg_name_entry.bind("<FocusIn>", lambda e, w=self.seg_name_entry, p="e.g. Code, Data, Stack": self._on_entry_focus_in(w, p))
        self.seg_name_entry.bind("<FocusOut>", lambda e, w=self.seg_name_entry, p="e.g. Code, Data, Stack": self._on_entry_focus_out(w, p))

        tk.Label(
            input_container,
            text="Segment Size (KB)",
            font=("Inter", 9, "bold"),
            bg="#1e293b",
            fg=self.text_secondary
        ).grid(row=2, column=0, sticky="w", pady=(0, 2))

        seg_size_frame = tk.Frame(input_container, bg="#1f2937", highlightthickness=1, highlightbackground="#374151")
        seg_size_frame.grid(row=3, column=0, sticky="ew", pady=(0, 6), columnspan=2)
        self.seg_size_entry = tk.Entry(seg_size_frame, font=("Segoe UI", 10), bg="#1f2937", fg="#6e7681",
                                        insertbackground="white", relief=tk.FLAT, bd=0, width=35)
        self.seg_size_entry.pack(fill="x", padx=10, pady=6)
        self.seg_size_entry.insert(0, "e.g. 100")
        self.seg_size_entry.bind("<FocusIn>", lambda e, w=self.seg_size_entry, p="e.g. 100": self._on_entry_focus_in(w, p))
        self.seg_size_entry.bind("<FocusOut>", lambda e, w=self.seg_size_entry, p="e.g. 100": self._on_entry_focus_out(w, p))

        tk.Label(
            input_container,
            text="Total Memory (KB)",
            font=("Inter", 9, "bold"),
            bg="#1e293b",
            fg=self.text_secondary
        ).grid(row=4, column=0, sticky="w", pady=(0, 2))

        total_mem_frame = tk.Frame(input_container, bg="#1f2937", highlightthickness=1, highlightbackground="#374151")
        total_mem_frame.grid(row=5, column=0, sticky="ew", pady=(0, 8), columnspan=2)
        self.total_mem_entry = tk.Entry(total_mem_frame, font=("Segoe UI", 10), bg="#1f2937", fg="#6e7681",
                                        insertbackground="white", relief=tk.FLAT, bd=0, width=35)
        self.total_mem_entry.pack(fill="x", padx=10, pady=6)
        self.total_mem_entry.insert(0, "e.g. 512")
        self.total_mem_entry.bind("<FocusIn>", lambda e, w=self.total_mem_entry, p="e.g. 512": self._on_entry_focus_in(w, p))
        self.total_mem_entry.bind("<FocusOut>", lambda e, w=self.total_mem_entry, p="e.g. 512": self._on_entry_focus_out(w, p))

        input_container.columnconfigure(0, weight=1)

        btn_container = tk.Frame(card, bg="#1e293b")
        btn_container.pack(fill="x", padx=15, pady=(0, 8))

        self.add_seg_button = AnimatedButton(
            btn_container,
            text="+ Add Segment",
            command=self._on_add_segment,
            width=140,
            height=36
        )
        self.add_seg_button.pack(fill="x", expand=True)

        self.run_seg_button = AnimatedButton(
            btn_container,
            text="Run Segmentation",
            command=self._on_run_segmentation,
            width=140,
            height=36
        )
        self.run_seg_button.pack(fill="x", expand=True, pady=(5, 0))

        self.clear_seg_button = AnimatedButton(
            btn_container,
            text="Clear All",
            command=self._on_clear_segments,
            width=140,
            height=36
        )
        self.clear_seg_button.pack(fill="x", expand=True, pady=(5, 0))

        list_card = tk.Frame(card, bg="#1e293b")
        list_card.pack(fill="x", padx=15, pady=(0, 10))

        list_header = tk.Frame(list_card, bg="#1f2937")
        list_header.pack(fill="x", padx=10, pady=(8, 3))

        tk.Label(
            list_header,
            text="Segments List",
            font=("Inter", 10, "bold"),
            bg="#1f2937",
            fg=self.text_primary
        ).pack(side="left")

        self.seg_count_label = tk.Label(
            list_header,
            text="0 segments",
            font=("Inter", 9),
            bg="#1f2937",
            fg=self.text_secondary
        )
        self.seg_count_label.pack(side="right")

        list_container = tk.Frame(list_card, bg="#1f2937")
        list_container.pack(fill="x", padx=10, pady=(0, 8))

        self.scrollbar_y = ttk.Scrollbar(list_container, orient="vertical")
        self.scrollbar_y.pack(side="right", fill="y")

        self.seg_listbox = tk.Listbox(
            list_container,
            font=("Inter", 10),
            bg="#1f2937",
            fg=self.text_primary,
            highlightthickness=0,
            bd=0,
            selectbackground="#3b82f6",
            selectforeground="white",
            activestyle="none",
            yscrollcommand=self.scrollbar_y.set,
            height=5
        )
        self.scrollbar_y.configure(command=self.seg_listbox.yview)
        self.seg_listbox.pack(side="left", fill="both", expand=True)
        self.scrollbar_y.pack_forget()

        info_label = tk.Label(
            list_card,
            text="External fragmentation: free memory that cannot\nbe used to satisfy a request due to being\nsplit into small non-contiguous blocks",
            font=("Inter", 8),
            bg="#1e293b",
            fg="#64748b",
            justify="left"
        )
        info_label.pack(fill="x", padx=10, pady=(0, 8))

        self.segments = []

    def _create_segment_results_card(self, parent):
        """Create results card for segmentation."""
        card = ModernCard(parent)
        card.pack(fill="both", expand=True)

        card_header = tk.Frame(card, bg="#1e293b")
        card_header.pack(fill="x", padx=20, pady=(15, 10))

        tk.Label(
            card_header,
            text="Allocation Results",
            font=("Inter", 14, "bold"),
            bg="#1e293b",
            fg=self.text_primary
        ).pack(side="left")

        self.seg_status_label = tk.Label(
            card_header,
            text="Add segments and run",
            font=("Inter", 10),
            bg="#1e293b",
            fg=self.text_secondary
        )
        self.seg_status_label.pack(side="right")

        stats_frame = tk.Frame(card, bg="#1e293b")
        stats_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.seg_used_label = tk.Label(
            stats_frame,
            text="Used: -- KB",
            font=("Inter", 11, "bold"),
            bg="#1e293b",
            fg="#22c55e",
            padx=12,
            pady=8
        )
        self.seg_used_label.pack(side="left", padx=(0, 8))

        self.seg_free_label = tk.Label(
            stats_frame,
            text="Free: -- KB",
            font=("Inter", 11, "bold"),
            bg="#1e293b",
            fg="#f59e0b",
            padx=12,
            pady=8
        )
        self.seg_free_label.pack(side="left", padx=(0, 8))

        self.seg_frag_label = tk.Label(
            stats_frame,
            text="Fragmentation: -- KB",
            font=("Inter", 11, "bold"),
            bg="#1e293b",
            fg="#ef4444",
            padx=12,
            pady=8
        )
        self.seg_frag_label.pack(side="left")

        table_container = tk.Frame(card, bg="#1e293b")
        table_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.seg_table_placeholder = tk.Label(
            table_container,
            text="Run segmentation to see allocation results",
            font=("Inter", 12),
            bg="#1e293b",
            fg="#64748b",
            pady=40
        )
        self.seg_table_placeholder.pack(fill="both", expand=True)

        seg_table_inner = tk.Frame(table_container, bg="#1e293b")
        seg_table_inner.pack(fill="both", expand=True)
        seg_table_inner.pack_forget()

        scrollbar_y = ttk.Scrollbar(seg_table_inner, orient="vertical")
        scrollbar_y.pack(side="right", fill="y")

        scrollbar_x = ttk.Scrollbar(seg_table_inner, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")

        self.seg_result_tree = ttk.Treeview(seg_table_inner, show="headings", style="Modern.Treeview",
                                            yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        scrollbar_y.configure(command=self.seg_result_tree.yview)
        scrollbar_x.configure(command=self.seg_result_tree.xview)

        self.seg_result_tree.pack(side="left", fill="both", expand=True)

        self.seg_result_tree.tag_configure("allocated", background="#14532d", foreground="white")
        self.seg_result_tree.tag_configure("failed", background="#7f1d1d", foreground="white")

        self.seg_table_container = table_container
        self.seg_table_inner = seg_table_inner

    def _create_segment_memory_diagram(self, parent):
        """Create the memory diagram card with Matplotlib."""
        card = ModernCard(parent)
        card.pack(fill="both", expand=True)

        card_header = tk.Frame(card, bg="#1e293b")
        card_header.pack(fill="x", padx=20, pady=(15, 10))

        tk.Label(
            card_header,
            text="Memory Visualization",
            font=("Inter", 12, "bold"),
            bg="#1e293b",
            fg=self.text_primary
        ).pack(side="left")

        self.seg_fig = Figure(figsize=(9, 3), dpi=100, facecolor='#161b22')
        self.seg_ax = self.seg_fig.add_subplot(111)
        self.seg_ax.set_facecolor('#161b22')

        graph_inner = tk.Frame(card, bg='#161b22')
        graph_inner.pack(fill="x", padx=15, pady=(0, 10))

        self.seg_canvas = FigureCanvasTkAgg(self.seg_fig, master=graph_inner)
        self.seg_canvas.get_tk_widget().configure(bg='#161b22')
        self.seg_canvas.get_tk_widget().pack(fill="x")

        self._update_segment_diagram([], 512)

    def _on_entry_focus_in(self, widget, placeholder):
        """Handle entry focus in - clear placeholder."""
        if widget.get() == placeholder:
            widget.delete(0, tk.END)
            widget.configure(fg="#ffffff")

    def _on_entry_focus_out(self, widget, placeholder):
        """Handle entry focus out - restore placeholder."""
        if widget.get() == "":
            widget.insert(0, placeholder)
            widget.configure(fg="#6e7681")

    def _on_add_segment(self):
        """Handle Add Segment button click."""
        name = self.seg_name_entry.get().strip()
        size_str = self.seg_size_entry.get().strip()

        if not name or name == "e.g. Code, Data, Stack":
            messagebox.showerror("Input Error", "Please enter a segment name.")
            return

        try:
            size = int(size_str)
            if size <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Segment size must be a positive integer.")
            return

        self.segments.append((name, size))
        self.seg_listbox.insert(tk.END, f"{name} ({size} KB)")
        self.seg_count_label.configure(text=f"{len(self.segments)} segments")
        self._update_seg_scrollbar()

        self._reset_entry(self.seg_name_entry, "e.g. Code, Data, Stack")
        self._reset_entry(self.seg_size_entry, "e.g. 100")
        self.seg_name_entry.focus()

    def _reset_entry(self, entry, placeholder):
        """Reset entry to placeholder style."""
        entry.delete(0, tk.END)
        entry.insert(0, placeholder)
        entry.configure(fg="#6e7681")

    def _update_seg_scrollbar(self):
        """Show or hide scrollbar based on list size."""
        if len(self.segments) > self.seg_listbox.cget('height'):
            self.scrollbar_y.pack(side="right", fill="y")
        else:
            self.scrollbar_y.pack_forget()

    def _on_clear_segments(self):
        """Handle Clear All button click."""
        self.segments = []
        self.seg_listbox.delete(0, tk.END)
        self.seg_count_label.configure(text="0 segments")
        self._update_seg_scrollbar()
        self.seg_status_label.configure(text="Add segments and run")
        self.seg_used_label.configure(text="Used: -- KB")
        self.seg_free_label.configure(text="Free: -- KB")
        self.seg_frag_label.configure(text="Fragmentation: -- KB")

        self.seg_table_placeholder.pack(fill="both", expand=True)
        self.seg_table_inner.pack_forget()

        self._update_segment_diagram([], 512)

    def _on_run_segmentation(self):
        """Handle Run Segmentation button click."""
        if not self.segments:
            messagebox.showerror("Input Error", "Please add at least one segment.")
            return

        total_mem_str = self.total_mem_entry.get().strip()
        if not total_mem_str or total_mem_str == "e.g. 512":
            total_mem = 512
        else:
            try:
                total_mem = int(total_mem_str)
                if total_mem <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Input Error", "Total memory must be a positive integer.")
                return

        allocations, stats = simulate_segmentation(self.segments, total_mem)

        self._display_segment_results(allocations, stats)
        self._update_segment_diagram(allocations, total_mem)

    def _display_segment_results(self, allocations, stats):
        """Display segmentation results in the Treeview table."""
        self.seg_table_placeholder.pack_forget()
        self.seg_table_inner.pack(fill="both", expand=True)

        for item in self.seg_result_tree.get_children():
            self.seg_result_tree.delete(item)

        columns = ["Segment", "Base Address", "Size (KB)", "End Address", "Status"]
        self.seg_result_tree["columns"] = columns
        self.seg_result_tree["show"] = "headings"

        for col in columns:
            self.seg_result_tree.heading(col, text=col)
            self.seg_result_tree.column(col, width=120, anchor="center")

        failed_count = 0
        for alloc in allocations:
            row_values = [
                alloc['name'],
                str(alloc['base_address']),
                str(alloc['size']),
                str(alloc['end_address']),
                alloc['status']
            ]
            tag = "failed" if alloc['status'] == 'Allocation Failed' else "allocated"
            self.seg_result_tree.insert("", "end", values=row_values, tags=(tag,))
            if alloc['status'] == 'Allocation Failed':
                failed_count += 1

        self.seg_used_label.configure(text=f"Used: {stats['used_memory']} KB")
        self.seg_free_label.configure(text=f"Free: {stats['free_memory']} KB")
        self.seg_frag_label.configure(text=f"Fragmentation: {stats['external_fragmentation']} KB")

        if failed_count > 0:
            self.seg_status_label.configure(text=f"{failed_count} failed", fg="#ef4444")
        else:
            self.seg_status_label.configure(text="All allocated", fg="#22c55e")

    def _update_segment_diagram(self, allocations, total_memory):
        """Update the memory visualization diagram."""
        self.seg_ax.clear()
        self.seg_ax.set_facecolor('#161b22')

        colors = ['#3b82f6', '#8b5cf6', '#22c55e', '#f59e0b', '#ef4444', 
                  '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#6366f1']
        
        if not allocations:
            self.seg_ax.text(0.5, 0.5, 'Add segments to visualize memory allocation', 
                            ha='center', va='center', transform=self.seg_ax.transAxes,
                            color='#64748b', fontsize=12, style='italic')
            self.seg_ax.set_xlim(0, 1)
            self.seg_ax.set_ylim(0, 1)
            self.seg_ax.axis('off')
            self.seg_ax.set_title('Memory Block Diagram', color='#9ca3af', fontsize=12, pad=10)
        else:
            blocks = []
            current_addr = 0
            color_idx = 0

            for alloc in allocations:
                if alloc['status'] == 'Allocated':
                    blocks.append({
                        'name': alloc['name'],
                        'start': current_addr,
                        'size': alloc['size'],
                        'color': colors[color_idx % len(colors)]
                    })
                    current_addr += alloc['size']
                    color_idx += 1

            free_start = current_addr
            free_size = total_memory - current_addr

            y_pos = 0.5
            bar_height = 0.6

            for i, block in enumerate(blocks):
                width = block['size']
                rect = Rectangle((block['start'], y_pos), width, bar_height,
                                 facecolor=block['color'], edgecolor='white',
                                 linewidth=1, alpha=0.9)
                self.seg_ax.add_patch(rect)
                
                if width >= 15:
                    self.seg_ax.text(block['start'] + width/2, y_pos + bar_height/2,
                                   f"{block['name']}\n{width} KB",
                                   ha='center', va='center', fontsize=9,
                                   color='white', fontweight='bold')
                elif width >= 5:
                    self.seg_ax.text(block['start'] + width/2, y_pos + bar_height/2,
                                   block['name'], ha='center', va='center',
                                   fontsize=8, color='white', fontweight='bold')

            if free_size > 0:
                rect = Rectangle((free_start, y_pos), free_size, bar_height,
                                     facecolor='#6b7280', edgecolor='white',
                                     linewidth=1, alpha=0.5, hatch='///')
                self.seg_ax.add_patch(rect)
                if free_size >= 15:
                    self.seg_ax.text(free_start + free_size/2, y_pos + bar_height/2,
                                   f"FREE\n{free_size} KB", ha='center', va='center',
                                   fontsize=9, color='#d1d5db', style='italic')

            self.seg_ax.set_xlim(-5, total_memory + 10)
            self.seg_ax.set_ylim(0, 1)
            self.seg_ax.axis('off')
            
            self.seg_ax.set_title('Memory Block Diagram', color='#9ca3af', fontsize=12, pad=10)
            
            for i in range(0, total_memory + 1, 64):
                self.seg_ax.axvline(x=i, color='#4b5563', linestyle='--', linewidth=0.5, alpha=0.5)
                self.seg_ax.text(i, y_pos - 0.15, str(i), ha='center', va='top',
                                fontsize=8, color='#9ca3af')

            self.seg_ax.text(total_memory + 5, y_pos + bar_height/2, f'{total_memory} KB',
                            ha='left', va='center', fontsize=8, color='#9ca3af')

        self.seg_fig.tight_layout(pad=2.0)
        self.seg_canvas.draw()

    def _create_comparison_tab(self):
        """Create the LRU vs Optimal comparison tab content."""
        content = tk.Frame(self.content_frame, bg="#0f172a")
        self.tab_contents.append(content)

        scroll_canvas = tk.Canvas(content, bg="#0f172a", highlightthickness=0)
        scrollbar = tk.Scrollbar(content, orient="vertical", command=scroll_canvas.yview)
        scrollbar.configure(bg="#334155", activebackground="#475569", troughcolor="#1e293b", bd=0, highlightthickness=0)
        scroll_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        scroll_canvas.pack(side="left", fill="both", expand=True)

        inner_frame = tk.Frame(scroll_canvas, bg="#0f172a")
        inner_window = scroll_canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        def on_configure(event):
            scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
            scroll_canvas.itemconfig(inner_window, width=scroll_canvas.winfo_width())

        scroll_canvas.bind('<Configure>', on_configure)
        scroll_canvas.bind('<MouseWheel>', lambda e: scroll_canvas.yview_scroll(-1*(e.delta//120), "units"))

        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)

        card = ModernCard(inner_frame)
        card.pack(fill="x", padx=20, pady=20)

        card_header = tk.Frame(card, bg="#1e293b")
        card_header.pack(fill="x", padx=25, pady=(20, 10))

        tk.Label(
            card_header,
            text="Algorithm Comparison",
            font=("Inter", 18, "bold"),
            bg="#1e293b",
            fg=self.text_primary
        ).pack(side="left")

        input_container = tk.Frame(card, bg="#1e293b")
        input_container.pack(fill="x", padx=25, pady=(10, 5))

        input_row1 = tk.Frame(input_container, bg="#1e293b")
        input_row1.pack(fill="x", pady=(0, 10))

        left_col = tk.Frame(input_row1, bg="#1e293b")
        left_col.pack(side="left", fill="x", expand=True, padx=(0, 15))

        tk.Label(
            left_col,
            text="Page Reference String",
            font=("Inter", 10, "bold"),
            bg="#1e293b",
            fg=self.text_secondary
        ).pack(anchor="w", pady=(0, 5))

        self.comp_page_ref_entry = ModernEntry(left_col, placeholder="e.g. 7 0 1 2 0 3 0 4 2 3 0 3", width=50)
        self.comp_page_ref_entry.pack(fill="x")

        right_col = tk.Frame(input_row1, bg="#1e293b")
        right_col.pack(side="left", fill="x", expand=True, padx=(0, 15))

        tk.Label(
            right_col,
            text="Number of Frames",
            font=("Inter", 10, "bold"),
            bg="#1e293b",
            fg=self.text_secondary
        ).pack(anchor="w", pady=(0, 5))

        self.comp_frames_entry = ModernEntry(right_col, placeholder="e.g. 3", width=25)
        self.comp_frames_entry.pack(fill="x")

        btn_col = tk.Frame(input_row1, bg="#1e293b")
        btn_col.pack(side="left", fill="both", padx=(15, 0))

        tk.Label(
            btn_col,
            text="",
            font=("Inter", 10),
            bg="#1e293b",
            fg=self.text_secondary
        ).pack(anchor="w", pady=(0, 5))

        self.compare_btn = AnimatedButton(
            btn_col,
            text="Compare Algorithms",
            command=self._on_compare_clicked,
            width=180,
            height=44
        )
        self.compare_btn.pack()

        self.reset_comp_btn = AnimatedButton(
            btn_col,
            text="Reset",
            command=self._on_reset_comparison,
            width=180,
            height=36
        )
        self.reset_comp_btn.pack(pady=(8, 0))

        self.comp_card = card
        self.summary_table_frame = tk.Frame(card, bg="#1e293b")
        self.summary_table_frame.pack(fill="x", padx=25, pady=(10, 10))

        self._init_summary_table()

        self.chart_frame = tk.Frame(card, bg="#1e293b")
        self.chart_frame.pack(fill="x", padx=25, pady=(10, 10))

        self._create_comparison_chart()

        self.analysis_label = tk.Label(
            card,
            text="Run a comparison to see analysis",
            font=("Inter", 12),
            bg="#1e293b",
            fg=self.text_secondary,
            padx=15,
            pady=12
        )
        self.analysis_label.pack(fill="x", padx=25, pady=(10, 10))

        self.step_table_frame = tk.Frame(card, bg="#1e293b")
        self.step_table_frame.pack(fill="both", expand=True, padx=25, pady=(10, 20))

        self._create_step_comparison_table()

    def _init_summary_table(self):
        """Create the side-by-side summary comparison table."""
        self.summary_table_frame = tk.Frame(self.comp_card, bg="#1e293b")

        card_header = tk.Frame(self.summary_table_frame, bg="#1f2937")
        card_header.pack(fill="x", padx=0, pady=(0, 5))

        tk.Label(
            card_header,
            text="Performance Summary",
            font=("Inter", 12, "bold"),
            bg="#1f2937",
            fg=self.text_primary
        ).pack(side="left", padx=10, pady=8)

        table_outer = tk.Frame(self.summary_table_frame, bg="#1f2937")
        table_outer.pack(fill="x", padx=10, pady=(0, 10))

        columns = ["Algorithm", "Total Faults", "Hit Ratio", "Efficiency"]
        headers = ["Algorithm", "Total Faults", "Hit Ratio", "Efficiency"]

        header_frame = tk.Frame(table_outer, bg="#374151")
        header_frame.pack(fill="x")

        col_widths = [140, 120, 100, 120]
        for i, (col, width) in enumerate(zip(columns, col_widths)):
            tk.Label(
                header_frame,
                text=headers[i],
                font=("Inter", 10, "bold"),
                bg="#374151",
                fg=self.text_primary,
                width=width // 8,
                anchor="center",
                pady=8
            ).pack(side="left")

        self.summary_rows_frame = tk.Frame(table_outer, bg="#1f2937")
        self.summary_rows_frame.pack(fill="x")

        self.lru_summary_labels = []
        self.optimal_summary_labels = []

        for row_data, row_labels in [("LRU", self.lru_summary_labels), ("Optimal", self.optimal_summary_labels)]:
            row_frame = tk.Frame(self.summary_rows_frame, bg="#1f2937")
            row_frame.pack(fill="x")

            values = [row_data, "--", "--%", "--"]
            for val, width in zip(values, col_widths):
                lbl = tk.Label(
                    row_frame,
                    text=val,
                    font=("Inter", 10),
                    bg="#1f2937",
                    fg=self.text_primary,
                    width=width // 8,
                    anchor="center",
                    pady=6
                )
                lbl.pack(side="left")
                row_labels.append(lbl)

        self.summary_table_frame.pack(fill="x", padx=25, pady=(10, 10))

    def _create_comparison_chart(self):
        """Create the Matplotlib bar chart for comparison."""
        chart_header = tk.Frame(self.chart_frame, bg="#1f2937")
        chart_header.pack(fill="x", pady=(0, 5))

        tk.Label(
            chart_header,
            text="Page Fault Comparison",
            font=("Inter", 12, "bold"),
            bg="#1f2937",
            fg=self.text_primary
        ).pack(side="left", padx=10, pady=8)

        self.comp_fig = Figure(figsize=(8, 4), dpi=100, facecolor='#161b22')
        self.comp_ax = self.comp_fig.add_subplot(111)
        self.comp_ax.set_facecolor('#161b22')

        self.comp_ax.set_xlabel('Algorithm', color='#9ca3af', fontsize=10)
        self.comp_ax.set_ylabel('Number of Page Faults', color='#9ca3af', fontsize=10)
        self.comp_ax.tick_params(colors='#9ca3af', labelsize=10)

        self.comp_ax.grid(True, color='#2d3748', linestyle='--', linewidth=0.5, alpha=0.7)
        self.comp_ax.spines['bottom'].set_color('#4b5563')
        self.comp_ax.spines['left'].set_color('#4b5563')
        self.comp_ax.spines['top'].set_visible(False)
        self.comp_ax.spines['right'].set_visible(False)

        self.comp_fig.tight_layout(pad=2.0)

        chart_inner = tk.Frame(self.chart_frame, bg='#161b22')
        chart_inner.pack(fill="x", padx=0, pady=(0, 5))

        self.comp_canvas = FigureCanvasTkAgg(self.comp_fig, master=chart_inner)
        self.comp_canvas.get_tk_widget().configure(bg='#161b22')
        self.comp_canvas.get_tk_widget().pack(fill="x")

        self._update_comparison_chart(0, 0)

    def _update_comparison_chart(self, lru_faults, optimal_faults):
        """Update the comparison bar chart."""
        self.comp_ax.clear()
        self.comp_ax.set_facecolor('#161b22')

        self.comp_ax.set_xlabel('Algorithm', color='#9ca3af', fontsize=10)
        self.comp_ax.set_ylabel('Number of Page Faults', color='#9ca3af', fontsize=10)
        self.comp_ax.tick_params(colors='#9ca3af', labelsize=10)

        self.comp_ax.grid(True, color='#2d3748', linestyle='--', linewidth=0.5, alpha=0.7)
        self.comp_ax.spines['bottom'].set_color('#4b5563')
        self.comp_ax.spines['left'].set_color('#4b5563')
        self.comp_ax.spines['top'].set_visible(False)
        self.comp_ax.spines['right'].set_visible(False)

        if lru_faults == 0 and optimal_faults == 0:
            self.comp_ax.text(0.5, 0.5, 'Run comparison to see chart',
                             ha='center', va='center', transform=self.comp_ax.transAxes,
                             color='#64748b', fontsize=12, style='italic')
            self.comp_ax.set_xlim(0, 1)
            self.comp_ax.set_ylim(0, 1)
            self.comp_ax.axis('off')
        else:
            algorithms = ['LRU', 'Optimal']
            faults = [lru_faults, optimal_faults]
            colors = ['#f97316', '#3b82f6']

            bars = self.comp_ax.bar(algorithms, faults, color=colors, width=0.5, edgecolor='white', linewidth=1)

            for bar, fault_count in zip(bars, faults):
                height = bar.get_height()
                self.comp_ax.text(bar.get_x() + bar.get_width()/2., height,
                                 f'{fault_count}',
                                 ha='center', va='bottom', fontsize=12, fontweight='bold', color='white')

            self.comp_ax.set_ylim(0, max(faults) * 1.2)
            self.comp_ax.set_xticks(range(len(algorithms)))
            self.comp_ax.set_xticklabels(algorithms)

            for i, (alg, color) in enumerate(zip(algorithms, colors)):
                rect = plt.Rectangle((0, 0), 0, 0, facecolor=color, label=alg)
                self.comp_ax.legend(handles=[plt.Rectangle((0,0),1,1, facecolor=colors[0]),
                                            plt.Rectangle((0,0),1,1, facecolor=colors[1])],
                                   labels=algorithms, loc='upper right',
                                   facecolor='#1e293b', edgecolor='#4b5563', labelcolor='#e5e7eb')

        self.comp_fig.tight_layout(pad=2.0)
        self.comp_canvas.draw()

    def _create_step_comparison_table(self):
        """Create the step-by-step comparison table."""
        step_header = tk.Frame(self.step_table_frame, bg="#1f2937")
        step_header.pack(fill="x", pady=(0, 5))

        tk.Label(
            step_header,
            text="Step-by-Step Comparison",
            font=("Inter", 12, "bold"),
            bg="#1f2937",
            fg=self.text_primary
        ).pack(side="left", padx=10, pady=8)

        self.step_table_container = tk.Frame(self.step_table_frame, bg="#1f2937")
        self.step_table_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.step_table_placeholder = tk.Label(
            self.step_table_container,
            text="Run a comparison to see step-by-step execution",
            font=("Inter", 12),
            bg="#1f2937",
            fg="#64748b",
            pady=40
        )
        self.step_table_placeholder.pack(fill="both", expand=True)

        self.step_table_inner = tk.Frame(self.step_table_container, bg="#1f2937")
        self.step_table_inner.pack_forget()

    def _on_compare_clicked(self):
        """Handle Compare Algorithms button click."""
        page_ref_str = self.comp_page_ref_entry.get()
        frames_str = self.comp_frames_entry.get()

        if not page_ref_str:
            messagebox.showerror("Input Error", "Please enter a page reference string.")
            return

        if not frames_str:
            messagebox.showerror("Input Error", "Please enter the number of frames.")
            return

        pages = parse_page_reference(page_ref_str)
        if pages is None or len(pages) == 0:
            messagebox.showerror("Input Error", "Invalid page reference string. Must be space-separated integers (e.g., 7 0 1 2 0 3).")
            return

        try:
            num_frames = int(frames_str)
            if num_frames <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Number of frames must be a positive integer (at least 1).")
            return

        self.compare_btn.configure(state="disabled")
        self._update_status_bar("Running comparison...")
        
        try:
            lru_snapshots, lru_faults_list, lru_total = simulate_lru(pages, num_frames)
            opt_snapshots, opt_faults_list, opt_total = simulate_optimal(pages, num_frames)

            self._update_comparison_results(pages, lru_snapshots, lru_faults_list, lru_total,
                                            opt_snapshots, opt_faults_list, opt_total, num_frames)
            self._update_status_bar(f"Comparison complete: LRU={lru_total} faults, Optimal={opt_total} faults")
        except Exception as e:
            messagebox.showerror("Error", f"Comparison failed: {str(e)}")
            self._update_status_bar("Comparison failed")
        finally:
            self.compare_btn.configure(state="normal")

    def _update_comparison_results(self, pages, lru_snapshots, lru_faults, lru_total,
                                   opt_snapshots, opt_faults, opt_total, num_frames):
        """Update all comparison results: summary, chart, analysis, and step table."""
        total_refs = len(pages)
        lru_hits = total_refs - lru_total
        opt_hits = total_refs - opt_total
        lru_hit_ratio = (lru_hits / total_refs * 100) if total_refs > 0 else 0
        opt_hit_ratio = (opt_hits / total_refs * 100) if total_refs > 0 else 0
        lru_eff = f"{(lru_hits / lru_total * 100):.1f}%" if lru_total > 0 else "N/A"
        opt_eff = f"{(opt_hits / opt_total * 100):.1f}%" if opt_total > 0 else "N/A"

        for lbl in self.lru_summary_labels:
            lbl.configure(fg=self.text_primary)
        for lbl in self.optimal_summary_labels:
            lbl.configure(fg=self.text_primary)

        self.lru_summary_labels[0].configure(text="LRU", fg="#f97316")
        self.lru_summary_labels[1].configure(text=str(lru_total))
        self.lru_summary_labels[2].configure(text=f"{lru_hit_ratio:.1f}%")
        self.lru_summary_labels[3].configure(text=lru_eff)

        self.optimal_summary_labels[0].configure(text="Optimal", fg="#3b82f6")
        self.optimal_summary_labels[1].configure(text=str(opt_total))
        self.optimal_summary_labels[2].configure(text=f"{opt_hit_ratio:.1f}%")
        self.optimal_summary_labels[3].configure(text=opt_eff)

        self._update_comparison_chart(lru_total, opt_total)

        if lru_total > opt_total:
            diff = lru_total - opt_total
            pct = (diff / lru_total * 100) if lru_total > 0 else 0
            analysis_text = f"Optimal algorithm produced {diff} fewer page faults than LRU ({pct:.1f}% improvement)"
        elif opt_total > lru_total:
            diff = opt_total - lru_total
            pct = (diff / opt_total * 100) if opt_total > 0 else 0
            analysis_text = f"LRU algorithm produced {diff} fewer page faults than Optimal ({pct:.1f}% improvement)"
        else:
            analysis_text = "Both algorithms produced the same number of page faults"

        self.analysis_label.configure(text=analysis_text, fg=self.text_primary, bg="#1e293b")

        self._display_step_comparison(pages, lru_snapshots, lru_faults, opt_snapshots, opt_faults, num_frames)

    def _display_step_comparison(self, pages, lru_snapshots, lru_faults, opt_snapshots, opt_faults, num_frames):
        """Display the step-by-step comparison table."""
        self.step_table_placeholder.pack_forget()
        self.step_table_inner.pack_forget()

        self.step_table_inner = tk.Frame(self.step_table_container, bg="#1f2937")
        self.step_table_inner.pack(fill="both", expand=True)

        scrollbar_y = ttk.Scrollbar(self.step_table_inner, orient="vertical")
        scrollbar_y.pack(side="right", fill="y")

        scrollbar_x = ttk.Scrollbar(self.step_table_inner, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")

        self.step_tree = ttk.Treeview(self.step_table_inner, show="headings", style="Modern.Treeview",
                                      yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set,
                                      height=10)
        scrollbar_y.configure(command=self.step_tree.yview)
        scrollbar_x.configure(command=self.step_tree.xview)

        self.step_tree.pack(side="left", fill="both", expand=True)

        columns = ["Step", "Page", "LRU Frames", "LRU Fault", "Optimal Frames", "Optimal Fault"]
        self.step_tree["columns"] = columns
        self.step_tree["show"] = "headings"

        col_widths = [50, 50, 150, 80, 150, 90]
        for col, width in zip(columns, col_widths):
            self.step_tree.heading(col, text=col)
            self.step_tree.column(col, width=width, anchor="center")

        for i, (page, lru_frames, lru_fault, opt_frames, opt_fault) in enumerate(
                zip(pages, lru_snapshots, lru_faults, opt_snapshots, opt_faults)):

            lru_frames_str = str(lru_frames) if lru_frames else "[]"
            opt_frames_str = str(opt_frames) if opt_frames else "[]"
            lru_fault_str = "FAULT" if lru_fault else "HIT"
            opt_fault_str = "FAULT" if opt_fault else "HIT"

            row_values = [i + 1, page, lru_frames_str, lru_fault_str, opt_frames_str, opt_fault_str]

            if lru_fault and opt_fault:
                tag = "both_fault"
            elif lru_fault:
                tag = "lru_fault"
            elif opt_fault:
                tag = "opt_fault"
            else:
                tag = "both_hit"

            self.step_tree.insert("", "end", values=row_values, tags=(tag,))

        self.step_tree.tag_configure("both_fault", background="#7f1d1d", foreground="white")
        self.step_tree.tag_configure("lru_fault", background="#78350f", foreground="white")
        self.step_tree.tag_configure("opt_fault", background="#1e3a5f", foreground="white")
        self.step_tree.tag_configure("both_hit", background="#14532d", foreground="white")

    def _on_run_clicked(self):
        """Handle Run Simulation button click."""
        page_ref_str = self.page_ref_entry.get()
        frames_str = self.frames_entry.get()

        if not page_ref_str:
            messagebox.showerror("Input Error", "Please enter a page reference string.")
            return
        
        if not frames_str:
            messagebox.showerror("Input Error", "Please enter the number of frames.")
            return

        pages = parse_page_reference(page_ref_str)
        if pages is None or len(pages) == 0:
            messagebox.showerror("Input Error", "Invalid page reference string. Must be space-separated integers (e.g., 7 0 1 2 0 3).")
            return

        try:
            num_frames = int(frames_str)
            if num_frames <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Number of frames must be a positive integer (at least 1).")
            return

        if num_frames > 10:
            messagebox.showwarning("Warning", "Large number of frames may affect visualization.")
        
        self.run_button.configure(state="disabled")
        self._update_status_bar("Running simulation...")
        
        try:
            algorithm_name = self.algorithm_dropdown.get()
            algorithm_func = ALGORITHMS.get(algorithm_name, simulate_lru)
            frames_snapshots, fault_flags, total_faults = algorithm_func(pages, num_frames)
            self._display_results(pages, frames_snapshots, fault_flags, total_faults, num_frames)
            self._update_status_bar(f"Simulation complete: {algorithm_name} algorithm with {total_faults} page faults")
        except Exception as e:
            messagebox.showerror("Error", f"Simulation failed: {str(e)}")
            self._update_status_bar("Simulation failed")
        finally:
            self.run_button.configure(state="normal")

    def _display_results(self, pages, frame_snapshots, fault_flags, total_faults, num_frames):
        """Display simulation results in the Treeview table and update graph."""
        self.table_placeholder.pack_forget()
        self.table_inner.pack(fill="both", expand=True)
        
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        columns = ["Step", "Page"] + [f"Frame {i+1}" for i in range(num_frames)] + ["Fault?"]
        self.result_tree["columns"] = columns
        self.result_tree["show"] = "headings"
        
        for col in columns:
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=80, anchor="center")
        
        for i, (page, frames, is_fault) in enumerate(zip(pages, frame_snapshots, fault_flags)):
            row_values = [i + 1, page] + frames + [""] * (num_frames - len(frames))
            fault_text = "FAULT" if is_fault else "HIT"
            row_values.append(fault_text)
            
            tag = "fault" if is_fault else "hit"
            self.result_tree.insert("", "end", values=row_values, tags=(tag,))

        total_steps = len(pages)
        hits = total_steps - total_faults
        hit_ratio = (hits / total_steps * 100) if total_steps > 0 else 0
        
        self.page_faults_label.configure(text=f"Faults: {total_faults}")
        self.hit_ratio_label.configure(text=f"Hit: {hit_ratio:.1f}%")
        
        self.summary_label.configure(text=f"Total References: {total_steps}  |  Total Faults: {total_faults}  |  Hit Ratio: {hit_ratio:.1f}%")
        
        steps = list(range(1, total_steps + 1))
        cumulative_faults = []
        fault_count = 0
        for is_fault in fault_flags:
            if is_fault:
                fault_count += 1
            cumulative_faults.append(fault_count)
        
        self._update_graph(steps, cumulative_faults, fault_flags)
        
        self.root.update_idletasks()
        if hasattr(self, 'scroll_canvas'):
            self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _on_reset_paging(self):
        """Reset the paging tab to initial state."""
        self.page_ref_entry.entry.delete(0, tk.END)
        self.page_ref_entry.entry.insert(0, self.page_ref_entry.placeholder)
        self.page_ref_entry.entry.configure(fg=self.page_ref_entry.placeholder_color)
        self.page_ref_entry._has_value = False
        
        self.frames_entry.entry.delete(0, tk.END)
        self.frames_entry.entry.insert(0, self.frames_entry.placeholder)
        self.frames_entry.entry.configure(fg=self.frames_entry.placeholder_color)
        self.frames_entry._has_value = False
        
        self.algorithm_dropdown.dropdown.current(0)
        
        self.page_faults_label.configure(text="Faults: --")
        self.hit_ratio_label.configure(text="Hit: --")
        self.summary_label.configure(text="Total References: --  |  Total Faults: --  |  Hit Ratio: --")
        
        self.table_placeholder.pack(fill="both", expand=True)
        self.table_inner.pack_forget()
        
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        self._update_graph([], [], [])
        self._update_status_bar("Paging tab reset")

    def _on_reset_comparison(self):
        """Reset the comparison tab to initial state."""
        self.comp_page_ref_entry.entry.delete(0, tk.END)
        self.comp_page_ref_entry.entry.insert(0, self.comp_page_ref_entry.placeholder)
        self.comp_page_ref_entry.entry.configure(fg=self.comp_page_ref_entry.placeholder_color)
        self.comp_page_ref_entry._has_value = False
        
        self.comp_frames_entry.entry.delete(0, tk.END)
        self.comp_frames_entry.entry.insert(0, self.comp_frames_entry.placeholder)
        self.comp_frames_entry.entry.configure(fg=self.comp_frames_entry.placeholder_color)
        self.comp_frames_entry._has_value = False
        
        for lbl in self.lru_summary_labels:
            lbl.configure(text="--", fg=self.text_primary)
        self.lru_summary_labels[0].configure(text="LRU", fg="#f97316")
        
        for lbl in self.optimal_summary_labels:
            lbl.configure(text="--", fg=self.text_primary)
        self.optimal_summary_labels[0].configure(text="Optimal", fg="#3b82f6")
        
        self._update_comparison_chart(0, 0)
        self.analysis_label.configure(text="Run a comparison to see analysis", fg=self.text_secondary, bg="#1e293b")
        
        self.step_table_placeholder.pack(fill="both", expand=True)
        self.step_table_inner.pack_forget()
        
        self._update_status_bar("Comparison tab reset")

    def _create_fault_graph(self, parent):
        """Create the embedded Matplotlib graph for page faults."""
        graph_card = ModernCard(parent)
        graph_card.grid(row=1, column=0, sticky="nsew", pady=(15, 0))

        card_header = tk.Frame(graph_card, bg="#1e293b")
        card_header.pack(fill="x", padx=20, pady=(15, 10))

        tk.Label(
            card_header,
            text="Page Fault Graph",
            font=("Inter", 14, "bold"),
            bg="#1e293b",
            fg=self.text_primary
        ).pack(side="left")

        self.fig = Figure(figsize=(8, 5), dpi=100, facecolor='#161b22')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#161b22')
        
        plt.style.use('dark_background')
        
        self.ax.set_xlabel('Step Number', color='#9ca3af', fontsize=10)
        self.ax.set_ylabel('Cumulative Page Faults', color='#9ca3af', fontsize=10)
        self.ax.tick_params(colors='#9ca3af', labelsize=9)
        
        self.ax.grid(True, color='#2d3748', linestyle='--', linewidth=0.5, alpha=0.7)
        self.ax.spines['bottom'].set_color('#4b5563')
        self.ax.spines['left'].set_color('#4b5563')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        
        self.fig.tight_layout(pad=2.0)

        graph_inner = tk.Frame(graph_card, bg='#161b22')
        graph_inner.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_inner)
        self.canvas.get_tk_widget().configure(bg='#161b22')
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self._update_graph([], [], [])

    def _update_graph(self, steps, cumulative_faults, fault_flags):
        """Update the page fault graph with new data."""
        self.ax.clear()
        self.ax.set_facecolor('#161b22')
        
        self.ax.set_xlabel('Step Number', color='#9ca3af', fontsize=10)
        self.ax.set_ylabel('Cumulative Page Faults', color='#9ca3af', fontsize=10)
        self.ax.tick_params(colors='#9ca3af', labelsize=9)
        
        self.ax.grid(True, color='#2d3748', linestyle='--', linewidth=0.5, alpha=0.7)
        self.ax.spines['bottom'].set_color('#4b5563')
        self.ax.spines['left'].set_color('#4b5563')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        
        if len(steps) > 0:
            self.ax.step(steps, cumulative_faults, where='post', color='#3b82f6', linewidth=2, label='Cumulative Faults')
            
            fault_points = [(s, cf) for s, cf, is_fault in zip(steps, cumulative_faults, fault_flags) if is_fault]
            if fault_points:
                fx, fy = zip(*fault_points)
                self.ax.scatter(fx, fy, color='#ef4444', s=60, zorder=5, label='Page Fault', edgecolors='white', linewidths=0.5)
            
            self.ax.legend(loc='upper left', fontsize=9, facecolor='#1e293b', edgecolor='#4b5563', labelcolor='#e5e7eb')
            self.ax.set_xlim(0.5, max(steps) + 0.5)
            self.ax.set_ylim(-0.2, max(cumulative_faults) + 0.5)
        else:
            self.ax.text(0.5, 0.5, 'Run a simulation to see the graph', 
                        ha='center', va='center', transform=self.ax.transAxes,
                        color='#64748b', fontsize=14, style='italic')
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(0, 1)
            self.ax.axis('off')
        self.fig.tight_layout(pad=2.0)
        self.canvas.draw()


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = VirtualMemoryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
