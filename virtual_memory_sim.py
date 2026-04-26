"""
Virtual Memory Management Simulator
A Tkinter-based GUI application for visualizing and simulating
virtual memory management techniques including paging, segmentation,
and page replacement algorithm comparison.

New in this version:
  - Segmentation: First Fit / Best Fit / Worst Fit allocation strategies
  - Segmentation: Compact Memory button with before/after visualisation
  - Segmentation: Per-segment delete button in the segment list
  - Segmentation: Hole-size column in allocation results table
"""

import tkinter as tk
from tkinter import ttk, messagebox
from collections import OrderedDict
import math

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as mpatches



def simulate_lru(pages, num_frames):
    """LRU page replacement.

    Returns (frame_snapshots, fault_flags, total_faults).
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
    """Optimal page replacement.

    Returns (frame_snapshots, fault_flags, total_faults).
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
                future = pages[i + 1:]
                replace_idx = 0
                max_dist = -1
                for j, fp in enumerate(frames):
                    try:
                        dist = future.index(fp)
                    except ValueError:
                        dist = len(future) + 1
                    if dist > max_dist:
                        max_dist = dist
                        replace_idx = j
                frames[replace_idx] = page
        frame_snapshots.append(frames.copy())

    return frame_snapshots, fault_flags, total_faults


def simulate_segmentation(segments, total_memory=512, strategy='first'):
    """Segmentation with pluggable allocation strategy.

    Args:
        segments   : list of {'name': str, 'size': int}
        total_memory: int  – total KB
        strategy   : 'first' | 'best' | 'worst'

    Returns:
        (allocations, stats, free_list_after)

        allocations : list of dicts
            { name, size, base, end, hole_size, status }
        stats : dict
            { total_memory, used_memory, free_memory,
              external_fragmentation, largest_free_before }
        free_list_after : list of {start, size}
    """
    # Free list represented as [{start, size}, ...]
    free_list = [{'start': 0, 'size': total_memory}]
    allocations = []

    for seg in segments:
        candidates = [
            {**h, 'idx': i}
            for i, h in enumerate(free_list)
            if h['size'] >= seg['size']
        ]

        if not candidates:
            allocations.append({
                'name': seg['name'],
                'size': seg['size'],
                'base': '-',
                'end': '-',
                'hole_size': None,
                'status': 'Failed',
            })
            continue

        if strategy == 'first':
            chosen = min(candidates, key=lambda h: h['start'])
        elif strategy == 'best':
            chosen = min(candidates, key=lambda h: h['size'])
        else:  # worst
            chosen = max(candidates, key=lambda h: h['size'])

        base = chosen['start']
        allocations.append({
            'name': seg['name'],
            'size': seg['size'],
            'base': base,
            'end': base + seg['size'],
            'hole_size': chosen['size'],
            'status': 'Allocated',
        })

        # Split chosen hole
        remaining = chosen['size'] - seg['size']
        idx = chosen['idx']
        if remaining > 0:
            free_list[idx] = {'start': chosen['start'] + seg['size'], 'size': remaining}
        else:
            free_list.pop(idx)

    used = sum(a['size'] for a in allocations if a['status'] == 'Allocated')
    free = total_memory - used
    largest_before = max((h['size'] for h in free_list), default=0)

    stats = {
        'total_memory': total_memory,
        'used_memory': used,
        'free_memory': free,
        'external_fragmentation': free,
        'largest_free_before': largest_before,
    }
    return allocations, stats, free_list


def parse_page_reference(text):
    """Parse space/comma-separated page reference string."""
    try:
        return [int(x.strip()) for x in text.replace(',', ' ').split() if x.strip()]
    except ValueError:
        return None


# ─────────────────────────────────────────────────────────────────
#  COLOUR PALETTE
# ─────────────────────────────────────────────────────────────────
BG_DARK   = '#0f172a'
BG_CARD   = '#1e293b'
BG_INPUT  = '#1f2937'
BG_ROW2   = '#111827'
COL_BLUE  = '#3b82f6'
COL_GREEN = '#22c55e'
COL_RED   = '#ef4444'
COL_AMBE  = '#f59e0b'
COL_GRAY  = '#64748b'
TXT_PRI   = '#f1f5f9'
TXT_SEC   = '#94a3b8'
BDR       = '#334155'

SEG_COLOURS = ['#2563eb', '#7c3aed', '#059669', '#d97706',
               '#dc2626', '#0891b2', '#db2777', '#16a34a']


# ─────────────────────────────────────────────────────────────────
#  HELPER WIDGETS
# ─────────────────────────────────────────────────────────────────

class Card(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG_CARD, **kw)


class Label(tk.Label):
    def __init__(self, parent, text='', size=11, bold=False,
                 colour=TXT_PRI, bg=BG_CARD, **kw):
        font = ('Inter', size, 'bold' if bold else 'normal')
        super().__init__(parent, text=text, font=font,
                         bg=bg, fg=colour, **kw)


def styled_entry(parent, placeholder='', width=34):
    """Return a tk.Entry pre-styled for the dark theme."""
    wrapper = tk.Frame(parent, bg=BG_INPUT,
                       highlightthickness=1,
                       highlightbackground=BDR)
    e = tk.Entry(wrapper, font=('Segoe UI', 10),
                 bg=BG_INPUT, fg=COL_GRAY,
                 insertbackground=TXT_PRI,
                 relief=tk.FLAT, bd=0, width=width)
    e.pack(fill='x', padx=10, pady=6)
    e.insert(0, placeholder)

    def _focus_in(ev):
        if e.get() == placeholder:
            e.delete(0, tk.END)
            e.config(fg=TXT_PRI)

    def _focus_out(ev):
        if e.get() == '':
            e.insert(0, placeholder)
            e.config(fg=COL_GRAY)

    e.bind('<FocusIn>',  _focus_in)
    e.bind('<FocusOut>', _focus_out)
    e._placeholder = placeholder
    return wrapper, e


def get_entry(entry_widget, placeholder):
    v = entry_widget.get()
    return '' if v == placeholder else v


def styled_btn(parent, text, command, colour='#1a6bff',
               hover='#3388ff', width=None, height=36):
    """Simple flat tk.Button styled for the dark theme."""
    kw = dict(text=text, command=command,
              font=('Inter', 10, 'bold'),
              bg=colour, fg='white',
              activebackground=hover, activeforeground='white',
              relief=tk.FLAT, bd=0, cursor='hand2',
              pady=6)
    if width:
        kw['width'] = width
    b = tk.Button(parent, **kw)
    b.bind('<Enter>', lambda e: b.config(bg=hover))
    b.bind('<Leave>', lambda e: b.config(bg=colour))
    return b


def styled_dropdown(parent, values, textvariable, width=30):
    s = ttk.Style()
    s.theme_use('clam')
    s.configure('Dark.TCombobox',
                fieldbackground=BG_INPUT, background=BG_INPUT,
                foreground=TXT_PRI, selectbackground=BG_INPUT,
                selectforeground=TXT_PRI, borderwidth=0, arrowsize=14)
    s.map('Dark.TCombobox',
          fieldbackground=[('readonly', BG_INPUT)],
          foreground=[('readonly', TXT_PRI)])
    cb = ttk.Combobox(parent, values=values,
                      textvariable=textvariable,
                      state='readonly', width=width,
                      font=('Inter', 10),
                      style='Dark.TCombobox')
    cb.current(0)
    return cb


def style_treeview():
    s = ttk.Style()
    s.theme_use('clam')
    s.configure('Dark.Treeview',
                background='#1f2937', fieldbackground='#1f2937',
                foreground='#e5e7eb', rowheight=26, borderwidth=0)
    s.configure('Dark.Treeview.Heading',
                background='#374151', fieldbackground='#374151',
                foreground=TXT_PRI,
                font=('Inter', 9, 'bold'), borderwidth=0)
    s.map('Dark.Treeview', background=[('selected', COL_BLUE)])


