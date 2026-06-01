import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import json
import os
import re

# ── Colour palette ──────────────────────────────────────────────────────────
COLORS = {
    "bg":           "#F5F7FA",
    "surface":      "#FFFFFF",
    "surface_alt":  "#EEF2F7",
    "primary":      "#C0392B",
    "primary_dark": "#922B21",
    "primary_light":"#FADBD8",
    "secondary":    "#2C3E50",
    "accent":       "#1ABC9C",
    "text":         "#1A1A2E",
    "text_muted":   "#6B7280",
    "border":       "#D1D5DB",
    "success":      "#1ABC9C",
    "success_bg":   "#D5F5EF",
    "danger":       "#C0392B",
    "danger_bg":    "#FADBD8",
    "warning":      "#E67E22",
    "warning_bg":   "#FDEBD0",
    "header_bg":    "#1A1A2E",
    "header_fg":    "#FFFFFF",
    "sidebar_bg":   "#2C3E50",
    "sidebar_fg":   "#ECF0F1",
    "sidebar_sel":  "#C0392B",
}

FONT_FAMILY = "Segoe UI" if os.name == "nt" else "SF Pro Display" if os.uname().sysname == "Darwin" else "DejaVu Sans"
F_H1   = (FONT_FAMILY, 20, "bold")
F_H2   = (FONT_FAMILY, 14, "bold")
F_H3   = (FONT_FAMILY, 11, "bold")
F_BODY = (FONT_FAMILY, 10)
F_SMALL= (FONT_FAMILY, 9)
F_MONO = ("Courier New", 9)

HISTORY_FILE = os.path.join(os.path.expanduser("~"), ".blood_donor_history.json")

HIGH_RISK_CONDITIONS = [
    "hepatitis", "hiv", "aids", "cancer", "leukemia", "heart disease",
    "sickle cell", "tuberculosis", "malaria", "ebola", "chagas",
    "babesiosis", "creutzfeldt", "prion",
]

RISKY_MEDICATIONS = [
    "aspirin", "warfarin", "heparin", "accutane", "isotretinoin",
    "finasteride", "dutasteride", "thalidomide",
]

BLOOD_TYPE_COMPATIBILITY = {
    "O-":  {"donates_to": ["A+","A-","B+","B-","AB+","AB-","O+","O-"], "receives_from": ["O-"]},
    "O+":  {"donates_to": ["A+","B+","AB+","O+"],                      "receives_from": ["O+","O-"]},
    "A-":  {"donates_to": ["A+","A-","AB+","AB-"],                     "receives_from": ["A-","O-"]},
    "A+":  {"donates_to": ["A+","AB+"],                                 "receives_from": ["A+","A-","O+","O-"]},
    "B-":  {"donates_to": ["B+","B-","AB+","AB-"],                     "receives_from": ["B-","O-"]},
    "B+":  {"donates_to": ["B+","AB+"],                                 "receives_from": ["B+","B-","O+","O-"]},
    "AB-": {"donates_to": ["AB+","AB-"],                                "receives_from": ["A-","B-","AB-","O-"]},
    "AB+": {"donates_to": ["AB+"],                                      "receives_from": ["A+","A-","B+","B-","AB+","AB-","O+","O-"]},
}


# ── Utility helpers ──────────────────────────────────────────────────────────

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_history(records):
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(records[-100:], f, indent=2)
    except Exception:
        pass


# ── Custom widgets ───────────────────────────────────────────────────────────

class Divider(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, height=1, bg=COLORS["border"], **kw)


class Card(tk.Frame):
    """White raised card with optional title."""
    def __init__(self, parent, title="", **kw):
        super().__init__(parent, bg=COLORS["surface"],
                         relief="flat", bd=0,
                         highlightthickness=1,
                         highlightbackground=COLORS["border"], **kw)
        if title:
            tk.Label(self, text=title, font=F_H3, bg=COLORS["surface"],
                     fg=COLORS["secondary"]).pack(anchor="w", padx=14, pady=(10, 4))
            Divider(self).pack(fill="x", padx=14)


class IconButton(tk.Button):
    def __init__(self, parent, text, command, color=None, **kw):
        bg = color or COLORS["primary"]
        super().__init__(parent, text=text, command=command,
                         bg=bg, fg="white",
                         font=F_BODY, relief="flat", bd=0,
                         padx=14, pady=6, cursor="hand2",
                         activebackground=COLORS["primary_dark"],
                         activeforeground="white", **kw)
        self.bind("<Enter>", lambda e: self.config(bg=COLORS["primary_dark"] if color is None else self._darken(bg)))
        self.bind("<Leave>", lambda e: self.config(bg=bg))

    @staticmethod
    def _darken(hex_color):
        r, g, b = int(hex_color[1:3],16), int(hex_color[3:5],16), int(hex_color[5:7],16)
        return "#{:02x}{:02x}{:02x}".format(max(0,r-20), max(0,g-20), max(0,b-20))


