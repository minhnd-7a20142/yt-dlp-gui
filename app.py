import os
import queue
import re
import subprocess
import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from core import (
    APP_NAME,
    build_download_command,
    dependency_status,
    is_supported_url,
    normalize_url,
    refreshed_path,
)


CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0
FORMAT_OPTIONS = {
    "Video - chất lượng tốt nhất": "video_best",
    "Video - tối đa 1080p": "video_1080",
    "Video - tối đa 720p": "video_720",
    "Âm thanh - MP3": "audio_mp3",
    "Âm thanh - M4A": "audio_m4a",
}


class YtDlpGui(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.geometry("820x610")
        self.minsize(700, 520)
        self.process: subprocess.Popen[str] | None = None
        self.messages: queue.Queue[tuple[str, object]] = queue.Queue()

        self.url_var = tk.StringVar()
        self.output_var = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.format_var = tk.StringVar(value=next(iter(FORMAT_OPTIONS)))
        self.playlist_var = tk.BooleanVar(value=False)
        self.subtitles_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Sẵn sàng")

        self._build_ui()
        self.after(150, self._process_messages)
        self.after(400, self._check_dependencies_on_start)

    def _build_ui(self) -> None:
        style = ttk.Style(self)
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Hint.TLabel", foreground="#555555")
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=(14, 8))

        outer = ttk.Frame(self, padding=20)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="YT-DLP GUI", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            outer,
            text="Tải video và âm thanh bằng yt-dlp mà không cần dùng dòng lệnh.",
            style="Hint.TLabel",
        ).pack(anchor="w", pady=(2, 18))

        form = ttk.Frame(outer)
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Link video:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=6)
        self.url_entry = ttk.Entry(form, textvariable=self.url_var)
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=6)

        ttk.Label(form, text="Thư mục lưu:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=6)
        ttk.Entry(form, textvariable=self.output_var).grid(row=1, column=1, sticky="ew", pady=6)
        ttk.Button(form, text="Chọn...", command=self._choose_folder).grid(row=1, column=2, padx=(8, 0), pady=6)

        ttk.Label(form, text="Định dạng:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=6)
        self.format_box = ttk.Combobox(
            form,
            textvariable=self.format_var,
            values=list(FORMAT_OPTIONS),
            state="readonly",
        )
        self.format_box.grid(row=2, column=1, sticky="ew", pady=6)
        ttk.Button(form, text="Mở thư mục", command=self._open_output_folder).grid(
            row=2, column=2, padx=(8, 0), pady=6
        )

        options = ttk.Frame(outer)
        options.pack(fill="x", pady=(10, 8))
        ttk.Checkbutton(options, text="Tải cả playlist", variable=self.playlist_var).pack(side="left")
        ttk.Checkbutton(options, text="Tải phụ đề tiếng Việt", variable=self.subtitles_var).pack(
            side="left", padx=(24, 0)
        )

        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=(8, 8))
        self.download_button = ttk.Button(
            actions, text="Bắt đầu tải", command=self._start_download, style="Action.TButton"
        )
        self.download_button.pack(side="left")
        self.cancel_button = ttk.Button(actions, text="Hủy", command=self._cancel_download, state="disabled")
        self.cancel_button.pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="Cài/kiểm tra thành phần", command=self._install_dependencies).pack(side="right")

        self.progress = ttk.Progressbar(outer, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(4, 4))
        ttk.Label(outer, textvariable=self.status_var).pack(anchor="w", pady=(0, 8))

        log_frame = ttk.LabelFrame(outer, text="Nhật ký", padding=8)
        log_frame.pack(fill="both", expand=True)
        self.log = tk.Text(log_frame, height=12, wrap="word", state="disabled", font=("Consolas", 9))
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=scrollbar.set)
        self.log.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.url_entry.focus_set()

    def _choose_folder(self) -> None:
        initial = self.output_var.get().strip()
        folder = filedialog.askdirectory(initialdir=initial if Path(initial).exists() else str(Path.home()))
        if folder:
            self.output_var.set(folder)

    def _open_output_folder(self) -> None:
        folder = Path(self.output_var.get().strip())
        try:
            folder.mkdir(parents=True, exist_ok=True)
            os.startfile(folder)  # type: ignore[attr-defined]
        except OSError as error:
            messagebox.showerror(APP_NAME, f"Không thể mở thư mục:\n{error}")

    def _append_log(self, line: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", line.rstrip() + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _check_dependencies_on_start(self) -> None:
        status = dependency_status()
        missing = [name for name in ("yt-dlp", "ffmpeg", "deno") if not status[name]]
        if missing:
            answer = messagebox.askyesno(
                APP_NAME,
                "Ứng dụng cần cài thêm các thành phần chính thức:\n\n"
                + "\n".join(f"• {name}" for name in missing)
                + "\n\nCài tự động ngay bây giờ? (Cần Internet)",
            )
            if answer:
                self._install_dependencies()
        else:
            self.status_var.set("Sẵn sàng — các thành phần đã được cài")

    def _install_dependencies(self) -> None:
        status = dependency_status()
        if status["yt-dlp"] and status["ffmpeg"] and status["deno"]:
            messagebox.showinfo(APP_NAME, "yt-dlp, FFmpeg và Deno đã được cài đầy đủ.")
            return
        if not status["winget"]:
            messagebox.showerror(
                APP_NAME,
                "Không tìm thấy Winget. Hãy cài 'App Installer' từ Microsoft Store rồi thử lại.",
            )
            webbrowser.open("ms-windows-store://pdp/?ProductId=9NBLGGH4NNS1")
            return
        if self.process:
            return
        self.status_var.set("Đang cài yt-dlp, FFmpeg và Deno...")
        self.download_button.configure(state="disabled")
        self._append_log("Đang cài các thành phần bằng Windows Package Manager...")
        command = [
            status["winget"],
            "install",
            "--id",
            "yt-dlp.yt-dlp",
            "--exact",
            "--accept-package-agreements",
            "--accept-source-agreements",
            "--silent",
        ]
        threading.Thread(target=self._run_process, args=(command, "install"), daemon=True).start()

    def _start_download(self) -> None:
        url = normalize_url(self.url_var.get())
        output = self.output_var.get().strip()
        if not is_supported_url(url):
            messagebox.showwarning(APP_NAME, "Hãy nhập một link bắt đầu bằng http:// hoặc https://")
            self.url_entry.focus_set()
            return
        if not output:
            messagebox.showwarning(APP_NAME, "Hãy chọn thư mục lưu.")
            return

        try:
            output_path = Path(output)
            drive = output_path.drive
            if drive and not Path(drive + "\\").exists():
                raise OSError(f"Ổ đĩa {drive} không tồn tại hoặc chưa được kết nối.")
            output_path.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            messagebox.showerror(APP_NAME, f"Không thể tạo thư mục lưu:\n{error}")
            return

        status = dependency_status()
        missing = [name for name in ("yt-dlp", "ffmpeg", "deno") if not status[name]]
        if missing:
            messagebox.showwarning(APP_NAME, "Thiếu thành phần: " + ", ".join(missing) + ". Hãy cài trước.")
            self._install_dependencies()
            return

        command = build_download_command(
            yt_dlp_path=status["yt-dlp"] or "yt-dlp",
            url=url,
            output_dir=str(output_path),
            mode=FORMAT_OPTIONS[self.format_var.get()],
            playlist=self.playlist_var.get(),
            subtitles=self.subtitles_var.get(),
            ffmpeg_path=status["ffmpeg"],
        )
        self.progress.configure(value=0)
        self.status_var.set("Đang tải...")
        self.download_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self._append_log(f"Bắt đầu: {url}")
        threading.Thread(target=self._run_process, args=(command, "download"), daemon=True).start()

    def _run_process(self, command: list[str], task: str) -> None:
        env = os.environ.copy()
        env["PATH"] = refreshed_path()
        try:
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                creationflags=CREATE_NO_WINDOW,
            )
            assert self.process.stdout is not None
            for line in self.process.stdout:
                self.messages.put(("line", line))
                match = re.search(r"\[download]\s+([0-9]+(?:\.[0-9]+)?)%", line)
                if match:
                    self.messages.put(("progress", float(match.group(1))))
            return_code = self.process.wait()
            self.messages.put(("done", (task, return_code)))
        except OSError as error:
            self.messages.put(("error", str(error)))
        finally:
            self.process = None

    def _process_messages(self) -> None:
        try:
            while True:
                kind, payload = self.messages.get_nowait()
                if kind == "line":
                    self._append_log(str(payload))
                elif kind == "progress":
                    self.progress.configure(value=float(payload))
                    self.status_var.set(f"Đang tải... {float(payload):.1f}%")
                elif kind == "done":
                    task, return_code = payload  # type: ignore[misc]
                    self.download_button.configure(state="normal")
                    self.cancel_button.configure(state="disabled")
                    if return_code == 0:
                        if task == "install":
                            self.status_var.set("Đã cài thành phần — sẵn sàng")
                            messagebox.showinfo(APP_NAME, "Đã cài yt-dlp, FFmpeg và Deno thành công.")
                        else:
                            self.progress.configure(value=100)
                            self.status_var.set("Tải hoàn tất")
                            messagebox.showinfo(APP_NAME, "Đã tải xong.")
                    else:
                        self.status_var.set(f"Không thành công (mã lỗi {return_code})")
                        messagebox.showerror(APP_NAME, "Tác vụ không thành công. Xem phần Nhật ký để biết chi tiết.")
                elif kind == "error":
                    self.download_button.configure(state="normal")
                    self.cancel_button.configure(state="disabled")
                    self.status_var.set("Có lỗi")
                    messagebox.showerror(APP_NAME, str(payload))
        except queue.Empty:
            pass
        self.after(150, self._process_messages)

    def _cancel_download(self) -> None:
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.status_var.set("Đang hủy...")


if __name__ == "__main__":
    YtDlpGui().mainloop()

