# YT-DLP GUI cho Windows

Ứng dụng giao diện tiếng Việt giúp tải video hoặc âm thanh bằng `yt-dlp` mà không cần nhập lệnh thủ công.

## Cài bằng Setup.exe

1. Tải `YT-DLP-GUI-Setup-1.0.0.exe` từ mục **Releases** của repository, hoặc dùng file trong thư mục `release` nếu bạn tự build.
2. Mở file và hoàn thành các bước trong bộ cài.
3. Mở **YT-DLP GUI** từ Start Menu.
4. Ở lần chạy đầu, đồng ý cài `yt-dlp`, FFmpeg và Deno. Máy cần kết nối Internet và có Winget (App Installer của Microsoft).

## Sử dụng

1. Dán link video.
2. Chọn thư mục lưu bằng nút **Chọn...**.
3. Chọn định dạng video hoặc âm thanh.
4. Chọn tải playlist/phụ đề nếu cần.
5. Nhấn **Bắt đầu tải**.

Ứng dụng tự sửa link bị sao chép ở dạng Markdown như `[YouTube](https://youtube.com/...)` và báo rõ khi chọn một ổ đĩa không tồn tại.

## Chạy trực tiếp từ mã nguồn

Yêu cầu Python 3.10 trở lên. Clone repository rồi chạy:

```powershell
python app.py
```

Nếu máy chưa có các thành phần tải video, ứng dụng sẽ đề nghị cài tự động bằng Winget ở lần mở đầu tiên.

## Tự build bộ cài

Yêu cầu trên máy build:

- Windows 10/11 64-bit
- Python 3.10 trở lên
- Inno Setup 6

Cài Inno Setup:

```powershell
winget install --id JRSoftware.InnoSetup --exact
```

Chạy PowerShell trong thư mục dự án:

```powershell
.\build.ps1
```

File cài đặt được tạo trong thư mục `release`.

## Nguồn mở được sử dụng và lời cảm ơn

Giao diện trong repository này là mã nguồn riêng, hoạt động như một lớp giao diện gọi chương trình dòng lệnh `yt-dlp`. Bộ cài không nhúng `yt-dlp`, FFmpeg hay Deno; khi người dùng đồng ý, các thành phần chính thức được Windows Package Manager tải và cài riêng theo giấy phép của từng dự án.

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** — bộ máy tải video/âm thanh chính. Dự án là nhánh phát triển từ `youtube-dl` và `youtube-dlc`; mã nguồn repository dùng giấy phép Unlicense, còn một số bản phát hành đóng gói có điều khoản giấy phép bổ sung.
- **[FFmpeg](https://ffmpeg.org/)** và **[FFmpeg Builds for yt-dlp](https://github.com/yt-dlp/FFmpeg-Builds)** — ghép luồng video/âm thanh và chuyển đổi định dạng. Giấy phép phụ thuộc vào bản build được cài.
- **[Deno](https://github.com/denoland/deno)** — JavaScript runtime được yt-dlp khuyến nghị để hỗ trợ đầy đủ việc trích xuất nội dung; dự án dùng giấy phép MIT.
- **[Python](https://www.python.org/)** và **Tkinter** — ngôn ngữ và thư viện giao diện dùng để xây dựng ứng dụng.
- **[PyInstaller](https://github.com/pyinstaller/pyinstaller)** — đóng gói ứng dụng Python thành file EXE chạy độc lập.
- **[Inno Setup](https://jrsoftware.org/isinfo.php)** — tạo bộ cài Windows `Setup.exe`.

Xin chân thành cảm ơn các tác giả, maintainer và cộng đồng đóng góp của yt-dlp, youtube-dl, youtube-dlc, FFmpeg, Deno, Python, PyInstaller và Inno Setup. Nếu không có công sức của họ, ứng dụng giao diện nhỏ này sẽ không thể hoạt động.

Tên và nhãn hiệu của các dự án trên thuộc về chủ sở hữu tương ứng. YT-DLP GUI không phải ứng dụng chính thức và không được các dự án đó bảo trợ.

Chỉ tải nội dung khi bạn có quyền tải và sử dụng.