class LabeledField(tk.Frame):
    """Label + Entry pair."""
    def __init__(self, parent, label, variable, placeholder="", width=28, **kw):
        super().__init__(parent, bg=COLORS["surface"], **kw)
        tk.Label(self, text=label, font=F_SMALL, bg=COLORS["surface"],
                 fg=COLORS["text_muted"]).pack(anchor="w")
        self.entry = tk.Entry(self, textvariable=variable, width=width,
                              font=F_BODY, relief="solid", bd=1,
                              bg="white", fg=COLORS["text"],
                              insertbackground=COLORS["primary"],
                              highlightthickness=1,
                              highlightcolor=COLORS["primary"],
                              highlightbackground=COLORS["border"])
        self.entry.pack(fill="x", ipady=4)
        if placeholder and not variable.get():
            self._set_placeholder(placeholder, variable)

    def _set_placeholder(self, ph, var):
        self.entry.config(fg=COLORS["text_muted"])
        self.entry.insert(0, ph)
        def on_focus_in(e):
            if self.entry.get() == ph:
                self.entry.delete(0, "end")
                self.entry.config(fg=COLORS["text"])
        def on_focus_out(e):
            if not self.entry.get():
                self.entry.insert(0, ph)
                self.entry.config(fg=COLORS["text_muted"])
        self.entry.bind("<FocusIn>", on_focus_in)
        self.entry.bind("<FocusOut>", on_focus_out)


class Badge(tk.Label):
    def __init__(self, parent, text, kind="info", **kw):
        palettes = {
            "success": (COLORS["success_bg"], COLORS["accent"]),
            "danger":  (COLORS["danger_bg"],  COLORS["danger"]),
            "warning": (COLORS["warning_bg"], COLORS["warning"]),
            "info":    (COLORS["surface_alt"],COLORS["text_muted"]),
        }
        bg, fg = palettes.get(kind, palettes["info"])
        super().__init__(parent, text=text, font=F_SMALL,
                         bg=bg, fg=fg, padx=8, pady=2, **kw)


class SectionHeader(tk.Frame):
    def __init__(self, parent, text, icon="●", **kw):
        super().__init__(parent, bg=COLORS["surface_alt"], **kw)
        inner = tk.Frame(self, bg=COLORS["surface_alt"])
        inner.pack(fill="x", padx=12, pady=6)
        tk.Label(inner, text=icon, font=(FONT_FAMILY, 10), bg=COLORS["surface_alt"],
                 fg=COLORS["primary"]).pack(side="left", padx=(0,6))
        tk.Label(inner, text=text, font=F_H3, bg=COLORS["surface_alt"],
                 fg=COLORS["secondary"]).pack(side="left")


# ── Main Application ─────────────────────────────────────────────────────────

