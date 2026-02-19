from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from typing import Dict, Callable, Optional, List
from ..engine.models import TalentNode

@dataclass
class NodeView:
    node: TalentNode
    item_id: int
    text_id: int

class Tooltip:
    def __init__(self, widget: tk.Widget):
        self.widget = widget
        self.tip: Optional[tk.Toplevel] = None
        self.label: Optional[tk.Label] = None

    def show(self, x: int, y: int, text: str):
        self.hide()
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x+12}+{y+12}")
        self.label = tk.Label(self.tip, text=text, justify="left",
                              relief="solid", borderwidth=1,
                              font=("Segoe UI", 9), padx=8, pady=6)
        self.label.pack()

    def hide(self):
        if self.tip:
            self.tip.destroy()
            self.tip = None

class TalentTreeEditor(tk.Toplevel):
    """
    Clickable talent tree UI:
    - Hover for tooltip
    - Left click toggles rank (0->1->2..max->0)
    - Enforces prereqs (simple: you can't rank a node unless prereqs have rank>0)
    """
    def __init__(
        self,
        master: tk.Widget,
        talents: Dict[str, TalentNode],
        selected: Dict[str, int],
        *,
        on_apply: Callable[[Dict[str, int]], None],
        title: str = "Talent Tree",
        canvas_w: int = 900,
        canvas_h: int = 520,
    ):
        super().__init__(master)
        self.title(title)
        self.resizable(True, True)

        self.talents = talents
        self.selected = dict(selected or {})
        self.on_apply = on_apply

        self.tooltip = Tooltip(self)
        self.canvas_w = canvas_w
        self.canvas_h = canvas_h

        self._build()

    def _build(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="both", expand=True)

        header = ttk.Frame(top)
        header.pack(fill="x")

        ttk.Label(header, text="Tree").pack(side="left")
        self.tree_var = tk.StringVar(value="All")
        trees = sorted({t.tree for t in self.talents.values()})
        self.tree_combo = ttk.Combobox(header, textvariable=self.tree_var,
                                       values=["All"] + trees, state="readonly", width=18)
        self.tree_combo.pack(side="left", padx=8)
        self.tree_combo.bind("<<ComboboxSelected>>", lambda e: self.render())

        self.points_var = tk.StringVar(value="")
        ttk.Label(header, textvariable=self.points_var).pack(side="right")

        self.canvas = tk.Canvas(top, width=self.canvas_w, height=self.canvas_h)
        self.canvas.pack(fill="both", expand=True, pady=(10, 10))

        btns = ttk.Frame(top)
        btns.pack(fill="x")
        ttk.Button(btns, text="Apply", command=self.apply).pack(side="right")
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="right", padx=8)
        ttk.Button(btns, text="Clear", command=self.clear).pack(side="left")

        self.node_views: Dict[int, NodeView] = {}  # canvas_item_id -> NodeView
        self.text_to_item: Dict[int, int] = {}

        self.canvas.bind("<Motion>", self.on_motion)
        self.canvas.bind("<Leave>", lambda e: self.tooltip.hide())
        self.canvas.bind("<Button-1>", self.on_click)

        self.render()

    def clear(self):
        self.selected = {}
        self.render()

    def apply(self):
        # prune zero ranks
        out = {k: int(v) for k, v in self.selected.items() if int(v) > 0}
        self.on_apply(out)
        self.destroy()

    def _points(self) -> int:
        return sum(int(v) for v in self.selected.values())

    def _can_increase(self, node: TalentNode) -> bool:
        for pid in (node.prereq or []):
            if int(self.selected.get(pid, 0)) <= 0:
                return False
        return True

    def _node_tooltip_text(self, node: TalentNode) -> str:
        rank = int(self.selected.get(node.id, 0))
        lines: List[str] = []
        title = node.name or f"Node {node.id}"
        lines.append(title)
        if node.description:
            lines.append(node.description)
        lines.append("")
        lines.append(f"Tree: {node.tree}")
        lines.append(f"Effect: {node.stat} +{node.value_per_rank} per rank")
        lines.append(f"Rank: {rank}/{node.max_rank}")
        if node.prereq:
            lines.append(f"Prereq: {', '.join(node.prereq)}")
        return "\n".join(lines)

    def _resolve_xy(self, node: TalentNode):
        # If x,y look like 0..1, treat as normalized; else pixels.
        x, y = float(node.x), float(node.y)
        if 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0:
            return x * self.canvas_w, y * self.canvas_h
        return x, y

    def render(self):
        self.canvas.delete("all")
        self.node_views.clear()
        self.text_to_item.clear()

        tree_filter = self.tree_var.get()
        nodes = list(self.talents.values())
        if tree_filter != "All":
            nodes = [n for n in nodes if (n.tree or "General") == tree_filter]

        # draw prereq lines first
        by_id = self.talents
        for n in nodes:
            x1, y1 = self._resolve_xy(n)
            for pid in (n.prereq or []):
                p = by_id.get(pid)
                if not p:
                    continue
                # only draw if prereq is visible in this filter
                if tree_filter != "All" and (p.tree or "General") != tree_filter:
                    continue
                x0, y0 = self._resolve_xy(p)
                self.canvas.create_line(x0, y0, x1, y1, width=2)

        # draw nodes
        r = 22
        for n in nodes:
            x, y = self._resolve_xy(n)
            rank = int(self.selected.get(n.id, 0))
            is_active = rank > 0

            outline = "#ff2d2d" if is_active else "#9fb6c5"
            width = 4 if is_active else 2

            # hex-ish polygon
            pts = []
            for k in range(6):
                ang = (math.pi/3) * k + math.pi/6
                pts.append(x + r*math.cos(ang))
                pts.append(y + r*math.sin(ang))

            item = self.canvas.create_polygon(*pts, outline=outline, fill="", width=width)
            label = str(rank) if rank > 0 else ""
            txt = self.canvas.create_text(x, y, text=label, font=("Segoe UI", 10, "bold"))
            self.node_views[item] = NodeView(node=n, item_id=item, text_id=txt)
            self.text_to_item[txt] = item

        self.points_var.set(f"Points: {self._points()}")

    def _hit_test(self, item_id: int) -> Optional[NodeView]:
        if item_id in self.node_views:
            return self.node_views[item_id]
        if item_id in self.text_to_item:
            return self.node_views.get(self.text_to_item[item_id])
        return None

    def on_motion(self, event):
        ids = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        if not ids:
            self.tooltip.hide()
            return
        nv = self._hit_test(ids[-1])
        if not nv:
            self.tooltip.hide()
            return
        text = self._node_tooltip_text(nv.node)
        # screen coords
        x = self.winfo_rootx() + event.x
        y = self.winfo_rooty() + event.y
        self.tooltip.show(x, y, text)

    def on_click(self, event):
        ids = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        if not ids:
            return
        nv = self._hit_test(ids[-1])
        if not nv:
            return
        node = nv.node
        cur = int(self.selected.get(node.id, 0))

        # increment with prereq enforcement
        nxt = cur + 1
        if nxt > int(node.max_rank):
            nxt = 0

        if nxt > 0 and not self._can_increase(node):
            # can't increase; flash tooltip quickly
            self.tooltip.show(self.winfo_rootx()+event.x, self.winfo_rooty()+event.y,
                              "Prerequisite not met.")
            self.after(700, self.tooltip.hide)
            return

        if nxt == 0:
            self.selected.pop(node.id, None)
        else:
            self.selected[node.id] = nxt

        self.render()
