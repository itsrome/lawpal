# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import re
import time
import datetime
import os

# ─────────────────────────────────────────────
#  WORD MAPPING  (complex → simple)
# ─────────────────────────────────────────────
WORD_MAP = {
    "lessee": "renter", "lessor": "landlord", "indemnify": "pay for",
    "indemnification": "payment for damages", "pursuant to": "according to",
    "aforementioned": "mentioned above", "hereinafter": "from now on",
    "herein": "in this document", "thereof": "of that", "therein": "in that",
    "whereby": "by which", "notwithstanding": "despite", "forthwith": "immediately",
    "henceforth": "from this point on", "heretofore": "until now",
    "in accordance with": "following", "null and void": "invalid",
    "force majeure": "unexpected event beyond control",
    "bona fide": "genuine", "pro rata": "proportionally",
    "inter alia": "among other things", "prima facie": "at first glance",
    "de facto": "in practice", "ab initio": "from the beginning",
    "ipso facto": "by that very fact", "mutatis mutandis": "with necessary changes",
    "covenant": "agreement", "tort": "wrongful act", "plaintiff": "person who filed the case",
    "defendant": "person being accused", "affidavit": "written sworn statement",
    "subpoena": "legal order to appear", "injunction": "court order to stop something",
    "litigation": "legal dispute in court", "arbitration": "settling dispute outside court",
    "jurisdiction": "legal authority", "statute": "written law",
    "ordinance": "local law", "promulgate": "officially announce",
    "adjudicate": "make a legal decision", "indictment": "formal criminal charge",
    "acquittal": "being found not guilty", "restitution": "repayment for harm done",
    "liability": "legal responsibility", "negligence": "failure to take proper care",
    "breach": "violation", "remedy": "solution or compensation",
    "damages": "money paid for harm", "waiver": "giving up a right",
    "lien": "legal claim on property", "encumbrance": "burden on property",
    "easement": "right to use someone else's land", "probate": "legal process after death",
    "intestate": "dying without a will", "testator": "person who made a will",
    "executor": "person who carries out a will", "beneficiary": "person who receives something",
    "collateral": "property used as loan security", "default": "failure to meet obligation",
    "foreclosure": "taking property due to unpaid loan",
    "garnishment": "taking wages to pay debt", "levy": "legal seizure",
    "deposition": "sworn out-of-court testimony", "discovery": "gathering evidence before trial",
    "pleading": "formal legal statement", "verdict": "court decision",
    "appeal": "request to review a decision", "statute of limitations": "deadline to file a case",
    "due process": "fair legal procedures", "habeas corpus": "right to appear before a court",
    "eminent domain": "government taking private property", "sovereign immunity": "government cannot be sued",
    "fiduciary": "person trusted to act for another", "power of attorney": "legal permission to act for someone",
    "notarize": "officially certify a document", "ratify": "officially approve",
    "rescind": "cancel an agreement", "void": "not legally valid",
    "voidable": "can be cancelled", "enforceable": "can be legally required",
    "consideration": "something of value exchanged in a contract",
    "offer": "proposal to make a deal", "acceptance": "agreeing to an offer",
    "termination": "ending of an agreement", "clause": "section of a contract",
    "provision": "rule or condition", "stipulation": "specific requirement",
    "obligation": "duty", "right": "entitlement", "penalty": "punishment or fine",
    "sanction": "official penalty", "compliance": "following the rules",
    "violation": "breaking a rule", "infringement": "unauthorized use",
    "indemnity": "protection from loss", "surety": "guarantee",
    "warranty": "guarantee of quality", "representation": "statement of fact",
    "disclosure": "sharing of information", "confidentiality": "keeping information private",
    "proprietary": "privately owned", "intellectual property": "creative work protected by law",
    "copyright": "right to copy or use creative work", "trademark": "protected brand name or logo",
    "patent": "exclusive right to an invention", "license": "permission to use something",
    "assignment": "transfer of rights", "sublease": "renting to someone else",
    "eviction": "legally removing a tenant", "tenancy": "renting arrangement",
    "premises": "property", "dwelling": "home", "domicile": "permanent home",
    "residency": "place of living", "occupancy": "use of a property",
}

# ─────────────────────────────────────────────
#  ABBREVIATIONS (to avoid wrong sentence splits)
# ─────────────────────────────────────────────
ABBREVIATIONS = {"mr", "mrs", "ms", "dr", "prof", "sr", "jr", "vs", "etc",
                 "no", "art", "sec", "vol", "fig", "jan", "feb", "mar",
                 "apr", "jun", "jul", "aug", "sep", "oct", "nov", "dec"}

