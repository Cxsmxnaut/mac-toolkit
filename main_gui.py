"""Tkinter GUI for Mac Toolkit."""

from __future__ import annotations

import contextlib
import queue
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from modules.auto_service import run_auto_service
from modules.diagnostics_engine import run_diagnostics
from modules.report.generator import generate_reports
from modules.stress_engine import run_stress_tests
from modules.system import display_system_info, get_system_info


class TextRedirector:
    """Redirect writes into a queue consumed by the Tk event loop."""

    def __init__(self, output_queue: queue.Queue[str]) -> None:
        self.output_queue = output_queue

    def write(self, value: str) -> int:
        if value:
            self.output_queue.put(value)
        return len(value)

    def flush(self) -> None:
        """Satisfy file-like interface."""


class MacToolkitApp(tk.Tk):
    """Small GUI wrapper around the Mac Toolkit workflows."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Mac Toolkit")
        self.geometry("980x680")
        self.minsize(760, 520)
        self.output_queue: queue.Queue[str] = queue.Queue()
        self.worker: threading.Thread | None = None
        self._build_ui()
        self.after(100, self._drain_output)

    def _build_ui(self) -> None:
        header = ttk.Frame(self, padding=(16, 14, 16, 8))
        header.pack(fill=tk.X)
        ttk.Label(header, text="Mac Toolkit", font=("Helvetica", 22, "bold")).pack(side=tk.LEFT)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(header, textvariable=self.status_var).pack(side=tk.RIGHT)

        actions = ttk.Frame(self, padding=(16, 8))
        actions.pack(fill=tk.X)

        buttons = [
            ("Auto Service", self.run_auto_service_task),
            ("Diagnostics", self.run_diagnostics_task),
            ("System Info", self.run_system_info_task),
            ("Reports", self.run_reports_task),
            ("Stress Tests", self.run_stress_task),
            ("Clear Output", self.clear_output),
        ]
        for label, command in buttons:
            ttk.Button(actions, text=label, command=command).pack(side=tk.LEFT, padx=(0, 8))

        output_frame = ttk.Frame(self, padding=(16, 8, 16, 16))
        output_frame.pack(fill=tk.BOTH, expand=True)
        self.output = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, font=("Menlo", 12), state=tk.DISABLED)
        self.output.pack(fill=tk.BOTH, expand=True)

    def _run_task(self, title: str, func) -> None:
        if self.worker and self.worker.is_alive():
            messagebox.showinfo("Mac Toolkit", "A task is already running.")
            return

        self.status_var.set(f"Running {title}...")
        self._append(f"\n=== {title} ===\n")

        def target() -> None:
            redirector = TextRedirector(self.output_queue)
            try:
                with contextlib.redirect_stdout(redirector), contextlib.redirect_stderr(redirector):
                    func()
            except Exception as exc:
                self.output_queue.put(f"\nERROR: {exc}\n")
            finally:
                self.output_queue.put(f"\n=== {title} complete ===\n")
                self.output_queue.put("__TASK_DONE__")

        self.worker = threading.Thread(target=target, daemon=True)
        self.worker.start()

    def _drain_output(self) -> None:
        while True:
            try:
                value = self.output_queue.get_nowait()
            except queue.Empty:
                break
            if value == "__TASK_DONE__":
                self.status_var.set("Ready")
            else:
                self._append(value)
        self.after(100, self._drain_output)

    def _append(self, value: str) -> None:
        self.output.configure(state=tk.NORMAL)
        self.output.insert(tk.END, value)
        self.output.see(tk.END)
        self.output.configure(state=tk.DISABLED)

    def clear_output(self) -> None:
        self.output.configure(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.configure(state=tk.DISABLED)

    def run_auto_service_task(self) -> None:
        self._run_task("Auto Service", lambda: run_auto_service(show_progress=False))

    def run_diagnostics_task(self) -> None:
        self._run_task("Diagnostics", lambda: run_diagnostics(show_progress=False))

    def run_system_info_task(self) -> None:
        self._run_task("System Information", display_system_info)

    def run_reports_task(self) -> None:
        def task() -> None:
            results = run_diagnostics(show_progress=False)
            files = generate_reports(results, get_system_info(), formats=["txt", "json", "html", "pdf"])
            print("\nReports generated:")
            for report_type, path in files.items():
                print(f"{report_type.upper()}: {path}")

        self._run_task("Reports", task)

    def run_stress_task(self) -> None:
        if not messagebox.askyesno("Run Stress Tests?", "Stress tests intentionally load CPU, memory, and disk. Continue?"):
            return
        self._run_task("Stress Tests", lambda: run_stress_tests(show_progress=False))


def main() -> None:
    """Launch the Mac Toolkit GUI."""
    app = MacToolkitApp()
    app.mainloop()


if __name__ == "__main__":
    main()
