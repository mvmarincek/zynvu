"""Small native desktop advisor using the same public SDK."""

import json
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any

from zynvu.contracts import Requirements
from zynvu.engine import advise
from zynvu.export import report
from zynvu.hardware import diagnose
from zynvu.requirements import parse_goal


def launch() -> None:
    root = tk.Tk()
    root.title("ZYNVU · Advisor local de IA")
    root.geometry("1020x780")
    root.minsize(760, 600)
    root.configure(bg="#101720")
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TFrame", background="#101720")
    style.configure("TLabel", background="#101720", foreground="#e6edf3", font=("Segoe UI", 11))
    style.configure("Title.TLabel", font=("Segoe UI", 26, "bold"))
    style.configure("TButton", font=("Segoe UI", 11), padding=10)
    panel = ttk.Frame(root, padding=24)
    panel.pack(fill="both", expand=True)
    ttk.Label(panel, text="ZYNVU", style="Title.TLabel").pack(anchor="w")
    ttk.Label(panel, text="Descreva seu agente. Planeje com os recursos da sua máquina.").pack(
        anchor="w"
    )
    ttk.Label(panel, text="01  Objetivo do agente", padding=(0, 16, 0, 6)).pack(anchor="w")
    goal = tk.Text(
        panel,
        height=3,
        font=("Segoe UI", 12),
        bg="#1b2635",
        fg="white",
        insertbackground="white",
        wrap="word",
    )
    goal.insert("1.0", "Quero um assistente para conversar e ajudar a programar.")
    goal.pack(fill="x")
    ttk.Label(
        panel, text="02  Revise os requisitos antes de gerar (JSON editável)", padding=(0, 14, 0, 6)
    ).pack(anchor="w")
    editor = tk.Text(
        panel,
        height=8,
        font=("Consolas", 10),
        bg="#1b2635",
        fg="#addcc9",
        insertbackground="white",
        wrap="word",
    )
    editor.pack(fill="x")
    buttons = ttk.Frame(panel)
    buttons.pack(fill="x", pady=12)
    status = tk.StringVar(value="Local e offline · nenhuma instalação ou execução de modelos")
    ttk.Label(panel, textvariable=status, wraplength=900).pack(anchor="w")
    output = tk.Text(
        panel,
        height=12,
        font=("Segoe UI", 10),
        bg="#0c121a",
        fg="#e6edf3",
        wrap="word",
        state="disabled",
    )
    output.pack(fill="both", expand=True, pady=(10, 0))
    result: dict[str, Any] | None = None
    messages: queue.Queue[dict[str, Any] | None] = queue.Queue()
    busy = False

    def extract() -> None:
        try:
            req = parse_goal(goal.get("1.0", "end").strip())
            editor.delete("1.0", "end")
            editor.insert("1.0", json.dumps(req.to_dict(), indent=2, ensure_ascii=False))
        except ValueError:
            messagebox.showerror("Objetivo", "Descreva o que seu agente deve fazer.")

    def generate() -> None:
        nonlocal busy
        if busy:
            return
        try:
            req = Requirements(**json.loads(editor.get("1.0", "end")))
        except (ValueError, TypeError):
            messagebox.showerror("Requisitos", "Revise o JSON e as capacidades informadas.")
            return
        busy = True
        generate_button.configure(state="disabled")
        status.set("Diagnosticando hardware e calculando combinações locais…")

        def work() -> None:
            try:
                messages.put(advise(req, diagnose()))
            except Exception:
                messages.put(None)

        threading.Thread(target=work, daemon=True).start()

    def poll() -> None:
        nonlocal result, busy
        try:
            received = messages.get_nowait()
        except queue.Empty:
            root.after(100, poll)
            return
        busy = False
        generate_button.configure(state="normal")
        if received is None:
            status.set("Falha no diagnóstico. Revise os requisitos e tente novamente.")
        else:
            result = received
            output.configure(state="normal")
            output.delete("1.0", "end")
            output.insert("1.0", report(result))
            output.configure(state="disabled")
            status.set("Análise concluída. Confira as limitações e exporte o Blueprint.")
        root.after(100, poll)

    def save() -> None:
        if result is None:
            messagebox.showinfo("Exportar", "Gere a análise primeiro.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("Blueprint JSON", "*.json")]
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as destination:
                    json.dump(result, destination, indent=2, ensure_ascii=False, allow_nan=False)
                status.set("Blueprint exportado.")
            except OSError:
                messagebox.showerror("Exportar", "Não foi possível gravar nesse caminho.")

    ttk.Button(buttons, text="Extrair requisitos", command=extract).pack(side="left", padx=(0, 8))
    generate_button = ttk.Button(buttons, text="Diagnosticar e recomendar", command=generate)
    generate_button.pack(side="left", padx=(0, 8))
    ttk.Button(buttons, text="Exportar Blueprint", command=save).pack(side="left")
    extract()
    root.after(100, poll)
    root.mainloop()
