"""Desktop interface for the rule-based chatbot."""

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
from datetime import datetime

import engine

INK = "#0B111C"
PANEL = "#101A28"
RAISED = "#1A2739"
HAIRLINE = "#22314A"
BRASS = "#C8A96A"
BRASS_LIT = "#DBC48E"
BRASS_DEEP = "#7E6B42"
IVORY = "#EDE7DA"
MUTED = "#8697B0"
JADE = "#6FBF9B"
AMBER = "#D9A05B"
SLATE = "#5D6E88"

PAD = 26
GAP = 18
RADIUS = 16
RAIL_W = 258


def spaced(text):
    return " ".join(text.upper())


class ChatWindow(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title(f"{engine.BOT_NAME} - Rule-Based Chat Engine")
        self.configure(bg=INK)
        self.geometry("1000x700")
        self.minsize(820, 560)

        self._pick_fonts()
        self.messages = []
        self.canvas_w = 700
        self.session_open = True
        self._revert_job = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_header()
        self._build_conversation()
        self._build_rail()
        self._build_composer()

        self.after(120, self._greet)

    def _pick_fonts(self):
        have = set(tkfont.families())

        def first(*names):
            for n in names:
                if n in have:
                    return n
            return "TkDefaultFont"

        display = first("Palatino Linotype", "Georgia", "Book Antiqua",
                        "Times New Roman", "DejaVu Serif")
        body = first("Segoe UI", "Helvetica Neue", "Inter", "Helvetica",
                     "DejaVu Sans")
        mono = first("Consolas", "JetBrains Mono", "SF Mono", "Menlo",
                     "DejaVu Sans Mono", "Courier New")

        self.f_title = (display, 21)
        self.f_body = (body, 11)
        self.f_bubble = (body, 11)
        self.f_rail = (body, 10)
        self.f_micro = (mono, 8)
        self.f_mono = (mono, 9)
        self.f_send = (body, 10, "bold")

    def _build_header(self):
        head = tk.Frame(self, bg=INK)
        head.grid(row=0, column=0, columnspan=2, sticky="ew")
        head.columnconfigure(0, weight=1)

        left = tk.Frame(head, bg=INK)
        left.grid(row=0, column=0, sticky="w", padx=(PAD, 0), pady=(20, 16))
        tk.Label(left, text=spaced("rule-based engine"), bg=INK, fg=BRASS_DEEP,
                 font=self.f_micro).pack(anchor="w")
        tk.Label(left, text=engine.BOT_NAME, bg=INK, fg=IVORY,
                 font=self.f_title).pack(anchor="w", pady=(3, 0))

        right = tk.Frame(head, bg=INK)
        right.grid(row=0, column=1, sticky="e", padx=(0, PAD))
        dot = tk.Canvas(right, width=8, height=8, bg=INK, highlightthickness=0)
        dot.create_oval(1, 1, 7, 7, fill=JADE, outline="")
        dot.pack(side="left", padx=(0, 8))
        tk.Label(right, text=f"{engine.rule_count()} rules  ·  "
                             f"{len(engine.INTENTS)} intents  ·  deterministic",
                 bg=INK, fg=MUTED, font=self.f_micro).pack(side="left")

        tk.Frame(head, bg=HAIRLINE, height=1).grid(
            row=1, column=0, columnspan=2, sticky="ew")

    def _build_conversation(self):
        wrap = tk.Frame(self, bg=PANEL)
        wrap.grid(row=1, column=0, sticky="nsew")
        wrap.rowconfigure(0, weight=1)
        wrap.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(wrap, bg=PANEL, highlightthickness=0, bd=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Thin.Vertical.TScrollbar", gripcount=0, borderwidth=0,
                        relief="flat", troughcolor=PANEL, background=HAIRLINE,
                        darkcolor=PANEL, lightcolor=PANEL, arrowcolor=PANEL)
        style.map("Thin.Vertical.TScrollbar", background=[("active", BRASS_DEEP)])
        style.layout("Thin.Vertical.TScrollbar", [
            ("Vertical.Scrollbar.trough", {"sticky": "ns", "children": [
                ("Vertical.Scrollbar.thumb",
                 {"expand": "1", "sticky": "nswe"})]})])

        bar = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview,
                            style="Thin.Vertical.TScrollbar")
        bar.grid(row=0, column=1, sticky="ns", padx=(0, 4), pady=8)
        self.canvas.configure(yscrollcommand=bar.set)

        self.canvas.bind("<Configure>", self._on_resize)
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.canvas.bind_all(seq, self._on_wheel)

    def _on_resize(self, event):
        if abs(event.width - self.canvas_w) > 3:
            self.canvas_w = event.width
            self._render()

    def _on_wheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-2, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(2, "units")
        else:
            self.canvas.yview_scroll(-1 * (event.delta // 120) * 2, "units")

    def _build_rail(self):
        rail = tk.Frame(self, bg=INK, width=RAIL_W)
        rail.grid(row=1, column=1, rowspan=2, sticky="ns")
        rail.grid_propagate(False)
        tk.Frame(rail, bg=HAIRLINE, width=1).place(x=0, y=0, relheight=1)

        inner = tk.Frame(rail, bg=INK)
        inner.pack(fill="both", expand=True, padx=(21, 18), pady=(22, 18))

        tk.Label(inner, text=spaced("knowledge base"), bg=INK, fg=BRASS_DEEP,
                 font=self.f_micro).pack(anchor="w", pady=(0, 12))

        self.rail_rows = {}
        for name, label, count in engine.intent_rows():
            row = tk.Frame(inner, bg=INK)
            row.pack(fill="x", pady=1)
            marker = tk.Label(row, text="│", bg=INK, fg=HAIRLINE,
                              font=self.f_mono)
            marker.pack(side="left", padx=(0, 9))
            title = tk.Label(row, text=label, bg=INK, fg=MUTED,
                             font=self.f_rail)
            title.pack(side="left")
            tk.Label(row, text=f"{count}", bg=INK, fg=HAIRLINE,
                     font=self.f_micro).pack(side="right")
            self.rail_rows[name] = (marker, title)

        tk.Frame(inner, bg=HAIRLINE, height=1).pack(fill="x", pady=18)

        tk.Label(inner, text=spaced("last trace"), bg=INK, fg=BRASS_DEEP,
                 font=self.f_micro).pack(anchor="w", pady=(0, 10))

        card = tk.Frame(inner, bg=RAISED)
        card.pack(fill="x")
        self.trace_labels = {}
        for key in ("input", "rule", "path"):
            line = tk.Frame(card, bg=RAISED)
            line.pack(fill="x", padx=13, pady=(9 if key == "input" else 0, 9))
            tk.Label(line, text=key.ljust(6), bg=RAISED, fg=SLATE,
                     font=self.f_micro).pack(side="left")
            value = tk.Label(line, text="—", bg=RAISED, fg=MUTED,
                             font=self.f_mono, anchor="w")
            value.pack(side="left", fill="x", expand=True)
            self.trace_labels[key] = value

        legend = tk.Frame(inner, bg=INK)
        legend.pack(fill="x", pady=(16, 0))
        paths = ((JADE, "exact", "whole phrase matched"),
                 (AMBER, "keyword", "word found inside"),
                 (SLATE, "fallback", "no rule applied"))
        for colour, name, meaning in paths:
            line = tk.Frame(legend, bg=INK)
            line.pack(fill="x", pady=2)
            swatch = tk.Canvas(line, width=6, height=6, bg=INK,
                               highlightthickness=0)
            swatch.create_rectangle(0, 0, 6, 6, fill=colour, outline="")
            swatch.pack(side="left", padx=(1, 9))
            tk.Label(line, text=name, bg=INK, fg=colour,
                     font=self.f_micro).pack(side="left")
            tk.Label(line, text=meaning, bg=INK, fg=HAIRLINE,
                     font=self.f_micro).pack(side="right")

        tk.Label(inner, text="Project 1  ·  DecodeLabs", bg=INK, fg=HAIRLINE,
                 font=self.f_micro).pack(side="bottom", anchor="w")

    def _update_trace(self, clean_input, result):
        shown = clean_input if len(clean_input) <= 22 else clean_input[:21] + "…"
        colours = {"exact": JADE, "keyword": AMBER, "fallback": SLATE}
        self.trace_labels["input"].config(text=shown, fg=IVORY)
        self.trace_labels["rule"].config(
            text=result["intent"] or "none", fg=MUTED)
        self.trace_labels["path"].config(
            text=result["path"], fg=colours[result["path"]])

        if self._revert_job:
            self.after_cancel(self._revert_job)
        for marker, title in self.rail_rows.values():
            marker.config(fg=HAIRLINE)
            title.config(fg=MUTED)
        if result["intent"]:
            marker, title = self.rail_rows[result["intent"]]
            marker.config(fg=BRASS)
            title.config(fg=IVORY)
            self._revert_job = self.after(2600, self._dim_rail)

    def _dim_rail(self):
        for marker, title in self.rail_rows.values():
            marker.config(fg=HAIRLINE)
            title.config(fg=MUTED)

    def _build_composer(self):
        bar = tk.Frame(self, bg=INK)
        bar.grid(row=2, column=0, sticky="ew")
        tk.Frame(bar, bg=HAIRLINE, height=1).pack(fill="x")

        chips = tk.Frame(bar, bg=INK)
        chips.pack(fill="x", padx=PAD, pady=(16, 0))
        for text in ("help", "what time is it", "tell me a joke", "what is ai"):
            self._chip(chips, text)

        row = tk.Frame(bar, bg=INK)
        row.pack(fill="x", padx=PAD, pady=(14, 20))

        self.field_border = tk.Frame(row, bg=HAIRLINE)
        self.field_border.pack(side="left", fill="x", expand=True,
                               padx=(0, 12))
        field = tk.Frame(self.field_border, bg=RAISED)
        field.pack(fill="both", expand=True, padx=1, pady=1)

        self.entry = tk.Entry(field, bg=RAISED, fg=IVORY, bd=0,
                              font=self.f_body, insertbackground=BRASS,
                              highlightthickness=0, relief="flat")
        self.entry.pack(fill="x", expand=True, padx=16, pady=13)
        self.entry.bind("<Return>", lambda _e: self._send())
        self.entry.bind("<FocusIn>", self._focus_on)
        self.entry.bind("<FocusOut>", self._focus_off)
        self._placeholder_on()
        self.entry.bind("<KeyPress>", self._placeholder_off)

        self.send = tk.Canvas(row, width=104, height=46, bg=INK,
                              highlightthickness=0)
        self.send.pack(side="left")
        self.send_bg = self._round(self.send, 0, 0, 104, 46, 13, fill=BRASS)
        self.send_text = self.send.create_text(52, 24, text="Send", fill=INK,
                                               font=self.f_send)
        self.send.bind("<Button-1>", lambda _e: self._send())
        self.send.bind("<Enter>", lambda _e: self._send_tint(BRASS_LIT))
        self.send.bind("<Leave>", lambda _e: self._send_tint(BRASS))
        self.send.configure(cursor="hand2")

    def _chip(self, parent, text):
        c = tk.Canvas(parent, height=30, bg=INK, highlightthickness=0,
                      cursor="hand2")
        width = tkfont.Font(font=self.f_micro).measure(text) + 34
        c.configure(width=width)
        c.pack(side="left", padx=(0, 9))
        shape = self._round(c, 0, 0, width, 30, 15, fill=INK,
                            outline=HAIRLINE)
        label = c.create_text(width / 2, 15, text=text, fill=MUTED,
                              font=self.f_micro)

        def enter(_e):
            c.itemconfig(shape, outline=BRASS_DEEP)
            c.itemconfig(label, fill=BRASS)

        def leave(_e):
            c.itemconfig(shape, outline=HAIRLINE)
            c.itemconfig(label, fill=MUTED)

        c.bind("<Enter>", enter)
        c.bind("<Leave>", leave)
        c.bind("<Button-1>", lambda _e: self._send(text))

    def _send_tint(self, colour):
        if self.session_open:
            self.send.itemconfig(self.send_bg, fill=colour)

    def _focus_on(self, _e):
        self.field_border.config(bg=BRASS_DEEP)

    def _focus_off(self, _e):
        self.field_border.config(bg=HAIRLINE)
        if not self.entry.get().strip():
            self._placeholder_on()

    def _placeholder_on(self):
        self.entry.delete(0, "end")
        self.entry.insert(0, f"Message {engine.BOT_NAME}…")
        self.entry.config(fg=SLATE)
        self._placeholder = True

    def _placeholder_off(self, _e=None):
        if getattr(self, "_placeholder", False):
            self.entry.delete(0, "end")
            self.entry.config(fg=IVORY)
            self._placeholder = False

    @staticmethod
    def _round(canvas, x1, y1, x2, y2, r, **kw):
        pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r,
               x2, y2, x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r,
               x1, y1 + r, x1, y1]
        return canvas.create_polygon(pts, smooth=True, **kw)

    def _greet(self):
        self._add("bot", f"Hello. I'm {engine.BOT_NAME}. Every answer I give "
                         f"comes from a rule written in advance - the panel on "
                         f"the right shows which one fired.",
                  meta="session opened")

    def _add(self, role, text, meta=""):
        self.messages.append({
            "role": role,
            "text": text,
            "meta": meta,
            "time": datetime.now().strftime("%H:%M"),
        })
        self._render()

    def _send(self, preset=None):
        if not self.session_open:
            return
        raw = preset if preset is not None else self.entry.get()
        if getattr(self, "_placeholder", False) and preset is None:
            return
        clean = engine.sanitize(raw)
        if not clean:
            return

        self.entry.delete(0, "end")
        self._placeholder = False
        if preset is not None and self.focus_get() is not self.entry:
            self._placeholder_on()
        self._add("user", raw.strip())

        if engine.is_exit(clean):
            self._add("bot", "Session closed. Reopen the window to start "
                             "again.", meta="exit command")
            self._close_session()
            return

        self._add("typing", "· · ·")
        self.after(420, lambda: self._reply(clean))

    def _reply(self, clean):
        self.messages.pop()
        result = engine.respond(clean)
        note = ("no rule matched" if result["path"] == "fallback"
                else f"{result['path']} match  ·  {result['intent']}")
        self._add("bot", result["reply"], meta=note)
        self._update_trace(clean, result)

    def _close_session(self):
        self.session_open = False
        self.entry.config(state="disabled")
        self.send.itemconfig(self.send_bg, fill=RAISED)
        self.send.itemconfig(self.send_text, fill=SLATE)
        self.send.configure(cursor="")

    def _render(self):
        c = self.canvas
        c.delete("all")
        width = max(self.canvas_w, 360)
        limit = max(240, min(470, int(width * 0.62)))
        y = 26

        for msg in self.messages:
            role = msg["role"]
            is_user = role == "user"
            fill = BRASS if is_user else RAISED
            ink = INK if is_user else IVORY
            if role == "typing":
                ink = BRASS

            item = c.create_text(0, 0, text=msg["text"], width=limit,
                                 anchor="nw", font=self.f_bubble, fill=ink)
            x1, y1, x2, y2 = c.bbox(item)
            w, h = x2 - x1, y2 - y1
            box_w = w + 34

            bx = width - PAD - box_w if is_user else PAD
            c.coords(item, bx + 17, y + 13)
            shape = self._round(c, bx, y, bx + box_w, y + h + 26, RADIUS,
                                fill=fill)
            c.tag_lower(shape, item)
            y += h + 26

            caption = msg["meta"] or msg["time"]
            if role != "typing":
                if is_user:
                    c.create_text(width - PAD - 3, y + 7, text=caption,
                                  anchor="ne", font=self.f_micro, fill=SLATE)
                else:
                    colour = BRASS_DEEP if msg["meta"] else SLATE
                    c.create_text(bx + 3, y + 7, text=caption, anchor="nw",
                                  font=self.f_micro, fill=colour)
                y += 15
            y += GAP

        c.configure(scrollregion=(0, 0, width, y + 6))
        c.yview_moveto(1.0)


if __name__ == "__main__":
    ChatWindow().mainloop()