class BloodDonorSystem:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Smart Blood Donor Eligibility System")
        self.root.geometry("920x680")
        self.root.minsize(820, 600)
        self.root.configure(bg=COLORS["bg"])

        self.history = load_history()
        self._init_vars()
        self._build_ui()
        self._show_page("eligibility")

    # ── Variables ────────────────────────────────────────────────────────────

    def _init_vars(self):
        self.name_var           = tk.StringVar()
        self.age_var            = tk.StringVar()
        self.gender_var         = tk.StringVar(value="Male")
        self.blood_type_var     = tk.StringVar()
        self.weight_var         = tk.StringVar()
        self.last_donation_var  = tk.StringVar()
        self.medical_var        = tk.StringVar()
        self.medications_var    = tk.StringVar()
        self.recent_surgery_var = tk.BooleanVar()
        self.recent_tattoo_var  = tk.BooleanVar()
        self.pregnancy_var      = tk.BooleanVar()
        self.travel_var         = tk.BooleanVar()
        self.hb_level_var       = tk.StringVar()
        self.bp_systolic_var    = tk.StringVar()
        self.bp_diastolic_var   = tk.StringVar()
        self.smoker_var         = tk.BooleanVar()
        self.alcohol_var        = tk.BooleanVar()

    # ── UI Structure ─────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        body = tk.Frame(self.root, bg=COLORS["bg"])
        body.pack(fill="both", expand=True)
        self._build_sidebar(body)
        self.content_frame = tk.Frame(body, bg=COLORS["bg"])
        self.content_frame.pack(side="left", fill="both", expand=True, padx=16, pady=16)
        self._build_pages()

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=COLORS["header_bg"], height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        inner = tk.Frame(hdr, bg=COLORS["header_bg"])
        inner.pack(fill="both", expand=True, padx=20)
        tk.Label(inner, text="🩸", font=(FONT_FAMILY, 18), bg=COLORS["header_bg"],
                 fg=COLORS["primary"]).pack(side="left", pady=10)
        tk.Label(inner, text="  Blood Donor Eligibility System",
                 font=(FONT_FAMILY, 14, "bold"), bg=COLORS["header_bg"],
                 fg=COLORS["header_fg"]).pack(side="left", pady=10)
        tk.Label(inner, text=f"v2.0  •  {date.today().strftime('%B %d, %Y')}",
                 font=F_SMALL, bg=COLORS["header_bg"],
                 fg="#7F8C8D").pack(side="right", pady=10)

    def _build_sidebar(self, parent):
        self.sidebar = tk.Frame(parent, bg=COLORS["sidebar_bg"], width=180)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"], height=16).pack()
        self.nav_buttons = {}
        nav_items = [
            ("eligibility", "📋", "Check Eligibility"),
            ("compatibility","🔬", "Blood Compatibility"),
            ("history",      "📜", "Donor History"),
            ("guide",        "ℹ️",  "Donor Guide"),
        ]
        for page_id, icon, label in nav_items:
            btn = tk.Button(self.sidebar, text=f"  {icon}  {label}",
                            font=F_BODY, anchor="w",
                            bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_fg"],
                            relief="flat", bd=0, padx=10, pady=10,
                            cursor="hand2",
                            activebackground=COLORS["sidebar_sel"],
                            activeforeground="white",
                            command=lambda p=page_id: self._show_page(p))
            btn.pack(fill="x")
            self.nav_buttons[page_id] = btn
        tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"]).pack(fill="both", expand=True)
        tk.Label(self.sidebar, text="PH Red Cross\nWHO Guidelines",
                 font=F_SMALL, bg=COLORS["sidebar_bg"], fg="#7F8C8D",
                 justify="center").pack(pady=10)

    def _build_pages(self):
        self.pages = {}
        self.pages["eligibility"]   = self._build_eligibility_page()
        self.pages["compatibility"] = self._build_compatibility_page()
        self.pages["history"]       = self._build_history_page()
        self.pages["guide"]         = self._build_guide_page()

    def _show_page(self, page_id):
        for p in self.pages.values():
            p.pack_forget()
        self.pages[page_id].pack(fill="both", expand=True)
        for pid, btn in self.nav_buttons.items():
            if pid == page_id:
                btn.config(bg=COLORS["sidebar_sel"], fg="white")
            else:
                btn.config(bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_fg"])
        if page_id == "history":
            self._refresh_history()

    # ── Page: Eligibility ────────────────────────────────────────────────────

    def _build_eligibility_page(self):
        page = tk.Frame(self.content_frame, bg=COLORS["bg"])

        # Scrollable canvas setup
        canvas = tk.Canvas(page, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(page, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=COLORS["bg"])

        self.scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        sf = self.scroll_frame

        # ── Section 1: Personal Info ──
        card1 = Card(sf, title="  Personal Information")
        card1.pack(fill="x", pady=(0, 10))
        grid1 = tk.Frame(card1, bg=COLORS["surface"])
        grid1.pack(fill="x", padx=14, pady=(6, 14))
        grid1.columnconfigure((0,1,2), weight=1)

        LabeledField(grid1, "Full Name *", self.name_var, width=24).grid(row=0, column=0, padx=6, pady=4, sticky="ew")
        LabeledField(grid1, "Age *", self.age_var, "18–65", width=10).grid(row=0, column=1, padx=6, pady=4, sticky="ew")

        gender_f = tk.Frame(grid1, bg=COLORS["surface"])
        gender_f.grid(row=0, column=2, padx=6, pady=4, sticky="ew")
        tk.Label(gender_f, text="Gender", font=F_SMALL, bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(anchor="w")
        rb_frame = tk.Frame(gender_f, bg=COLORS["surface"])
        rb_frame.pack(anchor="w")
        for g in ["Male", "Female", "Other"]:
            tk.Radiobutton(rb_frame, text=g, variable=self.gender_var, value=g,
                           font=F_BODY, bg=COLORS["surface"], fg=COLORS["text"],
                           selectcolor=COLORS["primary_light"],
                           activebackground=COLORS["surface"]).pack(side="left", padx=(0,8))

        bt_f = tk.Frame(grid1, bg=COLORS["surface"])
        bt_f.grid(row=1, column=0, padx=6, pady=4, sticky="ew")
        tk.Label(bt_f, text="Blood Type", font=F_SMALL, bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(anchor="w")
        bt_combo = ttk.Combobox(bt_f, textvariable=self.blood_type_var,
                                values=["A+","A-","B+","B-","AB+","AB-","O+","O-"],
                                state="readonly", width=10, font=F_BODY)
        bt_combo.pack(anchor="w", ipady=3)

        LabeledField(grid1, "Weight (kg) *", self.weight_var, "≥50 kg", width=12).grid(row=1, column=1, padx=6, pady=4, sticky="ew")
        LabeledField(grid1, "Last Donation (YYYY-MM-DD)", self.last_donation_var, "optional", width=16).grid(row=1, column=2, padx=6, pady=4, sticky="ew")

        # ── Section 2: Health Vitals ──
        card2 = Card(sf, title="  Health Vitals")
        card2.pack(fill="x", pady=(0, 10))
        grid2 = tk.Frame(card2, bg=COLORS["surface"])
        grid2.pack(fill="x", padx=14, pady=(6, 14))
        grid2.columnconfigure((0,1,2), weight=1)

        LabeledField(grid2, "Hemoglobin (g/dL)", self.hb_level_var, "M≥13  F≥12", width=14).grid(row=0, column=0, padx=6, pady=4, sticky="ew")
        LabeledField(grid2, "BP Systolic (mmHg)", self.bp_systolic_var, "90–160", width=12).grid(row=0, column=1, padx=6, pady=4, sticky="ew")
        LabeledField(grid2, "BP Diastolic (mmHg)", self.bp_diastolic_var, "60–100", width=12).grid(row=0, column=2, padx=6, pady=4, sticky="ew")
        LabeledField(grid2, "Medical Conditions", self.medical_var, "e.g. hepatitis, cancer…", width=30).grid(row=1, column=0, columnspan=2, padx=6, pady=4, sticky="ew")
        LabeledField(grid2, "Current Medications", self.medications_var, "e.g. aspirin, warfarin…", width=30).grid(row=1, column=2, padx=6, pady=4, sticky="ew")

        # ── Section 3: Risk Factors ──
        card3 = Card(sf, title="  Risk & Deferral Factors")
        card3.pack(fill="x", pady=(0, 10))
        risk_grid = tk.Frame(card3, bg=COLORS["surface"])
        risk_grid.pack(fill="x", padx=14, pady=(6, 14))

        checks = [
            (self.recent_surgery_var,  "Recent Surgery",          "Within the last 6 months"),
            (self.recent_tattoo_var,   "Tattoo / Piercing",       "Within the last 12 months"),
            (self.pregnancy_var,       "Pregnancy / Childbirth",  "Currently pregnant or within 6 months"),
            (self.travel_var,          "Travel to Endemic Area",  "Malaria/Ebola zone in past 12 months"),
            (self.smoker_var,          "Smoker",                  "Deferral required before donation"),
            (self.alcohol_var,         "Recent Alcohol Use",      "Within the past 24 hours"),
        ]
        for i, (var, label, note) in enumerate(checks):
            row = i // 2
            col = i % 2
            f = tk.Frame(risk_grid, bg=COLORS["surface"])
            f.grid(row=row, column=col, padx=6, pady=4, sticky="ew")
            risk_grid.columnconfigure(col, weight=1)
            cb = tk.Checkbutton(f, variable=var, font=F_BODY,
                                bg=COLORS["surface"], fg=COLORS["text"],
                                selectcolor=COLORS["primary_light"],
                                activebackground=COLORS["surface"])
            cb.pack(side="left")
            txt_f = tk.Frame(f, bg=COLORS["surface"])
            txt_f.pack(side="left")
            tk.Label(txt_f, text=label, font=F_BODY, bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w")
            tk.Label(txt_f, text=note,  font=F_SMALL, bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(anchor="w")

        # ── Action buttons ──
        btn_row = tk.Frame(sf, bg=COLORS["bg"])
        btn_row.pack(fill="x", pady=(0, 10))
        IconButton(btn_row, "  ✔  Check Eligibility", self._check_eligibility).pack(side="left", padx=(0,8))
        IconButton(btn_row, "  ✖  Clear Form", self._clear_form, color="#6B7280").pack(side="left")

        # ── Results card ──
        self.result_card = Card(sf, title="  Eligibility Result")
        self.result_card.pack(fill="x", pady=(0, 16))
        self.result_inner = tk.Frame(self.result_card, bg=COLORS["surface"])
        self.result_inner.pack(fill="x", padx=14, pady=12)
        tk.Label(self.result_inner, text="Fill in the form above and click  'Check Eligibility'",
                 font=F_BODY, bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(pady=10)

        return page

    # ── Page: Compatibility ──────────────────────────────────────────────────

    def _build_compatibility_page(self):
        page = tk.Frame(self.content_frame, bg=COLORS["bg"])
        tk.Label(page, text="Blood Type Compatibility", font=F_H1,
                 bg=COLORS["bg"], fg=COLORS["secondary"]).pack(anchor="w", pady=(0,10))

        sel_f = tk.Frame(page, bg=COLORS["bg"])
        sel_f.pack(anchor="w", pady=(0, 14))
        tk.Label(sel_f, text="Select Blood Type:", font=F_BODY,
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left")
        self.compat_var = tk.StringVar(value="O+")
        for bt in ["A+","A-","B+","B-","AB+","AB-","O+","O-"]:
            b = tk.Radiobutton(sel_f, text=bt, variable=self.compat_var, value=bt,
                               font=F_BODY, bg=COLORS["bg"],
                               selectcolor=COLORS["primary_light"],
                               command=self._update_compatibility)
            b.pack(side="left", padx=4)

        self.compat_frame = tk.Frame(page, bg=COLORS["bg"])
        self.compat_frame.pack(fill="both", expand=True)
        self._update_compatibility()
        return page

    def _update_compatibility(self):
        for w in self.compat_frame.winfo_children():
            w.destroy()
        bt = self.compat_var.get()
        info = BLOOD_TYPE_COMPATIBILITY.get(bt, {})

        row = tk.Frame(self.compat_frame, bg=COLORS["bg"])
        row.pack(fill="x")

        donate_card = Card(row, title="  Can Donate To")
        donate_card.pack(side="left", fill="both", expand=True, padx=(0,8))
        df = tk.Frame(donate_card, bg=COLORS["surface"])
        df.pack(fill="x", padx=14, pady=12)
        for t in info.get("donates_to", []):
            Badge(df, t, kind="success").pack(side="left", padx=3, pady=3)

        receive_card = Card(row, title="  Can Receive From")
        receive_card.pack(side="left", fill="both", expand=True)
        rf = tk.Frame(receive_card, bg=COLORS["surface"])
        rf.pack(fill="x", padx=14, pady=12)
        for t in info.get("receives_from", []):
            Badge(rf, t, kind="info").pack(side="left", padx=3, pady=3)

        # Universal donor/recipient note
        note = ""
        if bt == "O-": note = "🏅  Universal Donor — can give to all blood types."
        elif bt == "AB+": note = "🏅  Universal Recipient — can receive from all blood types."
        if note:
            lbl = tk.Label(self.compat_frame, text=note, font=F_BODY,
                           bg=COLORS["warning_bg"], fg=COLORS["warning"],
                           padx=12, pady=8)
            lbl.pack(fill="x", pady=(10,0))

        # Compatibility table
        tbl_card = Card(self.compat_frame, title="  Full Compatibility Matrix")
        tbl_card.pack(fill="x", pady=(12,0))
        tbl_f = tk.Frame(tbl_card, bg=COLORS["surface"])
        tbl_f.pack(fill="x", padx=14, pady=12)
        types = ["A+","A-","B+","B-","AB+","AB-","O+","O-"]
        tk.Label(tbl_f, text="", font=F_SMALL, bg=COLORS["surface"], width=6).grid(row=0, column=0)
        for ci, t in enumerate(types):
            tk.Label(tbl_f, text=t, font=(FONT_FAMILY, 9, "bold"),
                     bg=COLORS["surface_alt"], fg=COLORS["secondary"],
                     width=5, relief="flat", padx=2, pady=3).grid(row=0, column=ci+1, padx=1, pady=1)
        for ri, donor in enumerate(types):
            tk.Label(tbl_f, text=donor, font=(FONT_FAMILY, 9, "bold"),
                     bg=COLORS["surface_alt"], fg=COLORS["secondary"],
                     width=6, padx=2, pady=3).grid(row=ri+1, column=0, padx=1, pady=1)
            for ci, recipient in enumerate(types):
                compat = donor in BLOOD_TYPE_COMPATIBILITY.get(recipient, {}).get("receives_from", [])
                bg = COLORS["success_bg"] if compat else COLORS["surface"]
                txt = "✓" if compat else "·"
                fg = COLORS["accent"] if compat else COLORS["border"]
                tk.Label(tbl_f, text=txt, bg=bg, fg=fg,
                         font=(FONT_FAMILY, 9, "bold"), width=5, pady=3).grid(row=ri+1, column=ci+1, padx=1, pady=1)

    # ── Page: History ────────────────────────────────────────────────────────

    def _build_history_page(self):
        page = tk.Frame(self.content_frame, bg=COLORS["bg"])
        hdr_f = tk.Frame(page, bg=COLORS["bg"])
        hdr_f.pack(fill="x", pady=(0, 10))
        tk.Label(hdr_f, text="Donor Check History", font=F_H1,
                 bg=COLORS["bg"], fg=COLORS["secondary"]).pack(side="left")
        IconButton(hdr_f, "  🗑  Clear History", self._clear_history,
                   color="#6B7280").pack(side="right")

        cols = ("timestamp","name","age","blood_type","result")
        self.history_tree = ttk.Treeview(page, columns=cols, show="headings", height=18)
        headers = {"timestamp":"Date & Time","name":"Name","age":"Age",
                   "blood_type":"Blood Type","result":"Result"}
        widths  = {"timestamp":140,"name":180,"age":60,"blood_type":90,"result":120}
        for c in cols:
            self.history_tree.heading(c, text=headers[c])
            self.history_tree.column(c, width=widths[c], anchor="center" if c != "name" else "w")

        style = ttk.Style()
        style.configure("Treeview", font=F_BODY, rowheight=26, background=COLORS["surface"])
        style.configure("Treeview.Heading", font=F_H3, background=COLORS["surface_alt"])
        style.map("Treeview", background=[("selected", COLORS["primary_light"])])
        self.history_tree.tag_configure("eligible",   background="#F0FDF4")
        self.history_tree.tag_configure("ineligible", background="#FFF5F5")

        vsb = ttk.Scrollbar(page, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=vsb.set)
        self.history_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        return page

    def _refresh_history(self):
        self.history_tree.delete(*self.history_tree.get_children())
        for rec in reversed(self.history):
            tag = "eligible" if rec["result"] == "ELIGIBLE" else "ineligible"
            self.history_tree.insert("", "end", values=(
                rec.get("timestamp",""), rec.get("name",""), rec.get("age",""),
                rec.get("blood_type",""), rec.get("result","")
            ), tags=(tag,))

    def _clear_history(self):
        if messagebox.askyesno("Clear History", "Delete all donor check records?"):
            self.history.clear()
            save_history(self.history)
            self._refresh_history()

    # ── Page: Guide ──────────────────────────────────────────────────────────

    def _build_guide_page(self):
        page = tk.Frame(self.content_frame, bg=COLORS["bg"])
        tk.Label(page, text="Donor Eligibility Guide", font=F_H1,
                 bg=COLORS["bg"], fg=COLORS["secondary"]).pack(anchor="w", pady=(0, 10))

        canvas = tk.Canvas(page, bg=COLORS["bg"], highlightthickness=0)
        vsb = ttk.Scrollbar(page, orient="vertical", command=canvas.yview)
        sf = tk.Frame(canvas, bg=COLORS["bg"])
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=sf, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        sections = [
            ("Basic Requirements", [
                ("Age",             "18–65 years old"),
                ("Weight",          "At least 50 kg (110 lbs)"),
                ("Hemoglobin",      "Male ≥13.0 g/dL  |  Female ≥12.0 g/dL"),
                ("Blood Pressure",  "Systolic 90–160 mmHg  |  Diastolic 60–100 mmHg"),
                ("Donation Interval","At least 56 days (8 weeks) between whole-blood donations"),
            ]),
            ("Temporary Deferrals", [
                ("Surgery",         "Wait 6 months after any surgical procedure"),
                ("Tattoo/Piercing", "Wait 12 months after tattoos or body piercings"),
                ("Pregnancy",       "Wait 6 months after delivery or end of breastfeeding"),
                ("Travel",          "Wait 12 months after travel to malaria-endemic regions"),
                ("Alcohol",         "Do not donate within 24 hours of alcohol consumption"),
                ("Smoking",         "Avoid smoking 2 hours before and after donation"),
                ("Fever/Illness",   "Wait until fully recovered + 14 days"),
            ]),
            ("Permanent Deferrals", [
                ("HIV/AIDS",        "Permanent deferral"),
                ("Hepatitis B/C",   "Permanent deferral"),
                ("Cancer",          "Most cancers are permanent deferrals; some exceptions apply"),
                ("Heart Disease",   "Most cardiac conditions result in deferral"),
                ("Chagas Disease",  "Permanent deferral"),
            ]),
            ("High-Risk Medications", [
                ("Anticoagulants",  "Warfarin, Heparin — permanent deferral risk"),
                ("Isotretinoin",    "Accutane — wait 1 month after last dose"),
                ("Finasteride",     "Propecia/Proscar — wait 1 month"),
                ("Aspirin",         "Wait 48 hours for platelet donation"),
            ]),
        ]

        for title, items in sections:
            card = Card(sf, title=f"  {title}")
            card.pack(fill="x", pady=(0, 10))
            for label, desc in items:
                row = tk.Frame(card, bg=COLORS["surface"])
                row.pack(fill="x", padx=14, pady=3)
                tk.Label(row, text=label, font=(FONT_FAMILY, 10, "bold"),
                         bg=COLORS["surface"], fg=COLORS["secondary"], width=22, anchor="w").pack(side="left")
                tk.Label(row, text=desc, font=F_BODY,
                         bg=COLORS["surface"], fg=COLORS["text_muted"], anchor="w").pack(side="left")
            tk.Frame(card, bg=COLORS["surface"], height=8).pack()

        return page

    # ── Eligibility Logic ────────────────────────────────────────────────────

    def _check_eligibility(self):
        reasons = []
        warnings = []

        # ── Validate required fields ──
        name = self.name_var.get().strip()
        if not name or name == "":
            messagebox.showwarning("Missing Field", "Please enter the donor's full name.")
            return

        age = self._parse_number(self.age_var.get(), "Age", int)
        if age is None: return
        weight = self._parse_number(self.weight_var.get(), "Weight", float)
        if weight is None: return

        # ── Age ──
        if age < 18:
            reasons.append(("Age", f"Under minimum age (18). Current: {age}"))
        elif age > 65:
            reasons.append(("Age", f"Over maximum age (65). Current: {age}"))

        # ── Weight ──
        if weight < 50:
            reasons.append(("Weight", f"Below minimum weight (50 kg). Current: {weight} kg"))

        # ── Last donation ──
        last_don = self._parse_date(self.last_donation_var.get())
        if last_don:
            days = (datetime.now() - last_don).days
            if days < 56:
                reasons.append(("Donation Interval", f"Only {days} days since last donation (need 56+)"))

        # ── Hemoglobin ──
        hb_str = self.hb_level_var.get().strip()
        if hb_str and hb_str not in ("M≥13  F≥12", ""):
            hb = self._parse_number(hb_str, "Hemoglobin", float, silent=True)
            if hb is not None:
                min_hb = 13.0 if self.gender_var.get() == "Male" else 12.0
                if hb < min_hb:
                    reasons.append(("Hemoglobin", f"{hb} g/dL — below minimum ({min_hb} g/dL)"))
                elif hb > 17.5:
                    warnings.append("Hemoglobin is high (>17.5 g/dL) — consult medical staff")

        # ── Blood pressure ──
        sys_str = self.bp_systolic_var.get().strip()
        dia_str = self.bp_diastolic_var.get().strip()
        if sys_str not in ("", "90–160"):
            sys_bp = self._parse_number(sys_str, "Systolic BP", int, silent=True)
            if sys_bp is not None:
                if sys_bp < 90 or sys_bp > 160:
                    reasons.append(("Blood Pressure", f"Systolic {sys_bp} mmHg out of range (90–160)"))
        if dia_str not in ("", "60–100"):
            dia_bp = self._parse_number(dia_str, "Diastolic BP", int, silent=True)
            if dia_bp is not None:
                if dia_bp < 60 or dia_bp > 100:
                    reasons.append(("Blood Pressure", f"Diastolic {dia_bp} mmHg out of range (60–100)"))

        # ── Risk factors ──
        if self.recent_surgery_var.get():
            reasons.append(("Surgery",      "Recent surgery within 6 months"))
        if self.recent_tattoo_var.get():
            reasons.append(("Tattoo/Piercing", "Recent tattoo or piercing within 12 months"))
        if self.pregnancy_var.get():
            reasons.append(("Pregnancy",    "Currently pregnant or within 6 months post-partum"))
        if self.travel_var.get():
            reasons.append(("Travel",       "Travel to endemic disease area in past 12 months"))
        if self.alcohol_var.get():
            reasons.append(("Alcohol",      "Alcohol consumed within the past 24 hours"))
        if self.smoker_var.get():
            warnings.append("Smoker — advised to wait 2 hours before and after donation")

        # ── Medical conditions ──
        conds = self.medical_var.get().lower()
        for c in HIGH_RISK_CONDITIONS:
            if c in conds:
                reasons.append(("Medical Condition", f"'{c}' is a deferral condition"))

        # ── Medications ──
        meds = self.medications_var.get().lower()
        for m in RISKY_MEDICATIONS:
            if m in meds:
                reasons.append(("Medication", f"'{m}' may require deferral — consult staff"))

        is_eligible = len(reasons) == 0

        # ── Save to history ──
        self.history.append({
            "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M"),
            "name":       name,
            "age":        age,
            "blood_type": self.blood_type_var.get() or "—",
            "result":     "ELIGIBLE" if is_eligible else "NOT ELIGIBLE",
            "reasons":    [r[1] for r in reasons],
        })
        save_history(self.history)

        self._show_result(is_eligible, reasons, warnings, name)

    def _show_result(self, is_eligible, reasons, warnings, name):
        for w in self.result_inner.winfo_children():
            w.destroy()

        if is_eligible:
            bg  = COLORS["success_bg"]
            fg  = COLORS["accent"]
            icon = "✅"
            msg  = "ELIGIBLE TO DONATE"
            sub  = f"{name} meets all eligibility criteria."
        else:
            bg  = COLORS["danger_bg"]
            fg  = COLORS["danger"]
            icon = "🚫"
            msg  = "NOT ELIGIBLE"
            sub  = f"{name} does not meet the eligibility criteria."

        banner = tk.Frame(self.result_inner, bg=bg)
        banner.pack(fill="x", pady=(0, 10))
        tk.Label(banner, text=f"{icon}  {msg}", font=(FONT_FAMILY, 15, "bold"),
                 bg=bg, fg=fg, pady=12).pack(side="left", padx=16)
        bt = self.blood_type_var.get()
        if bt:
            Badge(banner, f"Blood Type: {bt}", kind="info").pack(side="right", padx=16)
        tk.Label(self.result_inner, text=sub, font=F_BODY,
                 bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(anchor="w", pady=(0,8))

        if reasons:
            tk.Label(self.result_inner, text="Deferral Reasons:", font=F_H3,
                     bg=COLORS["surface"], fg=COLORS["secondary"]).pack(anchor="w")
            for label, detail in reasons:
                row = tk.Frame(self.result_inner, bg=COLORS["surface"])
                row.pack(fill="x", pady=2)
                tk.Label(row, text="  ✗", font=F_BODY, bg=COLORS["surface"],
                         fg=COLORS["danger"]).pack(side="left")
                tk.Label(row, text=f" {label}: ", font=(FONT_FAMILY, 10, "bold"),
                         bg=COLORS["surface"], fg=COLORS["text"]).pack(side="left")
                tk.Label(row, text=detail, font=F_BODY,
                         bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(side="left")

        if warnings:
            tk.Label(self.result_inner, text="Advisories:", font=F_H3,
                     bg=COLORS["surface"], fg=COLORS["secondary"]).pack(anchor="w", pady=(8,0))
            for w in warnings:
                row = tk.Frame(self.result_inner, bg=COLORS["surface"])
                row.pack(fill="x", pady=2)
                tk.Label(row, text="  ⚠", font=F_BODY, bg=COLORS["surface"],
                         fg=COLORS["warning"]).pack(side="left")
                tk.Label(row, text=f" {w}", font=F_BODY,
                         bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(side="left")

        if is_eligible:
            tk.Frame(self.result_inner, bg=COLORS["surface"], height=6).pack()
            tk.Label(self.result_inner,
                     text="📍  Please proceed to the registration desk with a valid ID.",
                     font=F_BODY, bg=COLORS["success_bg"], fg=COLORS["accent"],
                     padx=10, pady=6).pack(fill="x")

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _parse_number(self, val, field, cast=float, min_val=None, max_val=None, silent=False):
        try:
            n = cast(val.strip())
            if min_val is not None and n < min_val:
                if not silent:
                    messagebox.showwarning("Validation", f"{field} must be at least {min_val}.")
                return None
            if max_val is not None and n > max_val:
                if not silent:
                    messagebox.showwarning("Validation", f"{field} must be at most {max_val}.")
                return None
            return n
        except (ValueError, AttributeError):
            if not silent:
                messagebox.showwarning("Validation", f"'{val}' is not a valid {field}.")
            return None

    def _parse_date(self, val):
        if not val or val.strip() in ("", "optional"):
            return None
        try:
            return datetime.strptime(val.strip(), "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Validation", "Date must be in YYYY-MM-DD format.")
            return None

    def _clear_form(self):
        for v in (self.name_var, self.age_var, self.blood_type_var,
                  self.weight_var, self.last_donation_var,
                  self.medical_var, self.medications_var,
                  self.hb_level_var, self.bp_systolic_var, self.bp_diastolic_var):
            v.set("")
        for v in (self.recent_surgery_var, self.recent_tattoo_var,
                  self.pregnancy_var, self.travel_var,
                  self.smoker_var, self.alcohol_var):
            v.set(False)
        self.gender_var.set("Male")
        for w in self.result_inner.winfo_children():
            w.destroy()
        tk.Label(self.result_inner,
                 text="Fill in the form above and click  'Check Eligibility'",
                 font=F_BODY, bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(pady=10)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.tk.call("tk", "scaling", 1.2)
    except Exception:
        pass
    app = BloodDonorSystem(root)
    root.mainloop()