# ─────────────────────────────────────────────
#  RULE BASE  (keyword sets → answers)
# ─────────────────────────────────────────────
RULES = [
    {
        "keywords": ["landlord", "enter", "room", "permission"],
        "topic": "Tenant Rights – Landlord Entry",
        "answer": (
            "Your landlord CANNOT enter your room without your permission, except in emergencies.\n\n"
            "• They must give you advance notice (usually 24–48 hours).\n"
            "• Entering without notice may be considered trespassing.\n"
            "• You have the right to peaceful enjoyment of your rented space.\n\n"
            "Tip: If your landlord keeps entering without notice, document each incident and consider "
            "sending a written warning."
        )
    },
    {
        "keywords": ["break", "contract"],
        "topic": "Contract Breach",
        "answer": (
            "Breaking a contract (called a 'breach') can have legal consequences.\n\n"
            "• The other party may demand compensation for losses caused.\n"
            "• They may take you to court to enforce the contract.\n"
            "• In some cases, the contract can be cancelled entirely.\n\n"
            "Tip: Always read a contract carefully before signing. If you cannot fulfill it, "
            "try to negotiate with the other party before it becomes a legal issue."
        )
    },
    {
        "keywords": ["traffic", "fine", "ticket"],
        "topic": "Traffic Fine & Appeal",
        "answer": (
            "If you receive a traffic fine, you have rights.\n\n"
            "• You can appeal the fine if you believe it was issued unfairly.\n"
            "• Under Ethiopian Traffic Proclamation No. 1151/2019, you have the right to contest.\n"
            "• You must file your appeal within the deadline stated on the notice.\n"
            "• Keep a copy of all documents related to the fine.\n\n"
            "Tip: Do not just pay a fine you disagree with. Ask about the appeal process first."
        )
    },
    {
        "keywords": ["suspend", "suspension", "school", "university", "student"],
        "topic": "Student Suspension Rights",
        "answer": (
            "If you are suspended from school or university, you have rights.\n\n"
            "• You are entitled to a fair hearing before any suspension takes effect.\n"
            "• You should be informed of the reason in writing.\n"
            "• You have the right to present your side of the story.\n"
            "• Under Madda Walabu University's Student Code of Conduct, due process must be followed.\n\n"
            "Tip: Request a copy of the disciplinary procedure and follow it step by step."
        )
    },
    {
        "keywords": ["deposit", "landlord", "keep", "return", "refund"],
        "topic": "Security Deposit",
        "answer": (
            "Your landlord must return your deposit when you leave, unless there is a valid reason.\n\n"
            "• Valid reasons: unpaid rent, damage beyond normal wear and tear.\n"
            "• They cannot keep it just because they want to.\n"
            "• Ask for a written explanation if they deduct anything.\n"
            "• You can take the matter to a local court if they refuse unfairly.\n\n"
            "Tip: Always take photos of the property when you move in and move out."
        )
    },
    {
        "keywords": ["right", "arrest", "police", "detained"],
        "topic": "Rights When Arrested",
        "answer": (
            "Under the Ethiopian Constitution (Article 19), you have rights when arrested.\n\n"
            "• You must be told why you are being arrested.\n"
            "• You have the right to remain silent.\n"
            "• You have the right to a lawyer.\n"
            "• You must be brought before a court within 48 hours.\n"
            "• You cannot be tortured or mistreated.\n\n"
            "Tip: Stay calm, do not resist, and ask for a lawyer immediately."
        )
    },
    {
        "keywords": ["contract", "sign", "agreement", "terms"],
        "topic": "Signing a Contract",
        "answer": (
            "Before signing any contract, make sure you understand it fully.\n\n"
            "• Read every clause carefully — especially the fine print.\n"
            "• Ask questions about anything you do not understand.\n"
            "• Never sign under pressure.\n"
            "• A contract is legally binding once signed.\n"
            "• You can ask for changes before signing — it is your right.\n\n"
            "Tip: Use LawPal's Simplify tab to paste confusing contract text and get a plain version."
        )
    },
    {
        "keywords": ["evict", "eviction", "kicked out", "remove tenant"],
        "topic": "Eviction Rights",
        "answer": (
            "A landlord cannot evict you without following the proper legal process.\n\n"
            "• They must give you written notice with a reason.\n"
            "• You have the right to respond and contest the eviction.\n"
            "• Illegal eviction (changing locks, removing belongings) is not allowed.\n"
            "• You can report illegal eviction to local authorities.\n\n"
            "Tip: Keep all rental agreements and payment receipts as proof."
        )
    },
    {
        "keywords": ["fine", "appeal", "challenge", "dispute"],
        "topic": "Appealing a Fine or Decision",
        "answer": (
            "You have the right to appeal most fines and official decisions.\n\n"
            "• Check the notice for the appeal deadline — missing it may forfeit your right.\n"
            "• Write a clear, factual appeal letter explaining why the decision is wrong.\n"
            "• Attach any supporting evidence (photos, receipts, witnesses).\n"
            "• Submit to the correct authority listed on the notice.\n\n"
            "Tip: Always appeal in writing and keep a copy for yourself."
        )
    },
    {
        "keywords": ["constitution", "rights", "freedom", "liberty"],
        "topic": "Constitutional Rights (Ethiopia)",
        "answer": (
            "The Ethiopian Constitution guarantees fundamental rights to all citizens.\n\n"
            "• Right to life and personal liberty (Article 14)\n"
            "• Right to equality (Article 25)\n"
            "• Right to freedom of expression (Article 29)\n"
            "• Right to education (Article 41)\n"
            "• Right to a fair trial (Article 20)\n\n"
            "Tip: These rights apply to everyone. If you feel your rights are violated, "
            "you can report to the Ethiopian Human Rights Commission."
        )
    },
    {
        "keywords": ["wage", "salary", "pay", "employer", "employee", "work"],
        "topic": "Employment & Wages",
        "answer": (
            "As an employee, you have basic rights regarding your pay and working conditions.\n\n"
            "• Your employer must pay you on time as agreed.\n"
            "• Deductions from your salary must be explained and agreed upon.\n"
            "• You are entitled to a written employment contract.\n"
            "• Unfair dismissal without notice or reason may be challenged legally.\n\n"
            "Tip: Keep copies of your employment contract and all pay slips."
        )
    },
    {
        "keywords": ["loan", "debt", "borrow", "repay", "interest"],
        "topic": "Loans & Debt",
        "answer": (
            "When taking a loan, understand your obligations clearly.\n\n"
            "• You must repay the amount plus any agreed interest.\n"
            "• Defaulting (not paying) can lead to legal action or seizure of collateral.\n"
            "• You have the right to a clear written loan agreement.\n"
            "• Excessive interest rates may be illegal — check the terms carefully.\n\n"
            "Tip: Never sign a loan agreement without understanding the repayment schedule."
        )
    },
]

