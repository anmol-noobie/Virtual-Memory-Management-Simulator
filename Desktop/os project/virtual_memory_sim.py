"""
Virtual Memory Management Simulator
A Tkinter-based GUI application for visualizing and simulating
virtual memory management techniques.
"""

import tkinter as tk
from tkinter import ttk
import time


class AnimatedButton(tk.Canvas):
    """Animated button with smooth hover and click effects."""

    def __init__(self, parent, text="", command=None, width=180, height=45, **kwargs):
        super().__init__(parent, width=width, height=height)
        self.command = command
        self._text = text
        self.base_bg = "#3b82f6"
        self.hover_bg = "#2563eb"
        self.active_bg = "#1d4ed8"
        self.text_color = "white"
        self.corner_radius = 12
        self.current_bg = self.base_bg
        self.animation_running = False
        self.hovered = False
        self.clicked = False

        self.configure(highlightthickness=0, bg="#1a1a2e", cursor="hand2")
        self._text_id = None
        self._draw_button()

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _draw_button(self):
        """Draw the rounded rectangle and text."""
        self.delete("all")
        w, h = self.winfo_width() or 180, self.winfo_height() or 45
        self.create_rounded_rect(0, 0, w, h, self.corner_radius, fill=self.current_bg, outline="")
        self._text_id = self.create_text(w // 2, h // 2, text=self._text, fill=self.text_color, font=("Inter", 12, "bold"))

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = []
        r = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)
        points = [x1 + r, y1, x2 - r, y1, x2, y1 + r, x2, y2 - r, x2 - r, y2, x1 + r, y2, x1, y2 - r, x1, y1 + r]
        return self.create_polygon(points, smooth=True, joinstyle=tk.ROUND, **kwargs)

    def _animate_color(self, target_color):
        """Animate color transition."""
        if not self.hovered and not self.clicked:
            return
        self.current_bg = target_color
        self._draw_button()

    def _on_enter(self, event):
        self.hovered = True
        self.current_bg = self.hover_bg
        self._draw_button()
        self.configure(bg="#1e3a5f")

    def _on_leave(self, event):
        self.hovered = False
        self.current_bg = self.base_bg
        self._draw_button()
        self.configure(bg="#1a1a2e")

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
    """Modern styled entry with animated focus border."""

    def __init__(self, parent, placeholder="", width=40, **kwargs):
        super().__init__(parent, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = "#6b7280"
        self.text_color = "#e5e7eb"
        self.border_color = "#374151"
        self.focus_color = "#3b82f6"
        self.current_border_color = self.border_color

        self.configure(bg="#1f2937", highlightthickness=2, highlightcolor=self.border_color, highlightbackground=self.border_color)

        self.entry = tk.Entry(
            self,
            font=("Inter", 11),
            bg="#1f2937",
            fg=self.text_color,
            insertbackground=self.text_color,
            relief=tk.FLAT,
            bd=0,
            width=width
        )
        self.entry.pack(fill="x", padx=12, pady=10)

        self._show_placeholder()
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<KeyRelease>", self._on_key_release)

        self.after(100, self._update_border)

    def _update_border(self):
        """Update the border color."""
        self.configure(highlightbackground=self.current_border_color, highlightcolor=self.current_border_color)

    def _show_placeholder(self):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.placeholder)
        self.entry.configure(fg=self.placeholder_color)

    def _hide_placeholder(self):
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.configure(fg=self.text_color)
        self.current_border_color = self.focus_color
        self._update_border()

    def _on_focus_in(self, event):
        self._hide_placeholder()

    def _on_focus_out(self, event):
        if self.entry.get() == "":
            self._show_placeholder()
        self.current_border_color = self.border_color
        self._update_border()

    def _on_key_release(self, event):
        if self.entry.get() == "":
            self.current_border_color = self.border_color
            self._update_border()

    def get(self):
        value = self.entry.get()
        return "" if value == self.placeholder else value

    def insert(self, index, text):
        self.entry.delete(0, tk.END)
        self._hide_placeholder()
        self.entry.insert(0, text)


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
                       foreground="#e5e7eb",
                       borderwidth=0,
                       padding=0)
        style.configure("Modern.Treeview",
                       background="#1f2937",
                       fieldbackground="#1f2937",
                       foreground="#e5e7eb")
        self.dropdown.configure(style="Modern.TCombobox")

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
            text="Interactive Page Replacement Visualization",
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

        left_panel = tk.Frame(content, bg="#0f172a")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 20))

        self._create_input_card(left_panel)
        self._create_run_button(left_panel)

        right_panel = tk.Frame(content, bg="#0f172a")
        right_panel.pack(side="right", fill="both", expand=True)

        self._create_output_area(right_panel)

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

        self.page_ref_entry = ModernEntry(input_container, placeholder="7, 0, 1, 2, 0, 3, 0, 4, 1, 2", width=45)
        self.page_ref_entry.grid(row=1, column=0, sticky="ew", pady=(0, 15), columnspan=2)

        tk.Label(
            input_container,
            text="Number of Frames",
            font=("Inter", 10, "bold"),
            bg="#1e293b",
            fg=self.text_secondary
        ).grid(row=2, column=0, sticky="w", pady=(0, 5))

        self.frames_entry = ModernEntry(input_container, placeholder="3", width=45)
        self.frames_entry.grid(row=3, column=0, sticky="ew", pady=(0, 15), columnspan=2)

        tk.Label(
            input_container,
            text="Algorithm",
            font=("Inter", 10, "bold"),
            bg="#1e293b",
            fg=self.text_secondary
        ).grid(row=4, column=0, sticky="w", pady=(0, 5))

        self.algorithm_dropdown = ModernDropdown(input_container, values=["LRU", "Optimal", "FIFO", "Clock"], width=45)
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
        """Create the output visualization area."""
        card = ModernCard(parent)
        card.pack(fill="both", expand=True)

        card_header = tk.Frame(card, bg="#1e293b")
        card_header.pack(fill="x", padx=20, pady=(15, 10))

        tk.Label(
            card_header,
            text="Visualization",
            font=("Inter", 14, "bold"),
            bg="#1e293b",
            fg=self.text_primary
        ).pack(side="left")

        stats_frame = tk.Frame(card_header, bg="#1e293b")
        stats_frame.pack(side="right")

        self.page_faults_label = tk.Label(
            stats_frame,
            text="Page Faults: --",
            font=("Inter", 10, "bold"),
            bg="#1e293b",
            fg="#ef4444",
            padx=10
        )
        self.page_faults_label.pack(side="left", padx=(0, 10))

        self.hit_ratio_label = tk.Label(
            stats_frame,
            text="Hit Ratio: --",
            font=("Inter", 10, "bold"),
            bg="#1e293b",
            fg="#22c55e"
        )
        self.hit_ratio_label.pack(side="left")

        output_frame = tk.Frame(card, bg="#1e293b")
        output_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.output_label = tk.Label(
            output_frame,
            text="Click 'Run Simulation' to see the page replacement algorithm in action...",
            font=("Inter", 11),
            bg="#1e293b",
            fg=self.text_secondary,
            justify="left",
            anchor="nw",
            wraplength=500
        )
        self.output_label.pack(fill="both", expand=True, pady=10)

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
        """Placeholder handler for Run Simulation button."""
        self.output_label.configure(
            text="Simulation logic will be implemented here...\n\nInput received:\n• Page Reference: " + self.page_ref_entry.get() + "\n• Frames: " + self.frames_entry.get() + "\n• Algorithm: " + self.algorithm_dropdown.get(),
            fg=self.text_primary
        )


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = VirtualMemoryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