# ─────────────────────────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────────────────────────

class VirtualMemoryApp:
    def __init__(self, root):
        self.root = root
        root.title('Virtual Memory Management Simulator')
        root.geometry('1100x750')
        root.minsize(900, 620)
        root.configure(bg=BG_DARK)

        self.segments = []           # list of {'name':str, 'size':int}
        self.last_seg_result = None  # stores last segmentation run for Compact

        style_treeview()
        self._build_ui()

    # ── Top-level layout ──────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        self._build_tabs()
        self._build_status()
        self._show_tab(0)

    def _build_header(self):
        hdr = tk.Frame(self.root, bg='#0a0f1e', height=72)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)
        inner = tk.Frame(hdr, bg='#0a0f1e')
        inner.pack(fill='both', expand=True, padx=28, pady=14)
        tk.Label(inner, text='Virtual Memory Simulator',
                 font=('Inter', 22, 'bold'),
                 bg='#0a0f1e', fg=TXT_PRI).pack(side='left')
        tk.Label(inner,
                 text='Paging · Segmentation · Algorithm Comparison',
                 font=('Inter', 11), bg='#0a0f1e', fg=TXT_SEC
                 ).pack(side='left', padx=16, pady=4)
        tk.Label(inner, text=' v2.0 ', font=('Inter', 9, 'bold'),
                 bg=COL_BLUE, fg='white', padx=8, pady=2
                 ).pack(side='left')

    def _build_tabs(self):
        self.active_tab = 0
        tab_bar = tk.Frame(self.root, bg=BG_DARK)
        tab_bar.pack(fill='x', padx=24, pady=(10, 0))

        names = ['📄 Paging & Demand Paging',
                 '🧩 Segmentation & Fragmentation',
                 '⚡ LRU vs Optimal Comparison']
        self._tab_btns = []
        for i, n in enumerate(names):
            b = tk.Label(tab_bar, text=n,
                         font=('Inter', 11),
                         bg=BG_DARK, fg=TXT_SEC,
                         padx=20, pady=10, cursor='hand2')
            b.pack(side='left', padx=(0, 6))
            b.bind('<Button-1>', lambda e, i=i: self._show_tab(i))
            self._tab_btns.append(b)

        sep = tk.Frame(self.root, bg=BDR, height=1)
        sep.pack(fill='x', padx=0)

        self.tab_frame = tk.Frame(self.root, bg=BG_DARK)
        self.tab_frame.pack(fill='both', expand=True, padx=20, pady=16)

        self._pages = []
        self._pages.append(self._build_paging_page())
        self._pages.append(self._build_segmentation_page())
        self._pages.append(self._build_comparison_page())

    def _show_tab(self, idx):
        for i, b in enumerate(self._tab_btns):
            if i == idx:
                b.config(bg=COL_BLUE, fg='white')
            else:
                b.config(bg=BG_DARK, fg=TXT_SEC)
        for i, p in enumerate(self._pages):
            if i == idx:
                p.pack(fill='both', expand=True)
            else:
                p.pack_forget()
        self.active_tab = idx

    def _build_status(self):
        bar = tk.Frame(self.root, bg='#111827', height=28)
        bar.pack(fill='x', side='bottom')
        bar.pack_propagate(False)
        self._status_var = tk.StringVar(value='Ready')
        tk.Label(bar, textvariable=self._status_var,
                 font=('Inter', 9), bg='#111827', fg=TXT_SEC,
                 anchor='w', padx=16).pack(fill='x')

    def _set_status(self, msg):
        self._status_var.set(msg)
        self.root.update_idletasks()

    # ══════════════════════════════════════════════════════════════
    #  TAB 1 — PAGING
    # ══════════════════════════════════════════════════════════════

    def _build_paging_page(self):
        page = tk.Frame(self.tab_frame, bg=BG_DARK)

        # Left panel – config
        left = tk.Frame(page, bg=BG_DARK, width=280)
        left.pack(side='left', fill='y', padx=(0, 14))
        left.pack_propagate(False)
        self._build_paging_config(left)

        # Right panel – results + graph
        right = tk.Frame(page, bg=BG_DARK)
        right.pack(side='left', fill='both', expand=True)

        # Results card
        res_card = Card(right)
        res_card.pack(fill='both', expand=True, pady=(0, 12))
        Label(res_card, '  Results Table', size=12, bold=True,
              bg=BG_CARD).pack(anchor='w', pady=(10, 4))

        self._pg_tree_frame = tk.Frame(res_card, bg=BG_CARD)
        self._pg_tree_frame.pack(fill='both', expand=True, padx=12, pady=(0, 10))
        self._pg_placeholder = tk.Label(
            self._pg_tree_frame,
            text='Run a simulation to see results',
            font=('Inter', 11), bg=BG_CARD, fg=COL_GRAY, pady=40)
        self._pg_placeholder.pack()

        # Graph card
        graph_card = Card(right)
        graph_card.pack(fill='x', pady=(0, 4))
        Label(graph_card, '  Page Fault Graph', size=12, bold=True,
              bg=BG_CARD).pack(anchor='w', pady=(10, 4))
        self._pg_graph_frame = tk.Frame(graph_card, bg=BG_CARD)
        self._pg_graph_frame.pack(fill='x', padx=12, pady=(0, 10))
        self._pg_fig = Figure(figsize=(6, 2.2), facecolor=BG_CARD)
        self._pg_ax  = self._pg_fig.add_subplot(111)
        self._pg_canvas = FigureCanvasTkAgg(self._pg_fig, self._pg_graph_frame)
        self._pg_canvas.get_tk_widget().pack(fill='x')
        self._pg_draw_empty_graph()

        return page

    def _build_paging_config(self, parent):
        card = Card(parent)
        card.pack(fill='x', pady=(0, 12))

        Label(card, '  Configuration', size=12, bold=True,
              bg=BG_CARD).pack(anchor='w', pady=(10, 6))

        f = tk.Frame(card, bg=BG_CARD)
        f.pack(fill='x', padx=12, pady=(0, 10))

        Label(f, 'Page Reference String', size=9, bold=True,
              colour=TXT_SEC, bg=BG_CARD).pack(anchor='w', pady=(4, 2))
        self._pg_ref_wrap, self._pg_ref_e = styled_entry(
            f, 'e.g. 7 0 1 2 0 3 0 4', 32)
        self._pg_ref_wrap.pack(fill='x', pady=(0, 8))

        Label(f, 'Number of Frames', size=9, bold=True,
              colour=TXT_SEC, bg=BG_CARD).pack(anchor='w', pady=(0, 2))
        self._pg_frm_wrap, self._pg_frm_e = styled_entry(f, 'e.g. 3', 32)
        self._pg_frm_wrap.pack(fill='x', pady=(0, 8))

        Label(f, 'Algorithm', size=9, bold=True,
              colour=TXT_SEC, bg=BG_CARD).pack(anchor='w', pady=(0, 2))
        self._pg_algo_var = tk.StringVar(value='LRU')
        self._pg_algo_cb = styled_dropdown(
            f, ['LRU', 'Optimal'], self._pg_algo_var, 28)
        self._pg_algo_cb.pack(fill='x', pady=(0, 6))

        tk.Label(f, text='LRU: least recently used page\nOptimal: farthest future use',
                 font=('Inter', 8), bg=BG_CARD, fg=COL_GRAY,
                 justify='left').pack(anchor='w')

        # Buttons
        bf = tk.Frame(card, bg=BG_CARD)
        bf.pack(fill='x', padx=12, pady=(4, 12))
        styled_btn(bf, '▶  Run Simulation',
                   self._run_paging, '#238636', '#2ea043').pack(
            fill='x', pady=(0, 6))
        styled_btn(bf, '↺  Reset / Clear',
                   self._reset_paging, '#21262d', '#30363d').pack(fill='x')

        # Stats card
        self._pg_stats_card = Card(parent)
        self._pg_stats_card.pack(fill='x')
        sf = tk.Frame(self._pg_stats_card, bg=BG_CARD)
        sf.pack(fill='x', padx=12, pady=10)
        self._pg_faults_lbl  = self._stat_box(sf, 'Page Faults', '--', COL_RED)
        self._pg_hit_lbl     = self._stat_box(sf, 'Hit Ratio',   '--', COL_GREEN)
        self._pg_total_lbl   = self._stat_box(sf, 'Total Refs',  '--', TXT_PRI)
        self._pg_faults_lbl.pack(side='left', padx=(0, 8))
        self._pg_hit_lbl.pack(side='left', padx=(0, 8))
        self._pg_total_lbl.pack(side='left')

    def _stat_box(self, parent, label, value, colour):
        box = tk.Frame(parent, bg='#0d1117',
                       highlightthickness=1, highlightbackground=BDR)
        tk.Label(box, text=label, font=('Inter', 8, 'bold'),
                 bg='#0d1117', fg=TXT_SEC).pack(padx=12, pady=(6, 0))
        lbl = tk.Label(box, text=value, font=('JetBrains Mono', 18, 'bold'),
                       bg='#0d1117', fg=colour)
        lbl.pack(padx=12, pady=(0, 8))
        box._value_label = lbl
        return box

    # ── Paging logic ─────────────────────────────────────────────

    def _run_paging(self):
        ref_str = get_entry(self._pg_ref_e, 'e.g. 7 0 1 2 0 3 0 4')
        frm_str = get_entry(self._pg_frm_e, 'e.g. 3')
        if not ref_str:
            messagebox.showerror('Error', 'Please enter a page reference string.')
            return
        pages = parse_page_reference(ref_str)
        if not pages:
            messagebox.showerror('Error', 'Invalid page reference string.')
            return
        try:
            nf = int(frm_str)
            assert nf >= 1
        except Exception:
            messagebox.showerror('Error', 'Frames must be a positive integer.')
            return

        algo = self._pg_algo_var.get()
        self._set_status(f'Running {algo}…')
        if algo == 'LRU':
            snaps, faults, total = simulate_lru(pages, nf)
        else:
            snaps, faults, total = simulate_optimal(pages, nf)

        hits = len(pages) - total
        self._pg_faults_lbl._value_label.config(text=str(total))
        self._pg_hit_lbl._value_label.config(
            text=f'{hits/len(pages)*100:.1f}%')
        self._pg_total_lbl._value_label.config(text=str(len(pages)))

        self._draw_paging_table(pages, snaps, faults, nf)
        self._draw_paging_graph(pages, faults)
        self._set_status(
            f'{algo} complete — {total} page fault(s), '
            f'hit ratio {hits/len(pages)*100:.1f}%')

    def _reset_paging(self):
        self._pg_ref_e.delete(0, tk.END)
        self._pg_ref_e.insert(0, 'e.g. 7 0 1 2 0 3 0 4')
        self._pg_ref_e.config(fg=COL_GRAY)
        self._pg_frm_e.delete(0, tk.END)
        self._pg_frm_e.insert(0, 'e.g. 3')
        self._pg_frm_e.config(fg=COL_GRAY)
        self._pg_algo_var.set('LRU')
        for box in (self._pg_faults_lbl, self._pg_hit_lbl, self._pg_total_lbl):
            box._value_label.config(text='--')
        for w in self._pg_tree_frame.winfo_children():
            w.destroy()
        self._pg_placeholder = tk.Label(
            self._pg_tree_frame,
            text='Run a simulation to see results',
            font=('Inter', 11), bg=BG_CARD, fg=COL_GRAY, pady=40)
        self._pg_placeholder.pack()
        self._pg_draw_empty_graph()
        self._set_status('Paging tab reset')

    def _draw_paging_table(self, pages, snaps, faults, nf):
        for w in self._pg_tree_frame.winfo_children():
            w.destroy()

        cols = ['Step', 'Page'] + [f'Frame {i+1}' for i in range(nf)] + ['Fault?']
        tv = ttk.Treeview(self._pg_tree_frame, columns=cols,
                          show='headings', style='Dark.Treeview',
                          height=min(len(pages), 14))
        sy = ttk.Scrollbar(self._pg_tree_frame, orient='vertical',
                            command=tv.yview)
        sx = ttk.Scrollbar(self._pg_tree_frame, orient='horizontal',
                            command=tv.xview)
        tv.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side='right', fill='y')
        sx.pack(side='bottom', fill='x')
        tv.pack(fill='both', expand=True)

        for c in cols:
            tv.heading(c, text=c)
            tv.column(c, width=68, anchor='center')

        tv.tag_configure('fault', background='#7f1d1d', foreground='white')
        tv.tag_configure('hit',   background='#14532d', foreground='white')

        for i, page in enumerate(pages):
            row = [i+1, page]
            for j in range(nf):
                row.append(snaps[i][j] if j < len(snaps[i]) else '-')
            row.append('FAULT' if faults[i] else 'HIT')
            tag = 'fault' if faults[i] else 'hit'
            tv.insert('', tk.END, values=row, tags=(tag,))

    def _pg_draw_empty_graph(self):
        ax = self._pg_ax
        ax.clear()
        ax.set_facecolor('#0d1117')
        self._pg_fig.patch.set_facecolor(BG_CARD)
        ax.set_xlabel('Step', color=TXT_SEC, fontsize=9)
        ax.set_ylabel('Cumulative Faults', color=TXT_SEC, fontsize=9)
        ax.tick_params(colors=TXT_SEC, labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor(BDR)
        self._pg_canvas.draw()

    def _draw_paging_graph(self, pages, faults):
        ax = self._pg_ax
        ax.clear()
        ax.set_facecolor('#0d1117')
        self._pg_fig.patch.set_facecolor(BG_CARD)

        cum = []
        c = 0
        for f in faults:
            if f:
                c += 1
            cum.append(c)

        xs = list(range(1, len(pages)+1))
        ax.fill_between(xs, cum, alpha=0.25, color='#58a6ff')
        ax.plot(xs, cum, color='#58a6ff', linewidth=2)
        fault_xs = [xs[i] for i in range(len(faults)) if faults[i]]
        fault_ys = [cum[i]  for i in range(len(faults)) if faults[i]]
        ax.scatter(fault_xs, fault_ys, color='#f85149', zorder=5, s=40)

        ax.set_xlabel('Step', color=TXT_SEC, fontsize=9)
        ax.set_ylabel('Cumulative Faults', color=TXT_SEC, fontsize=9)
        ax.tick_params(colors=TXT_SEC, labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor(BDR)
        ax.set_xlim(1, len(pages))
        ax.set_ylim(0, max(cum, default=1) + 1)
        self._pg_fig.tight_layout()
        self._pg_canvas.draw()

    # ══════════════════════════════════════════════════════════════
    #  TAB 2 — SEGMENTATION  (with First/Best/Worst + Compact)
    # ══════════════════════════════════════════════════════════════

    def _build_segmentation_page(self):
        page = tk.Frame(self.tab_frame, bg=BG_DARK)

        # ── Left column ──────────────────────────────────────────
        left = tk.Frame(page, bg=BG_DARK, width=310)
        left.pack(side='left', fill='y', padx=(0, 14))
        left.pack_propagate(False)
        self._build_seg_input(left)

        # ── Right column ─────────────────────────────────────────
        right = tk.Frame(page, bg=BG_DARK)
        right.pack(side='left', fill='both', expand=True)

        # Allocation results table
        res_card = Card(right)
        res_card.pack(fill='both', expand=True, pady=(0, 10))

        hdr = tk.Frame(res_card, bg=BG_CARD)
        hdr.pack(fill='x', padx=12, pady=(10, 4))
        Label(hdr, 'Allocation Results', size=12, bold=True,
              bg=BG_CARD).pack(side='left')
        self._seg_status_lbl = tk.Label(
            hdr, text='Add segments and run',
            font=('Inter', 9), bg=BG_CARD, fg=TXT_SEC)
        self._seg_status_lbl.pack(side='right')

        self._seg_tree_frame = tk.Frame(res_card, bg=BG_CARD)
        self._seg_tree_frame.pack(fill='both', expand=True,
                                  padx=12, pady=(0, 8))
        tk.Label(self._seg_tree_frame,
                 text='Run segmentation to see results',
                 font=('Inter', 11), bg=BG_CARD, fg=COL_GRAY,
                 pady=30).pack()

        # Stats row
        stats_card = Card(right)
        stats_card.pack(fill='x', pady=(0, 10))
        sf = tk.Frame(stats_card, bg=BG_CARD)
        sf.pack(fill='x', padx=12, pady=10)
        self._seg_used_box  = self._stat_box(sf, 'Used',          '--', COL_GREEN)
        self._seg_free_box  = self._stat_box(sf, 'Free',          '--', COL_AMBE)
        self._seg_frag_box  = self._stat_box(sf, 'Fragmentation', '--', COL_RED)
        self._seg_used_box.pack(side='left', padx=(0, 8))
        self._seg_free_box.pack(side='left', padx=(0, 8))
        self._seg_frag_box.pack(side='left')

        # Memory diagram card
        diag_card = Card(right)
        diag_card.pack(fill='x')
        Label(diag_card, '  Memory Visualization', size=12, bold=True,
              bg=BG_CARD).pack(anchor='w', pady=(10, 4))

        self._seg_fig_frame = tk.Frame(diag_card, bg=BG_CARD)
        self._seg_fig_frame.pack(fill='x', padx=12, pady=(0, 10))

        self._seg_fig = Figure(figsize=(6, 1.2), facecolor=BG_CARD)
        self._seg_ax  = self._seg_fig.add_subplot(111)
        self._seg_canvas = FigureCanvasTkAgg(self._seg_fig, self._seg_fig_frame)
        self._seg_canvas.get_tk_widget().pack(fill='x')
        self._seg_draw_empty()

        # ── Compact diff panel (initially hidden) ─────────────────
        self._compact_frame = tk.Frame(diag_card, bg='#0d1117',
                                       highlightthickness=1,
                                       highlightbackground=BDR)
        # not packed until Compact is run

        self._build_compact_diff(self._compact_frame)

        return page

    def _build_seg_input(self, parent):
        """Build the left-column input form for the segmentation tab."""
        card = Card(parent)
        card.pack(fill='x', pady=(0, 10))

        Label(card, '  Add Segment', size=12, bold=True,
              bg=BG_CARD).pack(anchor='w', pady=(10, 6))

        f = tk.Frame(card, bg=BG_CARD)
        f.pack(fill='x', padx=12, pady=(0, 8))

        Label(f, 'Segment Name', size=9, bold=True,
              colour=TXT_SEC, bg=BG_CARD).pack(anchor='w', pady=(4, 2))
        self._sn_wrap, self._sn_e = styled_entry(f, 'e.g. Code, Stack', 30)
        self._sn_wrap.pack(fill='x', pady=(0, 6))

        Label(f, 'Segment Size (KB)', size=9, bold=True,
              colour=TXT_SEC, bg=BG_CARD).pack(anchor='w', pady=(0, 2))
        self._ss_wrap, self._ss_e = styled_entry(f, 'e.g. 100', 30)
        self._ss_wrap.pack(fill='x', pady=(0, 6))

        Label(f, 'Total Memory (KB)', size=9, bold=True,
              colour=TXT_SEC, bg=BG_CARD).pack(anchor='w', pady=(0, 2))
        self._tm_wrap, self._tm_e = styled_entry(f, '512', 30)
        self._tm_wrap.pack(fill='x', pady=(0, 6))

        # ── Fit Strategy dropdown ─────────────────────────────────
        Label(f, 'Fit Strategy', size=9, bold=True,
              colour=TXT_SEC, bg=BG_CARD).pack(anchor='w', pady=(0, 2))
        self._fit_var = tk.StringVar(value='First Fit')
        self._fit_cb  = styled_dropdown(
            f, ['First Fit', 'Best Fit', 'Worst Fit'], self._fit_var, 28)
        self._fit_cb.pack(fill='x', pady=(0, 2))
        self._fit_cb.bind('<<ComboboxSelected>>', self._update_fit_hint)

        self._fit_hint = tk.Label(
            f, wraplength=260, justify='left',
            font=('Inter', 8), bg=BG_CARD, fg=COL_GRAY)
        self._fit_hint.pack(anchor='w', pady=(0, 6))
        self._update_fit_hint()

        # Buttons
        bf = tk.Frame(card, bg=BG_CARD)
        bf.pack(fill='x', padx=12, pady=(0, 8))
        styled_btn(bf, '+ Add Segment',
                   self._add_segment, '#238636', '#2ea043').pack(
            fill='x', pady=(0, 4))
        styled_btn(bf, '▶  Run Segmentation',
                   self._run_segmentation, COL_BLUE, '#388bfd').pack(
            fill='x', pady=(0, 4))
        styled_btn(bf, 'Clear All',
                   self._clear_segments, '#da3633', '#f85149').pack(
            fill='x', pady=(0, 4))

        # Compact button (disabled until a run happens)
        self._compact_btn = styled_btn(
            bf, '⚡ Compact Memory',
            self._compact_memory, '#7c3aed', '#9333ea')
        self._compact_btn.pack(fill='x')
        self._compact_btn.config(state='disabled',
                                  bg='#21262d', fg='#484f58')

        tk.Label(bf,
                 text='Compaction merges scattered free holes into\none contiguous block at the cost of copying.',
                 font=('Inter', 7), bg=BG_CARD, fg=COL_GRAY,
                 justify='left').pack(anchor='w', pady=(4, 0))

        # Segment list
        list_card = tk.Frame(parent, bg=BG_CARD,
                             highlightthickness=1, highlightbackground=BDR)
        list_card.pack(fill='x')

        lh = tk.Frame(list_card, bg='#21262d')
        lh.pack(fill='x')
        tk.Label(lh, text='Segments List', font=('Inter', 10, 'bold'),
                 bg='#21262d', fg=TXT_PRI, padx=10, pady=6).pack(side='left')
        self._seg_count_lbl = tk.Label(
            lh, text='0 segments', font=('Inter', 9),
            bg='#21262d', fg=TXT_SEC, padx=10)
        self._seg_count_lbl.pack(side='right')

        self._seg_list_frame = tk.Frame(list_card, bg=BG_CARD)
        self._seg_list_frame.pack(fill='x')
        tk.Label(self._seg_list_frame,
                 text='No segments added',
                 font=('Inter', 10), bg=BG_CARD, fg=COL_GRAY,
                 pady=20).pack()

    def _update_fit_hint(self, event=None):
        hints = {
            'First Fit': 'Scans from the start; uses the first hole large enough. Fast but can leave awkward fragments.',
            'Best Fit':  'Searches entire free list; picks the smallest fitting hole. Minimises waste per allocation.',
            'Worst Fit': 'Picks the largest hole. Leaves bigger remnants for future large segments.',
        }
        self._fit_hint.config(text=hints.get(self._fit_var.get(), ''))

    def _build_compact_diff(self, parent):
        """Build the before/after compaction visualisation inside parent."""
        tk.Label(parent, text='Compaction — Before vs After',
                 font=('Inter', 10, 'bold'), bg='#0d1117', fg=TXT_PRI,
                 padx=12, pady=8).pack(anchor='w')

        # Before diagram
        bf = tk.Frame(parent, bg='#0d1117')
        bf.pack(fill='x', padx=12, pady=(0, 6))
        tk.Label(bf, text='Before compaction',
                 font=('Inter', 8), bg='#0d1117', fg=TXT_SEC).pack(anchor='w')
        self._compact_before_fig = Figure(figsize=(5, 0.6), facecolor='#0d1117')
        self._compact_before_ax  = self._compact_before_fig.add_subplot(111)
        self._compact_before_canvas = FigureCanvasTkAgg(
            self._compact_before_fig, bf)
        self._compact_before_canvas.get_tk_widget().pack(fill='x')

        # After diagram
        af = tk.Frame(parent, bg='#0d1117')
        af.pack(fill='x', padx=12, pady=(0, 8))
        tk.Label(af, text='After compaction (one contiguous free block)',
                 font=('Inter', 8), bg='#0d1117', fg=TXT_SEC).pack(anchor='w')
        self._compact_after_fig = Figure(figsize=(5, 0.6), facecolor='#0d1117')
        self._compact_after_ax  = self._compact_after_fig.add_subplot(111)
        self._compact_after_canvas = FigureCanvasTkAgg(
            self._compact_after_fig, af)
        self._compact_after_canvas.get_tk_widget().pack(fill='x')

        # Stats row
        sr = tk.Frame(parent, bg='#0d1117')
        sr.pack(fill='x', padx=12, pady=(0, 10))
        self._cs_before = self._compact_stat(sr, 'Largest Free Before', '--')
        self._cs_after  = self._compact_stat(sr, 'Contiguous Free After', '--')
        self._cs_gain   = self._compact_stat(sr, 'Gain', '--')
        self._cs_before.pack(side='left', padx=(0, 8), expand=True, fill='x')
        self._cs_after.pack( side='left', padx=(0, 8), expand=True, fill='x')
        self._cs_gain.pack(  side='left',               expand=True, fill='x')

        tk.Label(parent,
                 text='Note: Compaction is expensive — every allocated byte must be copied and\n'
                      'base registers updated. Modern OSes avoid it by using paging.',
                 font=('Inter', 7), bg='#0d1117', fg=COL_GRAY,
                 justify='left', padx=12, pady=(0, 8)).pack(anchor='w')

    def _compact_stat(self, parent, label, value):
        box = tk.Frame(parent, bg='#161b22',
                       highlightthickness=1, highlightbackground=BDR)
        tk.Label(box, text=label, font=('Inter', 7, 'bold'),
                 bg='#161b22', fg=TXT_SEC).pack(padx=8, pady=(6, 0))
        lbl = tk.Label(box, text=value,
                       font=('JetBrains Mono', 14, 'bold'),
                       bg='#161b22', fg=COL_GREEN)
        lbl.pack(padx=8, pady=(0, 6))
        box._val = lbl
        return box

    # ── Segmentation logic ────────────────────────────────────────

    def _add_segment(self):
        name = get_entry(self._sn_e, 'e.g. Code, Stack').strip()
        size_str = get_entry(self._ss_e, 'e.g. 100').strip()
        if not name:
            messagebox.showerror('Error', 'Please enter a segment name.')
            return
        try:
            size = int(size_str)
            assert size >= 1
        except Exception:
            messagebox.showerror('Error', 'Segment size must be a positive integer.')
            return
        self.segments.append({'name': name, 'size': size})
        self._refresh_seg_list()
        self._sn_e.delete(0, tk.END)
        self._sn_e.insert(0, 'e.g. Code, Stack')
        self._sn_e.config(fg=COL_GRAY)
        self._ss_e.delete(0, tk.END)
        self._ss_e.insert(0, 'e.g. 100')
        self._ss_e.config(fg=COL_GRAY)
        self._set_status(f'Added "{name}" ({size} KB). Total segments: {len(self.segments)}')

    def _delete_segment(self, idx):
        removed = self.segments.pop(idx)
        self._refresh_seg_list()
        self._set_status(f'Removed "{removed["name"]}". Remaining: {len(self.segments)}')

    def _refresh_seg_list(self):
        for w in self._seg_list_frame.winfo_children():
            w.destroy()
        self._seg_count_lbl.config(
            text=f'{len(self.segments)} segment{"s" if len(self.segments)!=1 else ""}')

        if not self.segments:
            tk.Label(self._seg_list_frame, text='No segments added',
                     font=('Inter', 10), bg=BG_CARD, fg=COL_GRAY,
                     pady=20).pack()
            return

        for i, seg in enumerate(self.segments):
            row = tk.Frame(self._seg_list_frame, bg=BG_CARD)
            row.pack(fill='x', padx=4, pady=1)
            tk.Frame(row, bg=BDR, width=1).pack(side='left', fill='y')
            tk.Label(row, text=seg['name'],
                     font=('Inter', 10, 'bold'),
                     bg=BG_CARD, fg=TXT_PRI,
                     padx=10, pady=6).pack(side='left')
            tk.Label(row, text=f'{seg["size"]} KB',
                     font=('JetBrains Mono', 9),
                     bg=BG_CARD, fg=TXT_SEC).pack(side='left')
            del_btn = tk.Button(
                row, text='✕',
                font=('Inter', 9),
                bg=BG_CARD, fg=COL_GRAY,
                activebackground=BG_CARD, activeforeground=COL_RED,
                relief=tk.FLAT, bd=0, cursor='hand2',
                command=lambda i=i: self._delete_segment(i))
            del_btn.pack(side='right', padx=8)

    def _clear_segments(self):
        self.segments = []
        self.last_seg_result = None
        self._refresh_seg_list()
        for w in self._seg_tree_frame.winfo_children():
            w.destroy()
        tk.Label(self._seg_tree_frame,
                 text='Run segmentation to see results',
                 font=('Inter', 11), bg=BG_CARD, fg=COL_GRAY,
                 pady=30).pack()
        self._seg_status_lbl.config(text='Add segments and run', fg=TXT_SEC)
        for box in (self._seg_used_box, self._seg_free_box, self._seg_frag_box):
            box._value_label.config(text='--')
        self._compact_btn.config(state='disabled', bg='#21262d', fg='#484f58')
        self._compact_frame.pack_forget()
        self._seg_draw_empty()
        self._set_status('Segmentation cleared')

    def _run_segmentation(self):
        if not self.segments:
            messagebox.showerror('Error', 'Please add at least one segment.')
            return
        tm_str = get_entry(self._tm_e, '512').strip()
        try:
            total_mem = int(tm_str) if tm_str else 512
            assert total_mem >= 1
        except Exception:
            messagebox.showerror('Error', 'Total memory must be a positive integer.')
            return

        strategy_map = {'First Fit': 'first', 'Best Fit': 'best', 'Worst Fit': 'worst'}
        strategy = strategy_map[self._fit_var.get()]

        self._set_status('Running segmentation…')
        allocs, stats, free_list = simulate_segmentation(
            self.segments, total_mem, strategy)

        self.last_seg_result = {
            'allocs': allocs, 'stats': stats,
            'free_list': free_list, 'total_mem': total_mem,
            'strategy': strategy,
        }

        self._draw_seg_table(allocs, strategy)
        self._draw_seg_diagram(allocs, total_mem)
        self._update_seg_stats(stats)

        failed = sum(1 for a in allocs if a['status'] == 'Failed')
        self._seg_status_lbl.config(
            text=f'{failed} failed' if failed else 'All allocated',
            fg=COL_RED if failed else COL_GREEN)

        has_alloc = any(a['status'] == 'Allocated' for a in allocs)
        if has_alloc:
            self._compact_btn.config(state='normal', bg='#7c3aed', fg='white')
        else:
            self._compact_btn.config(state='disabled', bg='#21262d', fg='#484f58')

        self._compact_frame.pack_forget()
        self._set_status(
            f'Segmentation ({self._fit_var.get()}) complete — '
            f'{len(allocs)} segment(s), {failed} failed')

    def _draw_seg_table(self, allocs, strategy):
        for w in self._seg_tree_frame.winfo_children():
            w.destroy()

        strategy_label = {'first': 'First Fit',
                          'best':  'Best Fit',
                          'worst': 'Worst Fit'}.get(strategy, strategy)

        cols = ['Segment', 'Base Addr', 'Size (KB)',
                'End Addr', 'Hole (KB)', 'Strategy', 'Status']
        tv = ttk.Treeview(self._seg_tree_frame, columns=cols,
                          show='headings', style='Dark.Treeview',
                          height=min(len(allocs)+1, 12))
        sy = ttk.Scrollbar(self._seg_tree_frame, orient='vertical',
                            command=tv.yview)
        tv.configure(yscrollcommand=sy.set)
        sy.pack(side='right', fill='y')
        tv.pack(fill='both', expand=True)

        widths = [90, 80, 80, 80, 80, 80, 90]
        for c, w in zip(cols, widths):
            tv.heading(c, text=c)
            tv.column(c, width=w, anchor='center')

        tv.tag_configure('ok',  background='#14532d', foreground='white')
        tv.tag_configure('bad', background='#7f1d1d', foreground='white')

        for a in allocs:
            row = [a['name'], a['base'], a['size'], a['end'],
                   a['hole_size'] if a['hole_size'] is not None else '—',
                   strategy_label, a['status']]
            tv.insert('', tk.END, values=row,
                      tags=('ok' if a['status'] == 'Allocated' else 'bad',))

    def _update_seg_stats(self, stats):
        self._seg_used_box._value_label.config(
            text=f'{stats["used_memory"]} KB')
        self._seg_free_box._value_label.config(
            text=f'{stats["free_memory"]} KB')
        self._seg_frag_box._value_label.config(
            text=f'{stats["external_fragmentation"]} KB')

    def _seg_draw_empty(self):
        ax = self._seg_ax
        ax.clear()
        ax.set_facecolor('#21262d')
        self._seg_fig.patch.set_facecolor(BG_CARD)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        ax.text(0.5, 0.5, 'Run segmentation to see memory layout',
                ha='center', va='center',
                color=COL_GRAY, fontsize=9, transform=ax.transAxes)
        self._seg_fig.tight_layout()
        self._seg_canvas.draw()

    def _draw_seg_diagram(self, allocs, total_mem, compacted=False):
        """Draw the horizontal memory bar.

        If compacted=True, draw all allocated segments contiguously
        starting at address 0, with free space at the end.
        """
        ax = self._seg_ax
        ax.clear()
        ax.set_facecolor('#0d1117')
        self._seg_fig.patch.set_facecolor(BG_CARD)
        ax.set_xlim(0, total_mem)
        ax.set_ylim(0, 1)
        ax.axis('off')

        if compacted:
            # Re-position allocated segments contiguously
            cursor = 0
            allocated = [a for a in allocs if a['status'] == 'Allocated']
            for ci, a in enumerate(allocated):
                colour = SEG_COLOURS[ci % len(SEG_COLOURS)]
                rect = mpatches.FancyBboxPatch(
                    (cursor, 0.1), a['size'], 0.8,
                    boxstyle='square,pad=0', color=colour)
                ax.add_patch(rect)
                if a['size'] > total_mem * 0.06:
                    ax.text(cursor + a['size']/2, 0.5,
                            f'{a["name"]}\n{a["size"]}KB',
                            ha='center', va='center',
                            color='white', fontsize=7, fontweight='bold')
                cursor += a['size']
            if cursor < total_mem:
                rect = mpatches.FancyBboxPatch(
                    (cursor, 0.1), total_mem - cursor, 0.8,
                    boxstyle='square,pad=0', color='#30363d')
                ax.add_patch(rect)
                ax.text(cursor + (total_mem - cursor)/2, 0.5,
                        f'FREE\n{total_mem - cursor} KB',
                        ha='center', va='center',
                        color=TXT_SEC, fontsize=7, style='italic')
        else:
            cursor = 0
            ci = 0
            for a in allocs:
                if a['status'] == 'Allocated':
                    colour = SEG_COLOURS[ci % len(SEG_COLOURS)]
                    rect = mpatches.FancyBboxPatch(
                        (cursor, 0.1), a['size'], 0.8,
                        boxstyle='square,pad=0', color=colour)
                    ax.add_patch(rect)
                    if a['size'] > total_mem * 0.06:
                        ax.text(cursor + a['size']/2, 0.5,
                                f'{a["name"]}\n{a["size"]}KB',
                                ha='center', va='center',
                                color='white', fontsize=7, fontweight='bold')
                    cursor += a['size']
                    ci += 1

            if cursor < total_mem:
                rect = mpatches.FancyBboxPatch(
                    (cursor, 0.1), total_mem - cursor, 0.8,
                    boxstyle='square,pad=0', color='#30363d')
                ax.add_patch(rect)
                ax.text(cursor + (total_mem - cursor)/2, 0.5,
                        f'FREE\n{total_mem - cursor} KB',
                        ha='center', va='center',
                        color=TXT_SEC, fontsize=7, style='italic')

        ax.text(0, -0.1, '0', ha='center', va='top',
                color=TXT_SEC, fontsize=7, transform=ax.transData)
        ax.text(total_mem, -0.1, f'{total_mem} KB', ha='center', va='top',
                color=TXT_SEC, fontsize=7, transform=ax.transData)

        self._seg_fig.tight_layout()
        self._seg_canvas.draw()

    # ── Compact Memory ────────────────────────────────────────────

    def _compact_memory(self):
        if not self.last_seg_result:
            return
        r = self.last_seg_result
        allocs    = r['allocs']
        total_mem = r['total_mem']
        free_list = r['free_list']

        allocated  = [a for a in allocs if a['status'] == 'Allocated']
        used_mem   = sum(a['size'] for a in allocated)
        free_total = total_mem - used_mem

        largest_before = max((h['size'] for h in free_list), default=0)
        gained = free_total - largest_before

        # Redraw main diagram in compacted state
        self._draw_seg_diagram(allocs, total_mem, compacted=True)

        # Show diff panel
        self._compact_frame.pack(fill='x', padx=0, pady=(8, 0))

        self._draw_compact_bar(self._compact_before_ax,
                               self._compact_before_canvas,
                               largest_before, total_mem,
                               colour='#da3633',
                               label=f'{largest_before} KB largest free hole')

        self._draw_compact_bar(self._compact_after_ax,
                               self._compact_after_canvas,
                               free_total, total_mem,
                               colour='#238636',
                               label=f'{free_total} KB contiguous')

        self._cs_before._val.config(text=f'{largest_before} KB')
        self._cs_after._val.config(text=f'{free_total} KB')
        self._cs_gain._val.config(
            text=f'+{gained} KB' if gained >= 0 else f'{gained} KB')

        self._set_status(
            f'Compaction complete — free space merged '
            f'{largest_before} KB → {free_total} KB contiguous')

    def _draw_compact_bar(self, ax, canvas, value, total, colour, label):
        ax.clear()
        ax.set_facecolor('#0d1117')
        ax.figure.patch.set_facecolor('#0d1117')
        ax.set_xlim(0, total)
        ax.set_ylim(0, 1)
        ax.axis('off')

        filled = max(value, 0)
        if filled > 0:
            rect = mpatches.FancyBboxPatch(
                (0, 0.15), filled, 0.7,
                boxstyle='square,pad=0', color=colour, alpha=0.85)
            ax.add_patch(rect)

        # Background track
        bg_rect = mpatches.FancyBboxPatch(
            (0, 0.15), total, 0.7,
            boxstyle='square,pad=0', color='#21262d', zorder=0)
        ax.add_patch(bg_rect)
        if filled > 0:
            ax.add_patch(rect)

        pct = filled / total * 100 if total else 0
        ax.text(filled / 2 if filled > 0 else total/2,
                0.5, label,
                ha='center', va='center',
                color='white', fontsize=8, fontweight='bold',
                clip_on=True)
        ax.text(total, 0.5, f'{pct:.1f}%',
                ha='right', va='center',
                color=TXT_SEC, fontsize=7)
        ax.figure.tight_layout()
        canvas.draw()

    # ══════════════════════════════════════════════════════════════
    #  TAB 3 — COMPARISON (LRU vs Optimal)
    # ══════════════════════════════════════════════════════════════

    def _build_comparison_page(self):
        page = tk.Frame(self.tab_frame, bg=BG_DARK)

        # Config card (top)
        cfg = Card(page)
        cfg.pack(fill='x', pady=(0, 10))

        hdr = tk.Frame(cfg, bg=BG_CARD)
        hdr.pack(fill='x', padx=12, pady=(10, 6))
        Label(hdr, 'Algorithm Comparison', size=12, bold=True,
              bg=BG_CARD).pack(side='left')

        inp = tk.Frame(cfg, bg=BG_CARD)
        inp.pack(fill='x', padx=12, pady=(0, 10))

        # Page reference
        tk.Frame(inp, bg=BG_CARD).pack(side='left', fill='x', expand=True)
        left_inp = tk.Frame(inp, bg=BG_CARD)
        left_inp.pack(side='left', fill='x', expand=True)
        Label(left_inp, 'Page Reference String', size=9, bold=True,
              colour=TXT_SEC, bg=BG_CARD).pack(anchor='w', pady=(0, 2))
        self._cmp_ref_wrap, self._cmp_ref_e = styled_entry(
            left_inp, 'e.g. 7 0 1 2 0 3 0 4', 36)
        self._cmp_ref_wrap.pack(fill='x', pady=(0, 0))

        tk.Frame(inp, bg=BG_CARD, width=20).pack(side='left')

        right_inp = tk.Frame(inp, bg=BG_CARD)
        right_inp.pack(side='left', fill='x')
        Label(right_inp, 'Number of Frames', size=9, bold=True,
              colour=TXT_SEC, bg=BG_CARD).pack(anchor='w', pady=(0, 2))
        self._cmp_frm_wrap, self._cmp_frm_e = styled_entry(
            right_inp, 'e.g. 3', 14)
        self._cmp_frm_wrap.pack(fill='x')

        bf = tk.Frame(cfg, bg=BG_CARD)
        bf.pack(fill='x', padx=12, pady=(0, 10))
        styled_btn(bf, '⚡ Compare Algorithms',
                   self._run_comparison, '#238636', '#2ea043').pack(
            side='left', padx=(0, 8))
        styled_btn(bf, '↺ Reset',
                   self._reset_comparison, '#21262d', '#30363d').pack(
            side='left')

        # Summary + chart row
        mid = tk.Frame(page, bg=BG_DARK)
        mid.pack(fill='both', expand=True, pady=(0, 10))

        # Summary table (left)
        sum_card = Card(mid)
        sum_card.pack(side='left', fill='y', padx=(0, 10))
        Label(sum_card, '  Performance Summary', size=11, bold=True,
              bg=BG_CARD).pack(anchor='w', pady=(10, 6))
        self._cmp_summary_frame = tk.Frame(sum_card, bg=BG_CARD)
        self._cmp_summary_frame.pack(padx=12, pady=(0, 10))
        self._build_cmp_summary_table()

        # Analysis box
        self._cmp_analysis = tk.Label(
            sum_card,
            text='Run a comparison to see analysis',
            font=('Inter', 10), bg='#0d1117', fg=TXT_SEC,
            wraplength=300, justify='center', pady=14, padx=12)
        self._cmp_analysis.pack(fill='x', padx=12, pady=(0, 10))

        # Bar chart (right)
        chart_card = Card(mid)
        chart_card.pack(side='left', fill='both', expand=True)
        Label(chart_card, '  Page Fault Comparison', size=11, bold=True,
              bg=BG_CARD).pack(anchor='w', pady=(10, 4))
        self._cmp_chart_frame = tk.Frame(chart_card, bg=BG_CARD)
        self._cmp_chart_frame.pack(fill='both', expand=True, padx=12,
                                   pady=(0, 10))
        self._cmp_fig = Figure(figsize=(4, 3), facecolor=BG_CARD)
        self._cmp_ax  = self._cmp_fig.add_subplot(111)
        self._cmp_canvas = FigureCanvasTkAgg(self._cmp_fig, self._cmp_chart_frame)
        self._cmp_canvas.get_tk_widget().pack(fill='both', expand=True)
        self._draw_cmp_chart_empty()

        # Step-by-step table (bottom)
        step_card = Card(page)
        step_card.pack(fill='both', expand=True)
        Label(step_card, '  Step-by-Step Comparison', size=11, bold=True,
              bg=BG_CARD).pack(anchor='w', pady=(10, 4))
        self._cmp_tree_frame = tk.Frame(step_card, bg=BG_CARD)
        self._cmp_tree_frame.pack(fill='both', expand=True, padx=12,
                                  pady=(0, 10))
        tk.Label(self._cmp_tree_frame,
                 text='Run a comparison to see step-by-step execution',
                 font=('Inter', 11), bg=BG_CARD, fg=COL_GRAY,
                 pady=30).pack()

        return page

    def _build_cmp_summary_table(self):
        """Build the static summary table structure."""
        headers = ['Algorithm', 'Total Faults', 'Hit Ratio', 'Efficiency']
        widths  = [90, 100, 90, 90]
        f = self._cmp_summary_frame

        for col, (h, w) in enumerate(zip(headers, widths)):
            tk.Label(f, text=h, font=('Inter', 9, 'bold'),
                     bg='#21262d', fg=TXT_SEC,
                     width=w//8, relief='flat', pady=6).grid(
                row=0, column=col, sticky='nsew', padx=1, pady=(0, 1))

        # LRU row
        self._cmp_lru_vals = []
        for col in range(4):
            lbl = tk.Label(f, text='--',
                           font=('JetBrains Mono', 10),
                           bg='#1f2937', fg='#f97316',
                           width=widths[col]//8, pady=8)
            lbl.grid(row=1, column=col, sticky='nsew', padx=1, pady=1)
            self._cmp_lru_vals.append(lbl)
        self._cmp_lru_vals[0].config(text='LRU', font=('Inter', 10, 'bold'))

        # Optimal row
        self._cmp_opt_vals = []
        for col in range(4):
            lbl = tk.Label(f, text='--',
                           font=('JetBrains Mono', 10),
                           bg='#1f2937', fg='#3b82f6',
                           width=widths[col]//8, pady=8)
            lbl.grid(row=2, column=col, sticky='nsew', padx=1, pady=1)
            self._cmp_opt_vals.append(lbl)
        self._cmp_opt_vals[0].config(text='Optimal', font=('Inter', 10, 'bold'))

    # ── Comparison logic ──────────────────────────────────────────

    def _run_comparison(self):
        ref_str = get_entry(self._cmp_ref_e, 'e.g. 7 0 1 2 0 3 0 4')
        frm_str = get_entry(self._cmp_frm_e, 'e.g. 3')
        if not ref_str:
            messagebox.showerror('Error', 'Please enter a page reference string.')
            return
        pages = parse_page_reference(ref_str)
        if not pages:
            messagebox.showerror('Error', 'Invalid page reference string.')
            return
        try:
            nf = int(frm_str)
            assert nf >= 1
        except Exception:
            messagebox.showerror('Error', 'Frames must be a positive integer.')
            return

        self._set_status('Running comparison…')
        lru_snaps, lru_faults, lru_total = simulate_lru(pages, nf)
        opt_snaps, opt_faults, opt_total = simulate_optimal(pages, nf)
        n = len(pages)

        lru_hit = (n - lru_total) / n * 100
        opt_hit = (n - opt_total) / n * 100
        lru_eff = (n - lru_total) / lru_total * 100 if lru_total else float('inf')
        opt_eff = (n - opt_total) / opt_total * 100 if opt_total else float('inf')

        def eff_str(v):
            return f'{v:.1f}%' if v != float('inf') else 'N/A'

        self._cmp_lru_vals[1].config(text=str(lru_total))
        self._cmp_lru_vals[2].config(text=f'{lru_hit:.1f}%')
        self._cmp_lru_vals[3].config(text=eff_str(lru_eff))
        self._cmp_opt_vals[1].config(text=str(opt_total))
        self._cmp_opt_vals[2].config(text=f'{opt_hit:.1f}%')
        self._cmp_opt_vals[3].config(text=eff_str(opt_eff))

        self._draw_cmp_chart(lru_total, opt_total)
        self._draw_cmp_step_table(
            pages, lru_snaps, lru_faults, opt_snaps, opt_faults, nf)

        if opt_total < lru_total:
            diff = lru_total - opt_total
            analysis = (f'Optimal produced {diff} fewer fault(s) than LRU '
                        f'({diff/lru_total*100:.1f}% improvement).')
            self._cmp_analysis.config(fg=COL_GREEN,
                                       bg='rgba(35,134,54,0.1)' if False else '#0d1117')
        elif lru_total < opt_total:
            diff = opt_total - lru_total
            analysis = (f'LRU produced {diff} fewer fault(s) than Optimal '
                        f'({diff/opt_total*100:.1f}% improvement).')
            self._cmp_analysis.config(fg=COL_AMBE)
        else:
            analysis = 'Both algorithms produced the same number of page faults.'
            self._cmp_analysis.config(fg=TXT_SEC)
        self._cmp_analysis.config(text=analysis)
        self._set_status(
            f'Comparison complete — LRU {lru_total} fault(s), '
            f'Optimal {opt_total} fault(s)')

    def _reset_comparison(self):
        self._cmp_ref_e.delete(0, tk.END)
        self._cmp_ref_e.insert(0, 'e.g. 7 0 1 2 0 3 0 4')
        self._cmp_ref_e.config(fg=COL_GRAY)
        self._cmp_frm_e.delete(0, tk.END)
        self._cmp_frm_e.insert(0, 'e.g. 3')
        self._cmp_frm_e.config(fg=COL_GRAY)
        for lbl in self._cmp_lru_vals[1:] + self._cmp_opt_vals[1:]:
            lbl.config(text='--')
        self._cmp_analysis.config(
            text='Run a comparison to see analysis', fg=TXT_SEC)
        self._draw_cmp_chart_empty()
        for w in self._cmp_tree_frame.winfo_children():
            w.destroy()
        tk.Label(self._cmp_tree_frame,
                 text='Run a comparison to see step-by-step execution',
                 font=('Inter', 11), bg=BG_CARD, fg=COL_GRAY,
                 pady=30).pack()
        self._set_status('Comparison tab reset')

    def _draw_cmp_chart_empty(self):
        ax = self._cmp_ax
        ax.clear()
        ax.set_facecolor('#0d1117')
        self._cmp_fig.patch.set_facecolor(BG_CARD)
        ax.set_ylabel('Page Faults', color=TXT_SEC, fontsize=9)
        ax.tick_params(colors=TXT_SEC, labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor(BDR)
        ax.bar(['LRU', 'Optimal'], [0, 0],
               color=['#f97316', '#3b82f6'], width=0.5)
        self._cmp_fig.tight_layout()
        self._cmp_canvas.draw()

    def _draw_cmp_chart(self, lru_total, opt_total):
        ax = self._cmp_ax
        ax.clear()
        ax.set_facecolor('#0d1117')
        self._cmp_fig.patch.set_facecolor(BG_CARD)

        bars = ax.bar(['LRU', 'Optimal'], [lru_total, opt_total],
                      color=['#f97316', '#3b82f6'], width=0.5,
                      zorder=3)
        for bar, val in zip(bars, [lru_total, opt_total]):
            ax.text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() + 0.15,
                    str(val),
                    ha='center', va='bottom',
                    color=TXT_PRI, fontsize=11, fontweight='bold')

        ax.set_ylabel('Page Faults', color=TXT_SEC, fontsize=9)
        ax.tick_params(colors=TXT_SEC, labelsize=9)
        ax.set_facecolor('#0d1117')
        for spine in ax.spines.values():
            spine.set_edgecolor(BDR)
        ax.grid(axis='y', color=BDR, linewidth=0.5, zorder=0)
        ax.set_ylim(0, max(lru_total, opt_total) * 1.3 + 1)
        self._cmp_fig.tight_layout()
        self._cmp_canvas.draw()

    def _draw_cmp_step_table(self, pages,
                              lru_snaps, lru_faults,
                              opt_snaps, opt_faults, nf):
        for w in self._cmp_tree_frame.winfo_children():
            w.destroy()

        cols = ['Step', 'Page',
                'LRU Frames', 'LRU',
                'Optimal Frames', 'Optimal']
        tv = ttk.Treeview(self._cmp_tree_frame, columns=cols,
                          show='headings', style='Dark.Treeview',
                          height=min(len(pages), 14))
        sy = ttk.Scrollbar(self._cmp_tree_frame, orient='vertical',
                            command=tv.yview)
        tv.configure(yscrollcommand=sy.set)
        sy.pack(side='right', fill='y')
        tv.pack(fill='both', expand=True)

        widths = [50, 55, 160, 70, 160, 70]
        for c, w in zip(cols, widths):
            tv.heading(c, text=c)
            tv.column(c, width=w, anchor='center')

        tv.tag_configure('both_fault', background='#7f1d1d', foreground='white')
        tv.tag_configure('lru_fault',  background='#78350f', foreground='white')
        tv.tag_configure('opt_fault',  background='#1e3a5f', foreground='white')
        tv.tag_configure('both_hit',   background='#14532d', foreground='white')

        for i, page in enumerate(pages):
            lf = lru_faults[i]
            of = opt_faults[i]
            if lf and of:
                tag = 'both_fault'
            elif lf:
                tag = 'lru_fault'
            elif of:
                tag = 'opt_fault'
            else:
                tag = 'both_hit'

            row = [
                i+1, page,
                str(lru_snaps[i]),
                'FAULT' if lf else 'HIT',
                str(opt_snaps[i]),
                'FAULT' if of else 'HIT',
            ]
            tv.insert('', tk.END, values=row, tags=(tag,))


# ─────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    app = VirtualMemoryApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