FALLBACK = (
    "I'm sorry, I don't have a specific answer for that question in my current knowledge base.\n\n"
    "For this type of legal matter, I recommend:\n"
    "• Consulting a qualified lawyer or legal aid organization.\n"
    "• Visiting the Ethiopian Legal Information Institute at ethlii.org.\n"
    "• Contacting your local court or legal aid office.\n\n"
    "Remember: LawPal provides general information only — not professional legal advice."
)

# ─────────────────────────────────────────────
#  NLP CORE FUNCTIONS
# ─────────────────────────────────────────────

def split_sentences(text):
    """Split text into sentences, respecting abbreviations."""
    parts = re.split(r'(?<=[.!?])\s+', text)
    merged, i = [], 0
    while i < len(parts):
        part = parts[i]
        last_word = part.rstrip('.').split('.')[-1].lower()
        if last_word in ABBREVIATIONS and i + 1 < len(parts):
            parts[i + 1] = part + ' ' + parts[i + 1]
        else:
            merged.append(part)
        i += 1
    return merged


def simplify_text(text):
    """Replace complex legal words and shorten sentences."""
    start = time.time()
    result = text

    # Replace multi-word phrases first (longest first)
    sorted_phrases = sorted(WORD_MAP.keys(), key=len, reverse=True)
    for phrase in sorted_phrases:
        pattern = re.compile(r'\b' + re.escape(phrase) + r'\b', re.IGNORECASE)
        replacement = WORD_MAP[phrase]
        result = pattern.sub(
            lambda m, r=replacement: r[0].upper() + r[1:]
            if m.group(0)[0].isupper() else r,
            result
        )

    # Split into sentences and clean up
    sentences = split_sentences(result)
    simplified_sentences = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        # Remove overly formal openers
        s = re.sub(r'^(It is hereby|Be it known that|Know all men by these presents that)\s*', '', s, flags=re.IGNORECASE)
        simplified_sentences.append(s)

    elapsed = time.time() - start
    return '\n'.join(simplified_sentences), round(elapsed, 4)


def is_question(text):
    """Detect if input is a question."""
    text = text.strip()
    if text.endswith('?'):
        return True
    question_starters = r'^(what|how|can|could|do|does|is|are|will|should|who|when|where|why|am|has|have)\b'
    return bool(re.match(question_starters, text, re.IGNORECASE))


def answer_question(text):
    """Match question to rule base using keyword scoring."""
    start = time.time()
    text_lower = text.lower()
    best_score, best_rule = 0, None

    for rule in RULES:
        score = sum(1 for kw in rule["keywords"] if kw in text_lower)
        if score > best_score:
            best_score, best_rule = score, rule

    elapsed = time.time() - start
    if best_rule and best_score >= 1:
        return best_rule["topic"], best_rule["answer"], round(elapsed, 4)
    return "No Match Found", FALLBACK, round(elapsed, 4)

# ─────────────────────────────────────────────
#  HISTORY MANAGER
# ─────────────────────────────────────────────
history = []  # list of dicts: {type, input, output, topic, time, timestamp}


