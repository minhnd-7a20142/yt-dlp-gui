import unittest

from core import build_download_command, is_supported_url, normalize_url


class CoreTests(unittest.TestCase):
    def test_normal_url_is_unchanged(self):
        url = "https://example.com/watch?v=demo"
        self.assertEqual(normalize_url(url), url)

    def test_markdown_url_is_repaired(self):
        value = "[Video](https://example.com/watch?v=demo)"
        self.assertEqual(normalize_url(value), "https://example.com/watch?v=demo")

    def test_url_validation(self):
        self.assertTrue(is_supported_url("https://example.com/video"))
        self.assertFalse(is_supported_url("example.com/video"))

    def test_mp3_command(self):
        command = build_download_command(
            "yt-dlp.exe",
            "https://example.com/video",
            r"E:\Nhạc",
            "audio_mp3",
            playlist=False,
            subtitles=False,
            ffmpeg_path=r"C:\Tools\ffmpeg.exe",
        )
        self.assertIn("--audio-format", command)
        self.assertIn("mp3", command)
        self.assertIn("--no-playlist", command)
        self.assertEqual(command[-1], "https://example.com/video")


if __name__ == "__main__":
    unittest.main()
