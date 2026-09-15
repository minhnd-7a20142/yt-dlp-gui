import os
import re
import shutil
from pathlib import Path


APP_NAME = "YT-DLP GUI"


def normalize_url(value: str) -> str:
    """Accept a normal URL and repair links copied in Markdown format."""
    value = value.strip()
    markdown_link = re.fullmatch(r"\[[^]]+]\((https?://[^)]+)\)", value)
    if markdown_link:
        return markdown_link.group(1).strip()
    return value


def is_supported_url(value: str) -> bool:
    return bool(re.fullmatch(r"https?://\S+", normalize_url(value), re.IGNORECASE))


def refreshed_path() -> str:
    paths = [os.environ.get("PATH", "")]
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        paths.insert(0, str(Path(local_app_data) / "Microsoft" / "WinGet" / "Links"))
        ffmpeg_packages = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
        if ffmpeg_packages.exists():
            for binary in ffmpeg_packages.glob("yt-dlp.FFmpeg_*/*/bin"):
                paths.insert(0, str(binary))
    return os.pathsep.join(filter(None, paths))


def find_program(name: str) -> str | None:
    return shutil.which(name, path=refreshed_path())


def dependency_status() -> dict[str, str | None]:
    return {
        "yt-dlp": find_program("yt-dlp"),
        "ffmpeg": find_program("ffmpeg"),
        "deno": find_program("deno"),
        "winget": find_program("winget"),
    }


def build_download_command(
    yt_dlp_path: str,
    url: str,
    output_dir: str,
    mode: str,
    playlist: bool,
    subtitles: bool,
    ffmpeg_path: str | None = None,
) -> list[str]:
    command = [yt_dlp_path, "--newline", "--no-color", "-P", output_dir]

    if ffmpeg_path:
        command.extend(["--ffmpeg-location", str(Path(ffmpeg_path).parent)])

    formats = {
        "video_best": ["-f", "bv*+ba/b"],
        "video_1080": ["-f", "bv*[height<=1080]+ba/b[height<=1080]"],
        "video_720": ["-f", "bv*[height<=720]+ba/b[height<=720]"],
        "audio_mp3": ["-x", "--audio-format", "mp3", "--audio-quality", "0"],
        "audio_m4a": ["-x", "--audio-format", "m4a"],
    }
    command.extend(formats.get(mode, formats["video_best"]))

    if not playlist:
        command.append("--no-playlist")
    if subtitles:
        command.extend(["--write-subs", "--write-auto-subs", "--sub-langs", "vi.*,vi"])

    command.append(normalize_url(url))
    return command