def add_history(entry_type, inp, out, topic="", elapsed=0.0):
    history.append({
        "type": entry_type,
        "input": inp,
        "output": out,
        "topic": topic,
        "time": elapsed,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


# ─────────────────────────────────────────────
#  COLOR THEME
# ─────────────────────────────────────────────
COLORS = {
    "bg":        "#0f1117",
    "sidebar":   "#1a1d27",
    "card":      "#1e2130",
    "accent":    "#4f8ef7",
    "accent2":   "#7c5cbf",
    "success":   "#3ecf8e",
    "warning":   "#f5a623",
    "danger":    "#e05c5c",
    "text":      "#e8eaf0",
    "subtext":   "#8b90a0",
    "border":    "#2a2d3e",
    "input_bg":  "#252836",
    "hover":     "#2d3148",
    "white":     "#ffffff",
}

FONTS = {
    "title":   ("Segoe UI", 22, "bold"),
    "heading": ("Segoe UI", 13, "bold"),
    "body":    ("Segoe UI", 11),
    "small":   ("Segoe UI", 9),
    "mono":    ("Consolas", 10),
    "logo":    ("Segoe UI", 28, "bold"),
}

# ─────────────────────────────────────────────
#  MAIN APPLICATION CLASS
# ─────────────────────────────────────────────
class LawPalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LawPal – Intelligent Legal Simplification & Advisory System")
        self.geometry("1100x720")
        self.minsize(900, 600)
        self.configure(bg=COLORS["bg"])
        self.current_page = tk.StringVar(value="home")
        self._build_ui()

    def _build_ui(self):
        # ── Sidebar ──
        self.sidebar = tk.Frame(self, bg=COLORS["sidebar"], width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        logo_frame = tk.Frame(self.sidebar, bg=COLORS["sidebar"], pady=20)
        logo_frame.pack(fill="x")
        tk.Label(logo_frame, text="⚖", font=("Segoe UI", 32), bg=COLORS["sidebar"],
                 fg=COLORS["accent"]).pack()
        tk.Label(logo_frame, text="LawPal", font=FONTS["logo"], bg=COLORS["sidebar"],
                 fg=COLORS["white"]).pack()
        tk.Label(logo_frame, text="Legal Simplification AI", font=FONTS["small"],
                 bg=COLORS["sidebar"], fg=COLORS["subtext"]).pack()

        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", padx=15, pady=5)

        # Nav buttons
        self.nav_buttons = {}
        nav_items = [
            ("🏠  Home",        "home"),
            ("📝  Simplify",    "simplify"),
            ("💬  Ask LawPal",  "ask"),
            ("📚  History",     "history"),
            ("ℹ️   About",       "about"),
        ]
        for label, page in nav_items:
            btn = tk.Button(
                self.sidebar, text=label, font=FONTS["body"],
                bg=COLORS["sidebar"], fg=COLORS["text"],
                activebackground=COLORS["hover"], activeforeground=COLORS["white"],
                relief="flat", anchor="w", padx=20, pady=10, cursor="hand2",
                command=lambda p=page: self.show_page(p)
            )
            btn.pack(fill="x")
            self.nav_buttons[page] = btn

        # Bottom info
        tk.Label(self.sidebar, text="v1.0  |  Python + NLP", font=FONTS["small"],
                 bg=COLORS["sidebar"], fg=COLORS["subtext"]).pack(side="bottom", pady=10)

        # ── Main content area ──
        self.content = tk.Frame(self, bg=COLORS["bg"])
        self.content.pack(side="left", fill="both", expand=True)

        # Build all pages
        self.pages = {}
        self.pages["home"]     = self._build_home()
        self.pages["simplify"] = self._build_simplify()
        self.pages["ask"]      = self._build_ask()
        self.pages["history"]  = self._build_history()
        self.pages["about"]    = self._build_about()

        self.show_page("home")

    def show_page(self, name):
        for p in self.pages.values():
            p.pack_forget()
        self.pages[name].pack(fill="both", expand=True)
        self.current_page.set(name)
        # Highlight active nav
        for pg, btn in self.nav_buttons.items():
            if pg == name:
                btn.config(bg=COLORS["hover"], fg=COLORS["accent"])
            else:
                btn.config(bg=COLORS["sidebar"], fg=COLORS["text"])
        if name == "history":
            self._refresh_history()

    # ── Helper: card frame ──
    def _card(self, parent, **kwargs):
        return tk.Frame(parent, bg=COLORS["card"],
                        highlightbackground=COLORS["border"],
                        highlightthickness=1, **kwargs)

    # ── Helper: styled button ──
    def _btn(self, parent, text, command, color=None, **kwargs):
        c = color or COLORS["accent"]
        return tk.Button(parent, text=text, command=command,
                         bg=c, fg=COLORS["white"], font=FONTS["body"],
                         relief="flat", padx=16, pady=8, cursor="hand2",
                         activebackground=COLORS["hover"],
                         activeforeground=COLORS["white"], **kwargs)

    # ── Helper: scrolled text ──
    def _scrolled(self, parent, height=10, state="normal"):
        st = scrolledtext.ScrolledText(
            parent, height=height, font=FONTS["mono"],
            bg=COLORS["input_bg"], fg=COLORS["text"],
            insertbackground=COLORS["text"], relief="flat",
            wrap="word", state=state,
            selectbackground=COLORS["accent"]
        )
        return st

    # ─────────────────────────────────────────
    #  PAGE: HOME
    # ─────────────────────────────────────────
    def _build_home(self):
        frame = tk.Frame(self.content, bg=COLORS["bg"])

        # Hero
        hero = tk.Frame(frame, bg=COLORS["bg"], pady=40)
        hero.pack(fill="x", padx=40)
        tk.Label(hero, text="⚖  Welcome to LawPal", font=FONTS["title"],
                 bg=COLORS["bg"], fg=COLORS["white"]).pack()
        tk.Label(hero, text="Intelligent Legal Simplification & Advisory System for Everyday Use",
                 font=FONTS["body"], bg=COLORS["bg"], fg=COLORS["subtext"]).pack(pady=6)
        tk.Label(hero,
                 text="Paste confusing legal text to get a plain-language version,\n"
                      "or ask a legal question and get a clear, structured answer.",
                 font=FONTS["body"], bg=COLORS["bg"], fg=COLORS["text"],
                 justify="center").pack(pady=4)

        # Quick-action cards
        cards_row = tk.Frame(frame, bg=COLORS["bg"])
        cards_row.pack(fill="x", padx=40, pady=10)

        actions = [
            ("📝", "Simplify Legal Text",
             "Paste any legal paragraph and get\na plain-language version instantly.",
             "simplify", COLORS["accent"]),
            ("💬", "Ask a Legal Question",
             "Type your question and LawPal\nwill give you a clear answer.",
             "ask", COLORS["accent2"]),
            ("📚", "View History",
             "Review all your past queries\nand their results.",
             "history", COLORS["success"]),
        ]
        for icon, title, desc, page, color in actions:
            card = self._card(cards_row, padx=20, pady=20)
            card.pack(side="left", expand=True, fill="both", padx=10)
            tk.Label(card, text=icon, font=("Segoe UI", 28),
                     bg=COLORS["card"], fg=color).pack()
            tk.Label(card, text=title, font=FONTS["heading"],
                     bg=COLORS["card"], fg=COLORS["white"]).pack(pady=4)
            tk.Label(card, text=desc, font=FONTS["small"],
                     bg=COLORS["card"], fg=COLORS["subtext"],
                     justify="center").pack()
            self._btn(card, f"Open {title.split()[0]}", lambda p=page: self.show_page(p),
                      color=color).pack(pady=10)

        # Stats bar
        stats = self._card(frame, padx=20, pady=14)
        stats.pack(fill="x", padx=40, pady=20)
        tk.Label(stats, text="📊  System Info", font=FONTS["heading"],
                 bg=COLORS["card"], fg=COLORS["accent"]).pack(anchor="w")
        info_row = tk.Frame(stats, bg=COLORS["card"])
        info_row.pack(fill="x", pady=6)
        items = [
            (f"{len(WORD_MAP)} words", "in dictionary"),
            (f"{len(RULES)} rules", "in knowledge base"),
            ("Rule-Based NLP", "AI technique"),
            ("English", "supported language"),
            ("< 2 sec", "response target"),
        ]
        for val, lbl in items:
            col = tk.Frame(info_row, bg=COLORS["card"])
            col.pack(side="left", expand=True)
            tk.Label(col, text=val, font=FONTS["heading"],
                     bg=COLORS["card"], fg=COLORS["accent"]).pack()
            tk.Label(col, text=lbl, font=FONTS["small"],
                     bg=COLORS["card"], fg=COLORS["subtext"]).pack()

        # Disclaimer
        disc = tk.Frame(frame, bg=COLORS["warning"], pady=8)
        disc.pack(fill="x", padx=40, pady=10)
        tk.Label(disc,
                 text="⚠  LawPal provides general legal information only — NOT professional legal advice. "
                      "For serious matters, always consult a qualified lawyer.",
                 font=FONTS["small"], bg=COLORS["warning"], fg=COLORS["bg"],
                 wraplength=800).pack()

        return frame

    # ─────────────────────────────────────────
    #  PAGE: SIMPLIFY
    # ─────────────────────────────────────────
    def _build_simplify(self):
        frame = tk.Frame(self.content, bg=COLORS["bg"])

        header = tk.Frame(frame, bg=COLORS["bg"], pady=16)
        header.pack(fill="x", padx=30)
        tk.Label(header, text="📝  Simplify Legal Text", font=FONTS["title"],
                 bg=COLORS["bg"], fg=COLORS["white"]).pack(anchor="w")
        tk.Label(header, text="Paste any legal paragraph below and get a plain-language version.",
                 font=FONTS["body"], bg=COLORS["bg"], fg=COLORS["subtext"]).pack(anchor="w")

        body = tk.Frame(frame, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=30, pady=6)

        # Left: input
        left = self._card(body, padx=12, pady=12)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(left, text="Original Legal Text", font=FONTS["heading"],
                 bg=COLORS["card"], fg=COLORS["accent"]).pack(anchor="w")
        self.simp_input = self._scrolled(left, height=16)
        self.simp_input.pack(fill="both", expand=True, pady=6)

        # Example button
        def load_example():
            self.simp_input.delete("1.0", "end")
            self.simp_input.insert("end",
                "The lessee hereby agrees to indemnify the lessor against any and all losses, "
                "damages, or claims arising from the lessee's use or occupancy of the leased premises, "
                "including but not limited to those caused by negligence or willful misconduct. "
                "Notwithstanding the aforementioned, the lessor shall forthwith notify the lessee "
                "pursuant to the provisions herein.")

        btn_row = tk.Frame(left, bg=COLORS["card"])
        btn_row.pack(fill="x")
        self._btn(btn_row, "▶  Simplify", self._run_simplify).pack(side="left", padx=(0, 8))
        self._btn(btn_row, "📄 Load Example", load_example,
                  color=COLORS["accent2"]).pack(side="left", padx=(0, 8))
        self._btn(btn_row, "🗑 Clear", lambda: (self.simp_input.delete("1.0", "end"),
                                                 self._clear_output(self.simp_output, self.simp_status)),
                  color=COLORS["danger"]).pack(side="left")

        # Right: output
        right = self._card(body, padx=12, pady=12)
        right.pack(side="left", fill="both", expand=True, padx=(8, 0))
        tk.Label(right, text="Simplified Version", font=FONTS["heading"],
                 bg=COLORS["card"], fg=COLORS["success"]).pack(anchor="w")
        self.simp_output = self._scrolled(right, height=16, state="disabled")
        self.simp_output.pack(fill="both", expand=True, pady=6)

        out_btns = tk.Frame(right, bg=COLORS["card"])
        out_btns.pack(fill="x")
        self._btn(out_btns, "📋 Copy", lambda: self._copy_text(self.simp_output),
                  color=COLORS["accent2"]).pack(side="left", padx=(0, 8))
        self._btn(out_btns, "💾 Save", lambda: self._save_text(self.simp_output),
                  color=COLORS["success"]).pack(side="left")

        self.simp_status = tk.Label(frame, text="", font=FONTS["small"],
                                    bg=COLORS["bg"], fg=COLORS["subtext"])
        self.simp_status.pack(anchor="w", padx=30, pady=4)

        return frame

    def _run_simplify(self):
        text = self.simp_input.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Empty Input", "Please paste some legal text first.")
            return
        result, elapsed = simplify_text(text)
        self._set_output(self.simp_output, result)
        self.simp_status.config(
            text=f"✅  Done in {elapsed}s  |  {len(text.split())} words in → {len(result.split())} words out",
            fg=COLORS["success"])
        add_history("Simplify", text, result, elapsed=elapsed)

    # ─────────────────────────────────────────
    #  PAGE: ASK
    # ─────────────────────────────────────────
    def _build_ask(self):
        frame = tk.Frame(self.content, bg=COLORS["bg"])

        header = tk.Frame(frame, bg=COLORS["bg"], pady=16)
        header.pack(fill="x", padx=30)
        tk.Label(header, text="💬  Ask LawPal", font=FONTS["title"],
                 bg=COLORS["bg"], fg=COLORS["white"]).pack(anchor="w")
        tk.Label(header, text="Type a legal question and get a clear, structured answer.",
                 font=FONTS["body"], bg=COLORS["bg"], fg=COLORS["subtext"]).pack(anchor="w")

        # Question entry card
        q_card = self._card(frame, padx=16, pady=14)
        q_card.pack(fill="x", padx=30, pady=6)
        tk.Label(q_card, text="Your Question", font=FONTS["heading"],
                 bg=COLORS["card"], fg=COLORS["accent"]).pack(anchor="w")

        self.ask_entry = tk.Text(q_card, height=3, font=FONTS["body"],
                                 bg=COLORS["input_bg"], fg=COLORS["text"],
                                 insertbackground=COLORS["text"], relief="flat",
                                 wrap="word", selectbackground=COLORS["accent"])
        self.ask_entry.pack(fill="x", pady=6)
        self.ask_entry.bind("<Return>", lambda e: (self._run_ask(), "break"))

        btn_row = tk.Frame(q_card, bg=COLORS["card"])
        btn_row.pack(fill="x")
        self._btn(btn_row, "🔍  Ask", self._run_ask).pack(side="left", padx=(0, 8))
        self._btn(btn_row, "🗑 Clear", self._clear_ask, color=COLORS["danger"]).pack(side="left")

        # Sample questions
        samples_card = self._card(frame, padx=16, pady=10)
        samples_card.pack(fill="x", padx=30, pady=4)
        tk.Label(samples_card, text="💡  Sample Questions  (click to try)",
                 font=FONTS["heading"], bg=COLORS["card"], fg=COLORS["accent2"]).pack(anchor="w", pady=(0, 6))

        samples = [
            "Can my landlord enter my room without permission?",
            "What happens if I break my contract?",
            "What are my rights if I get a traffic fine?",
            "Can I be suspended from university without a hearing?",
            "What are my rights if I am arrested?",
            "Can my landlord keep my deposit?",
        ]
        sample_row1 = tk.Frame(samples_card, bg=COLORS["card"])
        sample_row1.pack(fill="x")
        sample_row2 = tk.Frame(samples_card, bg=COLORS["card"])
        sample_row2.pack(fill="x", pady=4)

        for i, q in enumerate(samples):
            row = sample_row1 if i < 3 else sample_row2
            tk.Button(row, text=q, font=FONTS["small"],
                      bg=COLORS["hover"], fg=COLORS["text"],
                      relief="flat", padx=8, pady=4, cursor="hand2",
                      wraplength=220, justify="left",
                      activebackground=COLORS["accent"],
                      command=lambda s=q: self._load_sample_q(s)
                      ).pack(side="left", padx=4, fill="x", expand=True)

        # Answer card
        ans_card = self._card(frame, padx=16, pady=14)
        ans_card.pack(fill="both", expand=True, padx=30, pady=6)

        ans_header = tk.Frame(ans_card, bg=COLORS["card"])
        ans_header.pack(fill="x")
        tk.Label(ans_header, text="Answer", font=FONTS["heading"],
                 bg=COLORS["card"], fg=COLORS["success"]).pack(side="left")
        self.ask_topic_label = tk.Label(ans_header, text="", font=FONTS["small"],
                                        bg=COLORS["card"], fg=COLORS["accent2"])
        self.ask_topic_label.pack(side="left", padx=10)

        self.ask_output = self._scrolled(ans_card, height=10, state="disabled")
        self.ask_output.pack(fill="both", expand=True, pady=6)

        out_btns = tk.Frame(ans_card, bg=COLORS["card"])
        out_btns.pack(fill="x")
        self._btn(out_btns, "📋 Copy", lambda: self._copy_text(self.ask_output),
                  color=COLORS["accent2"]).pack(side="left", padx=(0, 8))
        self._btn(out_btns, "💾 Save", lambda: self._save_text(self.ask_output),
                  color=COLORS["success"]).pack(side="left")

        self.ask_status = tk.Label(frame, text="", font=FONTS["small"],
                                   bg=COLORS["bg"], fg=COLORS["subtext"])
        self.ask_status.pack(anchor="w", padx=30, pady=2)

        return frame

    def _load_sample_q(self, q):
        self.ask_entry.delete("1.0", "end")
        self.ask_entry.insert("end", q)

    def _run_ask(self):
        text = self.ask_entry.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Empty Input", "Please type a question first.")
            return
        topic, answer, elapsed = answer_question(text)
        self._set_output(self.ask_output, answer)
        self.ask_topic_label.config(text=f"Topic: {topic}")
        self.ask_status.config(
            text=f"✅  Answered in {elapsed}s",
            fg=COLORS["success"])
        add_history("Ask", text, answer, topic=topic, elapsed=elapsed)

    def _clear_ask(self):
        self.ask_entry.delete("1.0", "end")
        self._set_output(self.ask_output, "")
        self.ask_topic_label.config(text="")
        self.ask_status.config(text="")

    # ─────────────────────────────────────────
    #  PAGE: HISTORY
    # ─────────────────────────────────────────
    def _build_history(self):
        frame = tk.Frame(self.content, bg=COLORS["bg"])

        header = tk.Frame(frame, bg=COLORS["bg"], pady=16)
        header.pack(fill="x", padx=30)
        tk.Label(header, text="📚  History", font=FONTS["title"],
                 bg=COLORS["bg"], fg=COLORS["white"]).pack(anchor="w")
        tk.Label(header, text="All your past queries and results.",
                 font=FONTS["body"], bg=COLORS["bg"], fg=COLORS["subtext"]).pack(anchor="w")

        btn_row = tk.Frame(frame, bg=COLORS["bg"])
        btn_row.pack(fill="x", padx=30, pady=4)
        self._btn(btn_row, "🗑 Clear History", self._clear_history,
                  color=COLORS["danger"]).pack(side="left", padx=(0, 8))
        self._btn(btn_row, "💾 Export History", self._export_history,
                  color=COLORS["success"]).pack(side="left")

        # Treeview
        tree_card = self._card(frame, padx=10, pady=10)
        tree_card.pack(fill="both", expand=True, padx=30, pady=6)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                         background=COLORS["input_bg"],
                         foreground=COLORS["text"],
                         fieldbackground=COLORS["input_bg"],
                         rowheight=28,
                         font=FONTS["body"])
        style.configure("Treeview.Heading",
                         background=COLORS["card"],
                         foreground=COLORS["accent"],
                         font=FONTS["heading"])
        style.map("Treeview", background=[("selected", COLORS["accent"])])

        cols = ("#", "Time", "Type", "Topic", "Input Preview", "Speed")
        self.hist_tree = ttk.Treeview(tree_card, columns=cols, show="headings", height=12)
        widths = [40, 140, 80, 160, 320, 70]
        for col, w in zip(cols, widths):
            self.hist_tree.heading(col, text=col)
            self.hist_tree.column(col, width=w, anchor="w")

        vsb = ttk.Scrollbar(tree_card, orient="vertical", command=self.hist_tree.yview)
        self.hist_tree.configure(yscrollcommand=vsb.set)
        self.hist_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.hist_tree.bind("<Double-1>", self._view_history_item)

        # Detail panel
        detail_card = self._card(frame, padx=12, pady=10)
        detail_card.pack(fill="x", padx=30, pady=4)
        tk.Label(detail_card, text="Double-click a row to view full details",
                 font=FONTS["small"], bg=COLORS["card"], fg=COLORS["subtext"]).pack(anchor="w")
        self.hist_detail = self._scrolled(detail_card, height=6, state="disabled")
        self.hist_detail.pack(fill="x")

        return frame

    def _refresh_history(self):
        self.hist_tree.delete(*self.hist_tree.get_children())
        for i, h in enumerate(reversed(history), 1):
            preview = h["input"][:60].replace("\n", " ") + ("…" if len(h["input"]) > 60 else "")
            self.hist_tree.insert("", "end", iid=str(i), values=(
                i, h["timestamp"], h["type"], h.get("topic", "—"),
                preview, f"{h['time']}s"
            ))

    def _view_history_item(self, event):
        sel = self.hist_tree.selection()
        if not sel:
            return
        idx = int(sel[0]) - 1
        item = list(reversed(history))[idx]
        detail = (
            f"[{item['timestamp']}]  Type: {item['type']}  |  Topic: {item.get('topic','—')}  |  Speed: {item['time']}s\n"
            f"{'─'*60}\n"
            f"INPUT:\n{item['input']}\n\n"
            f"OUTPUT:\n{item['output']}\n"
        )
        self._set_output(self.hist_detail, detail)

    def _clear_history(self):
        if messagebox.askyesno("Clear History", "Are you sure you want to clear all history?"):
            history.clear()
            self._refresh_history()
            self._set_output(self.hist_detail, "")

    def _export_history(self):
        if not history:
            messagebox.showinfo("Export", "No history to export yet.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt")],
            title="Export History"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Exported", f"History saved to:\n{path}")

    # ─────────────────────────────────────────
    #  PAGE: ABOUT
    # ─────────────────────────────────────────
    def _build_about(self):
        frame = tk.Frame(self.content, bg=COLORS["bg"])

        canvas = tk.Canvas(frame, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=COLORS["bg"])
        canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        def section(title, color=COLORS["accent"]):
            tk.Label(inner, text=title, font=FONTS["heading"],
                     bg=COLORS["bg"], fg=color).pack(anchor="w", padx=40, pady=(18, 4))
            ttk.Separator(inner, orient="horizontal").pack(fill="x", padx=40, pady=2)

        def para(text):
            tk.Label(inner, text=text, font=FONTS["body"],
                     bg=COLORS["bg"], fg=COLORS["text"],
                     wraplength=700, justify="left").pack(anchor="w", padx=50, pady=3)

        # Hero
        tk.Label(inner, text="⚖  LawPal", font=FONTS["logo"],
                 bg=COLORS["bg"], fg=COLORS["white"]).pack(pady=(30, 4))
        tk.Label(inner, text="Intelligent Legal Simplification & Advisory System for Everyday Use",
                 font=FONTS["body"], bg=COLORS["bg"], fg=COLORS["subtext"]).pack()
        tk.Label(inner, text="Madda Walabu University  |  College of Computing  |  Dept. of Computer Science",
                 font=FONTS["small"], bg=COLORS["bg"], fg=COLORS["subtext"]).pack(pady=2)

        section("📌  What is LawPal?")
        para("LawPal is an AI-based system designed to make legal information more understandable and "
             "accessible. It allows users to paste legal text and receive a simplified version in everyday "
             "language, and to ask legal-related questions and receive clear, structured answers.")
        para("LawPal uses rule-based logic and basic Natural Language Processing (NLP). The goal is not to "
             "replace lawyers, but to act as a helpful tool that explains legal information in a way that is "
             "easier for people to understand.")

        section("🎯  Objectives")
        objectives = [
            "Convert complex legal text into simple, everyday language",
            "Respond to common legal questions clearly and accurately",
            "Improve access to legal information for people without a legal background",
            "Demonstrate the use of AI techniques in solving real-world problems",
        ]
        for obj in objectives:
            tk.Label(inner, text=f"  ✔  {obj}", font=FONTS["body"],
                     bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w", padx=50)

        section("⚙️  How It Works")
        steps = [
            ("Step 1", "User types a legal paragraph or a question."),
            ("Step 2", "LawPal detects whether it is a paragraph or a question."),
            ("Step 3a", "Paragraph → Simplification Module: replaces hard words, shortens sentences."),
            ("Step 3b", "Question → Advisory Module: matches keywords to rule base, returns answer."),
            ("Step 4", "Result is displayed in under 2 seconds."),
        ]
        for step, desc in steps:
            row = tk.Frame(inner, bg=COLORS["bg"])
            row.pack(anchor="w", padx=50, pady=2)
            tk.Label(row, text=f"{step}:", font=FONTS["heading"],
                     bg=COLORS["bg"], fg=COLORS["accent"], width=8, anchor="w").pack(side="left")
            tk.Label(row, text=desc, font=FONTS["body"],
                     bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left")

        section("⚠️  Limitations")
        limits = [
            "Does NOT replace a professional lawyer",
            "Currently supports English only (no Amharic or Afan Oromo)",
            "Covers limited topics: traffic, school, contracts, basic rights",
            "Uses simple rule-based AI — may struggle with very complex questions",
            "Simplification may not always preserve every legal nuance perfectly",
        ]
        for lim in limits:
            tk.Label(inner, text=f"  ✖  {lim}", font=FONTS["body"],
                     bg=COLORS["bg"], fg=COLORS["warning"]).pack(anchor="w", padx=50)

        section("👩‍💻  Project Info", color=COLORS["accent2"])
        info = [
            ("Prepared by", "Rahma Jemal  (ID: UGRR/52265/1)"),
            ("Submitted to", "Mr. Shume.B"),
            ("University", "Madda Walabu University"),
            ("Department", "Computer Science"),
            ("Language", "Python  (Tkinter + NLTK + re)"),
            ("Version", "1.0"),
        ]
        for label, val in info:
            row = tk.Frame(inner, bg=COLORS["bg"])
            row.pack(anchor="w", padx=50, pady=1)
            tk.Label(row, text=f"{label}:", font=FONTS["heading"],
                     bg=COLORS["bg"], fg=COLORS["subtext"], width=14, anchor="w").pack(side="left")
            tk.Label(row, text=val, font=FONTS["body"],
                     bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left")

        section("📚  References")
        refs = [
            "Ethiopian Traffic Proclamation No. 1151/2019",
            "Constitution of the Federal Democratic Republic of Ethiopia (1995)",
            "Madda Walabu University Student Code of Conduct (2022)",
            "Bird, Klein & Loper — Natural Language Processing with Python (O'Reilly, 2009)",
            "Susskind — Online Courts and the Future of Justice (Oxford, 2019)",
            "NLTK Project — Natural Language Toolkit (nltk.org, 2024)",
        ]
        for ref in refs:
            tk.Label(inner, text=f"  •  {ref}", font=FONTS["small"],
                     bg=COLORS["bg"], fg=COLORS["subtext"]).pack(anchor="w", padx=50)

        tk.Label(inner, text="\n", bg=COLORS["bg"]).pack()
        return frame

    # ─────────────────────────────────────────
    #  UTILITY METHODS
    # ─────────────────────────────────────────
    def _set_output(self, widget, text):
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("end", text)
        widget.config(state="disabled")

    def _clear_output(self, widget, status_label=None):
        self._set_output(widget, "")
        if status_label:
            status_label.config(text="")

    def _copy_text(self, widget):
        text = widget.get("1.0", "end").strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            messagebox.showinfo("Copied", "Text copied to clipboard.")

    def _save_text(self, widget):
        text = widget.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Nothing to Save", "There is no output to save yet.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            title="Save Output"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("Saved", f"Output saved to:\n{path}")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = LawPalApp()
    app.mainloop()
