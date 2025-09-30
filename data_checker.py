import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
import re

df = pd.DataFrame()
col_visibility = {}
logical_to_real = {}
MAX_WIDTH = 80

# ----------------- Utility -----------------

def normalize_name(name):
    return re.sub(r"[^A-Z0-9]", "", str(name).upper())

def excel_col_name(idx):
    result = ""
    n = idx
    while True:
        n, r = divmod(n, 26)
        result = chr(65 + r) + result
        if n == 0:
            break
        n -= 1
    return result

def map_columns(df_cols):
    mapping = {}
    norm_map = {normalize_name(c): c for c in df_cols}

    aliases = {
        "ANNULLATO": ["ANNULLATO", "ANNULLATI", "ANN", "CANCELLATO"],
        "MODELLO":   ["MODELLO", "MOD", "MODEL", "MODELLOPARTE"],
        "PARTE":     ["PARTE", "ARTICOLO", "CODICEPARTE", "PART"],
        "COLORE":    ["COLORE", "COLORI", "COLOR", "CLR"]
    }

    for logic, keys in aliases.items():
        for k in keys:
            nk = normalize_name(k)
            for col_norm, real in norm_map.items():
                if col_norm == nk or col_norm.startswith(nk) or nk in col_norm:
                    mapping[logic] = real
                    break
            if logic in mapping:
                break
    return mapping

def read_csv_robust(path, header_opt=True, sep_opt="Auto"):
    seps = [None, ',', ';', '|', '\t'] if sep_opt == "Auto" else [sep_opt]
    for sep in seps:
        try:
            d = pd.read_csv(path, sep=sep, engine="python",
                            header=0 if header_opt else None,
                            dtype=str, on_bad_lines='skip', na_filter=False)
            return d
        except Exception:
            continue
    raise RuntimeError("Impossibile leggere il file.")

def is_annullato_value(val):
    s = str(val).strip()
    if s == "":
        return False
    up = s.upper()
    if up in {"SI", "SÌ", "TRUE", "Y", "YES"}:
        return True
    try:
        return float(s) > 0
    except Exception:
        return False

# ----------------- Caricamento -----------------

def carica_file():
    global df, logical_to_real
    paths = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
    if not paths:
        return
    try:
        d = read_csv_robust(paths[0], header_opt=header_var.get() == 1, sep_opt=sep_var.get())
        df = d
        logical_to_real = map_columns(df.columns)
        setup_columns()
        setup_filters_ui()
        mostra_risultati(df)
        status_label.config(text=f"Caricato: {paths[0]}", fg="lime")
    except Exception as e:
        status_label.config(text=f"Errore: {e}", fg="red")

# ----------------- Visualizzazione -----------------

def setup_columns():
    tree["columns"] = list(df.columns)
    for w in check_frame.winfo_children():
        w.destroy()
    for i, col in enumerate(df.columns):
        letter = excel_col_name(i)
        tree.heading(col, text=letter)
        width = MAX_WIDTH if col_visibility.get(col, True) else 0
        tree.column(col, width=width, stretch=False)
        var = tk.BooleanVar(value=col_visibility.get(col, True))
        chk = tk.Checkbutton(check_frame, text=letter, variable=var,
                             command=lambda c=col, v=var: toggle_colonna(c, v),
                             bg="black", fg="lime", selectcolor="black")
        chk.pack(side="left")

def toggle_colonna(col, var):
    col_visibility[col] = bool(var.get())
    tree.column(col, width=MAX_WIDTH if var.get() else 0, stretch=False)

def mostra_risultati(dataframe):
    for row in tree.get_children():
        tree.delete(row)
    if dataframe.empty:
        return
    for _, r in dataframe.iterrows():
        tree.insert("", "end", values=list(r))

# ----------------- Filtri -----------------

def setup_filters_ui():
    for widget in filtro_frame.winfo_children():
        widget.destroy()
    global annullato_var, modello_entry, parte_entry, colore_entry

    # ANNULLATO → solo checkbox
    annullato_var = tk.BooleanVar(value=False)
    if logical_to_real.get("ANNULLATO"):
        tk.Checkbutton(filtro_frame, text="ANNULLATO", variable=annullato_var,
                       bg="black", fg="lime", selectcolor="black").pack(side="left", padx=8)

    # MODELLO, PARTE, COLORE → solo entry
    def add_text_filter(label, logic_key):
        real = logical_to_real.get(logic_key)
        entry = tk.Entry(filtro_frame, bg="black", fg="lime", insertbackground="lime", width=14)
        if real:
            tk.Label(filtro_frame, text=label, bg="black", fg="lime").pack(side="left", padx=(12, 4))
            entry.pack(side="left", padx=4)
        return entry

    modello_entry = add_text_filter("MODELLO", "MODELLO")
    parte_entry   = add_text_filter("PARTE",   "PARTE")
    colore_entry  = add_text_filter("COLORE",  "COLORE")

