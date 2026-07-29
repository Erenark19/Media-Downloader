import os
import sys
import threading
import io
import requests
import customtkinter as ctk
from PIL import Image
import yt_dlp

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class VideoDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Media Downloader")
        self.geometry("650x760")
        self.resizable(False, False)

        self.video_info = None

        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=30, pady=(30, 15))
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="Media Downloader", 
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold")
        )
        self.title_label.pack(anchor="w")
        
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame, 
            text="Videoları en yüksek kalitede, hızlıca indirin.", 
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="gray70"
        )
        self.subtitle_label.pack(anchor="w")

        self.url_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.url_frame.pack(fill="x", padx=30, pady=(0, 15))

        self.url_entry = ctk.CTkEntry(
            self.url_frame,
            placeholder_text="Video bağlantısını buraya yapıştırın...",
            height=45,
            font=ctk.CTkFont(size=14),
            corner_radius=8
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.fetch_button = ctk.CTkButton(
            self.url_frame, 
            text="Bul", 
            width=100, 
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=8,
            command=self.start_fetch_info
        )
        self.fetch_button.pack(side="right")

        self.status_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=13, slant="italic")
        )
        self.status_label.pack(pady=(0, 5))

        self.card_frame = ctk.CTkFrame(self, height=200, corner_radius=12)
        self.card_frame.pack(fill="x", padx=30, pady=10)
        self.card_frame.pack_propagate(False)

        self.thumb_label = ctk.CTkLabel(
            self.card_frame, 
            text="Görsel bekleniyor...", 
            width=220, 
            height=160,
            fg_color=("gray80", "gray20"),
            corner_radius=8
        )
        self.thumb_label.pack(side="left", padx=20, pady=20)

        self.info_subframe = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.info_subframe.pack(side="right", fill="both", expand=True, padx=(0, 20), pady=20)

        self.video_title_label = ctk.CTkLabel(
            self.info_subframe,
            text="Video başlığı burada görünecek...",
            wraplength=300,
            justify="left",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.video_title_label.pack(anchor="nw", pady=(5, 10))

        self.video_duration_label = ctk.CTkLabel(
            self.info_subframe,
            text="Süre: --:--",
            font=ctk.CTkFont(size=13),
            text_color="gray70"
        )
        self.video_duration_label.pack(anchor="w")

        self.settings_frame = ctk.CTkFrame(self, corner_radius=12)
        self.settings_frame.pack(fill="x", padx=30, pady=15)

        self.settings_grid = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.settings_grid.pack(padx=20, pady=20, fill="x")

        self.format_label = ctk.CTkLabel(self.settings_grid, text="İndirme Formatı:", font=ctk.CTkFont(weight="bold"))
        self.format_label.grid(row=0, column=0, padx=(0, 20), pady=10, sticky="w")

        self.format_option = ctk.CTkOptionMenu(
            self.settings_grid, 
            values=["MP4 (Görüntü + Ses)", "MP3 (Sadece Ses)"],
            width=200,
            corner_radius=8
        )
        self.format_option.grid(row=0, column=1, pady=10, sticky="w")

        self.quality_label = ctk.CTkLabel(self.settings_grid, text="Video Kalitesi:", font=ctk.CTkFont(weight="bold"))
        self.quality_label.grid(row=1, column=0, padx=(0, 20), pady=10, sticky="w")

        self.quality_option = ctk.CTkOptionMenu(
            self.settings_grid,
            values=["En Yüksek Kalite", "1080p", "720p", "480p"],
            width=200,
            corner_radius=8
        )
        self.quality_option.grid(row=1, column=1, pady=10, sticky="w")

        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(fill="x", padx=30, pady=(15, 30), side="bottom")

        self.progress_bar = ctk.CTkProgressBar(self.action_frame, height=8, corner_radius=4)
        self.progress_bar.pack(fill="x", pady=(0, 15))
        self.progress_bar.set(0)

        self.download_button = ctk.CTkButton(
            self.action_frame,
            text="İNDİRMEYİ BAŞLAT",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=8,
            command=self.start_download,
            state="disabled"
        )
        self.download_button.pack(fill="x")


    def start_fetch_info(self):
        url = self.url_entry.get().strip()
        if not url:
            self.status_label.configure(text="Lütfen geçerli bir URL girin!", text_color="#ff5555")
            return

        self.status_label.configure(text="Video bilgileri getiriliyor...", text_color="gray70")
        self.fetch_button.configure(state="disabled")
        threading.Thread(target=self.fetch_video_info, args=(url,), daemon=True).start()

    def fetch_video_info(self, url):
        ydl_opts = {"quiet": True, "no_warnings": True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.video_info = info

                title = info.get("title", "Başlık Bulunamadı")
                duration_sec = info.get("duration", 0)
                thumbnail_url = info.get("thumbnail", None)

                mins, secs = divmod(duration_sec, 60)
                hours, mins = divmod(mins, 60)
                duration_str = f"{hours:02d}:{mins:02d}:{secs:02d}" if hours else f"{mins:02d}:{secs:02d}"

                img_obj = None
                if thumbnail_url:
                    res = requests.get(thumbnail_url)
                    if res.status_code == 200:
                        raw_img = Image.open(io.BytesIO(res.content))
                        img_obj = ctk.CTkImage(light_image=raw_img, dark_image=raw_img, size=(200, 140))

                self.after(0, self.update_preview_ui, title, duration_str, img_obj)
        except Exception as e:
            self.after(0, lambda: self.status_label.configure(text="Video bilgisi alınamadı!", text_color="#ff5555"))
            self.after(0, lambda: self.fetch_button.configure(state="normal"))

    def update_preview_ui(self, title, duration, img_obj):
        self.video_title_label.configure(text=title)
        self.video_duration_label.configure(text=f"Süre: {duration}")

        if img_obj:
            self.thumb_label.configure(image=img_obj, text="", fg_color="transparent")

        self.status_label.configure(text="Video başarıyla yüklendi, indirmeye hazır.", text_color="#2ecc71")
        self.fetch_button.configure(state="normal")
        self.download_button.configure(state="normal")

    def start_download(self):
        if not self.video_info:
            return

        self.download_button.configure(state="disabled")
        self.status_label.configure(text="İndirme başlatıldı, lütfen bekleyin...", text_color="#f39c12")
        threading.Thread(target=self.download_process, daemon=True).start()

    def progress_hook(self, d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            if total > 0:
                percentage = downloaded / total
                self.after(0, lambda: self.progress_bar.set(percentage))
                self.after(0, lambda: self.status_label.configure(text=f"İndiriliyor: %{int(percentage * 100)}", text_color="#3498db"))
        elif d["status"] == "finished":
            self.after(0, lambda: self.progress_bar.set(1.0))
            self.after(0, lambda: self.status_label.configure(text="İndirme Tamamlandı! Dosya 'İndirilenler' klasöründe.", text_color="#2ecc71"))
            self.after(0, lambda: self.download_button.configure(state="normal"))

    def download_process(self):
        import os
        import sys
        
        fmt = self.format_option.get()
        quality = self.quality_option.get()
        
        if getattr(sys, 'frozen', False):
            current_dir = os.path.dirname(sys.executable)
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
        ffmpeg_path = os.path.join(current_dir, "ffmpeg.exe")
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        output_template = os.path.join(downloads_folder, "%(title)s.%(ext)s")

        ydl_opts = {
            "progress_hooks": [self.progress_hook],
            "outtmpl": output_template,
            "ffmpeg_location": ffmpeg_path,
        }

        if fmt.startswith("MP3"):
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
        else:
            if quality == "1080p":
                ydl_opts["format"] = "bestvideo[height<=1080]+bestaudio/best"
            elif quality == "720p":
                ydl_opts["format"] = "bestvideo[height<=720]+bestaudio/best"
            elif quality == "480p":
                ydl_opts["format"] = "bestvideo[height<=480]+bestaudio/best"
            else:
                ydl_opts["format"] = "bestvideo+bestaudio/best"

        url = self.url_entry.get().strip()
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            error_message = str(e)[:60]
            self.after(0, lambda msg=error_message: self.status_label.configure(text=f"Hata: {msg}", text_color="#ff5555"))
            self.after(0, lambda: self.download_button.configure(state="normal"))

if __name__ == "__main__":
    app = VideoDownloaderApp()
    app.mainloop()