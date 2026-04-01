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

        self._create_ui()

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
            text="Day 4: added scrollable results table, styled scrollbar, improved layout and UI fixes",
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
        """Create the Segmentation tab content."""
        content = tk.Frame(self.content_frame, bg="#0f172a")
        self.tab_contents.append(content)

        card = ModernCard(content)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        card_header = tk.Frame(card, bg="#1e293b")
        card_header.pack(fill="x", padx=25, pady=(20, 15))

        tk.Label(
            card_header,
            text="Segmentation & Fragmentation",
            font=("Inter", 18, "bold"),
            bg="#1e293b",
            fg=self.text_primary
        ).pack(side="left")

        tk.Label(
            card_header,
            text="Coming Soon",
            font=("Inter", 10, "bold"),
            bg="#8b5cf6",
            fg="white",
            padx=12,
            pady=4
        ).pack(side="right")

        placeholder = tk.Label(
            card,
            text="🔧  This module is under development.\n\nFeatures planned:\n• Segmentation with variable-sized segments\n• Internal and external fragmentation visualization\n• Memory allocation algorithms\n• Fragmentation metrics",
            font=("Inter", 12),
            bg="#1e293b",
            fg=self.text_secondary,
            justify="left",
            anchor="nw",
            padx=25,
            pady=20
        )
        placeholder.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def _create_comparison_tab(self):
        """Create the LRU vs Optimal comparison tab content."""
        content = tk.Frame(self.content_frame, bg="#0f172a")
        self.tab_contents.append(content)

        card = ModernCard(content)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        card_header = tk.Frame(card, bg="#1e293b")
        card_header.pack(fill="x", padx=25, pady=(20, 15))

        tk.Label(
            card_header,
            text="Algorithm Comparison",
            font=("Inter", 18, "bold"),
            bg="#1e293b",
            fg=self.text_primary
        ).pack(side="left")

        tk.Label(
            card_header,
            text="Coming Soon",
            font=("Inter", 10, "bold"),
            bg="#8b5cf6",
            fg="white",
            padx=12,
            pady=4
        ).pack(side="right")

        placeholder = tk.Label(
            card,
            text="⚡  This module is under development.\n\nFeatures planned:\n• Side-by-side LRU vs Optimal comparison\n• Performance metrics visualization\n• Hit/Miss ratio charts\n• Comparative analysis",
            font=("Inter", 12),
            bg="#1e293b",
            fg=self.text_secondary,
            justify="left",
            anchor="nw",
            padx=25,
            pady=20
        )
        placeholder.pack(fill="both", expand=True, padx=20, pady=(0, 20))

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
            messagebox.showerror("Input Error", "Invalid page reference string. Please enter space or comma-separated integers.")
            return

        try:
            num_frames = int(frames_str)
            if num_frames <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Number of frames must be a positive integer.")
            return

        if num_frames > 10:
            messagebox.showwarning("Warning", "Large number of frames may affect visualization.")
        
        algorithm_name = self.algorithm_dropdown.get()
        algorithm_func = ALGORITHMS.get(algorithm_name, simulate_lru)
        frames_snapshots, fault_flags, total_faults = algorithm_func(pages, num_frames)
        self._display_results(pages, frames_snapshots, fault_flags, total_faults, num_frames)

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