def applica_filtri():
    global df
    if df.empty:
        return
    r = df.copy()
    # ANNULLATO: se spuntato e colonna trovata, mostra solo righe con "N"
    ann_col = logical_to_real.get("ANNULLATO")
    if annullato_var.get() and ann_col:
        r = r[r[ann_col].astype(str).str.strip().str.upper() == "N"]
    # MODELLO
    if modello_entry and modello_entry.get().strip() and logical_to_real.get("MODELLO"):
        r = r[r[logical_to_real["MODELLO"]].astype(str).str.contains(modello_entry.get().strip(), case=False, na=False)]
    # PARTE
    if parte_entry and parte_entry.get().strip() and logical_to_real.get("PARTE"):
        r = r[r[logical_to_real["PARTE"]].astype(str).str.contains(parte_entry.get().strip(), case=False, na=False)]
    # COLORE
    if colore_entry and colore_entry.get().strip() and logical_to_real.get("COLORE"):
        r = r[r[logical_to_real["COLORE"]].astype(str).str.contains(colore_entry.get().strip(), case=False, na=False)]
    mostra_risultati(r)
    status_label.config(text="Filtri applicati.", fg="lime")

def reset_filtri():
    annullato_var.set(False)
    for entry in [modello_entry, parte_entry, colore_entry]:
        if entry:
            entry.delete(0, tk.END)
    mostra_risultati(df)
    status_label.config(text="Filtri resettati.", fg="lime")

# ----------------- GUI -----------------

root = tk.Tk()
root.title("Data Checker - by Atlas")
root.configure(bg="black")

top = tk.Frame(root, bg="black")
top.pack(pady=8, fill="x")

tk.Button(top, text="Carica CSV", command=carica_file,
          bg="black", fg="lime", activebackground="green").pack(side="left", padx=6)

tk.Label(top, text="Separatore:", bg="black", fg="lime").pack(side="left")
sep_var = tk.StringVar(value="Auto")
sep_menu = tk.OptionMenu(top, sep_var, "Auto", ",", ";", "|", "\t")
sep_menu.config(bg="black", fg="lime", activebackground="green", highlightthickness=0)
sep_menu.pack(side="left", padx=6)

header_var = tk.IntVar(value=1)
tk.Checkbutton(top, text="Prima riga intestazioni", variable=header_var,
               bg="black", fg="lime", selectcolor="black").pack(side="left", padx=6)

tk.Button(top, text="Applica filtro", command=applica_filtri,
          bg="black", fg="lime", activebackground="green").pack(side="left", padx=6)
tk.Button(top, text="Reset", command=reset_filtri,
          bg="black", fg="lime", activebackground="green").pack(side="left", padx=6)

filtro_frame = tk.Frame(root, bg="black")
filtro_frame.pack(pady=4)

status_label = tk.Label(root, text="Carica un CSV e applica i filtri.",
                        bg="black", fg="lime")
status_label.pack()

# Barra checkbox colonne (per mostrare/nascondere)
check_canvas = tk.Canvas(root, height=40, bg="black", highlightthickness=0, bd=0)
check_scroll_x = tk.Scrollbar(root, orient="horizontal", command=check_canvas.xview,
                              bg="#272727", troughcolor="#91C687", activebackground="#272727")
check_frame = tk.Frame(check_canvas, bg="black")
check_frame.bind("<Configure>", lambda e: check_canvas.configure(scrollregion=check_canvas.bbox("all")))
check_canvas.create_window((0, 0), window=check_frame, anchor="nw")
check_canvas.configure(xscrollcommand=check_scroll_x.set, bg="black")
check_canvas.pack(fill="x")
check_scroll_x.pack(fill="x")

# Tabella
container = tk.Frame(root, bg="black")
container.pack(fill="both", expand=True)

scroll_x = tk.Scrollbar(container, orient="horizontal",
                        bg="#444444", troughcolor="#666666", activebackground="#888888")
scroll_y = tk.Scrollbar(container, orient="vertical",
                        bg="#444444", troughcolor="#666666", activebackground="#888888")

style = ttk.Style()
style.theme_use("default")
style.configure("Treeview",
                background="black",
                foreground="lime",
                fieldbackground="black",
                bordercolor="black",
                borderwidth=0)
style.map("Treeview", background=[("selected", "green")])

tree = ttk.Treeview(container, columns=[], show="headings",
                    xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

scroll_x.config(command=tree.xview)
scroll_y.config(command=tree.yview)

scroll_x.pack(side="bottom", fill="x")
scroll_y.pack(side="right", fill="y")
tree.pack(side="left", fill="both", expand=True)

root.mainloop()