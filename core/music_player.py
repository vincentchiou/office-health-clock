# core/music_player.py — 音樂播放模組（mbplayer 華語熱門排行榜）

from __future__ import annotations

import json
import logging
import os
import random
import re
import subprocess
import threading
from dataclasses import dataclass
from typing import Callable
from urllib.request import urlopen, Request

logger = logging.getLogger(__name__)

# 華語本週熱門排行榜 mbplayer 清單頁面
PLAYLIST_URL = "https://www.mbplayer.com/list/10086761"


@dataclass
class TrackInfo:
    """單曲資訊"""
    title: str
    youtube_id: str
    duration: int = 0  # seconds


class MusicPlayer:
    """
    音樂播放器：從 mbplayer 華語熱門排行榜抓取 YouTube ID，再用 yt-dlp 播放音訊。
    
    依賴：
    - yt-dlp：提取 YouTube 音訊 URL
    - pygame：播放音訊
    """

    def __init__(self):
        self._is_playing = False
        self._is_paused = False
        self._current_track: TrackInfo | None = None
        self._process: subprocess.Popen | None = None
        self._playlist: list[TrackInfo] = []
        self._playlist_index = 0
        self._shuffle = True
        self._volume = 0.5  # 0.0 ~ 1.0
        self._on_track_change: Callable[[TrackInfo | None], None] | None = None
        self._on_error: Callable[[str], None] | None = None
        self._lock = threading.Lock()
        self._initialized = False

    def set_callbacks(self, on_track_change=None, on_error=None):
        """設定回呼函數"""
        self._on_track_change = on_track_change
        self._on_error = on_error

    def _ensure_init(self):
        """確認 ffplay 可用。"""
        if self._initialized:
            return True
        try:
            subprocess.run(["ffplay", "-version"], capture_output=True, check=True)
            self._initialized = True
            logger.info("ffplay available")
            return True
        except Exception as ex:
            logger.error("Failed to init ffplay: %s", ex)
            return False

    # ── 公開 API ──────────────────────────────────────────

    def is_playing(self) -> bool:
        return self._is_playing and not self._is_paused

    def is_paused(self) -> bool:
        return self._is_paused

    def get_current_track(self) -> TrackInfo | None:
        return self._current_track

    def get_volume(self) -> float:
        return self._volume

    def set_volume(self, volume: float):
        """設定音量 (0.0 ~ 1.0)"""
        self._volume = max(0.0, min(1.0, volume))

    def load_playlist_async(self):
        """非同步載入播放清單"""
        threading.Thread(target=self._load_playlist, daemon=True).start()

    def play(self):
        """播放/恢復播放"""
        if not self._ensure_init():
            self._notify_error("無法初始化音訊裝置")
            return

        if self._is_paused:
            self._resume()
            return

        if not self._playlist:
            self.load_playlist_async()
            return

        self._play_current()

    def pause(self):
        """暫停播放"""
        if self._is_playing and not self._is_paused:
            self._pause()

    def stop(self):
        """停止播放"""
        self._stop()

    def next_track(self):
        """下一首"""
        if not self._playlist:
            return
        self._playlist_index = (self._playlist_index + 1) % len(self._playlist)
        if self._is_playing:
            self._play_current()

    def toggle_shuffle(self):
        """切換隨機播放"""
        self._shuffle = not self._shuffle
        if self._shuffle and self._playlist:
            random.shuffle(self._playlist)
            self._playlist_index = 0

    def shutdown(self):
        """關閉播放器"""
        self._stop()

    # ── 內部方法 ──────────────────────────────────────────

    def _load_playlist(self):
        """從 mbplayer 頁面解析播放清單（YouTube ID）"""
        try:
            logger.info("Fetching playlist from mbplayer...")
            
            req = Request(PLAYLIST_URL, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            with urlopen(req, timeout=15) as resp:
                html = resp.read().decode('utf-8')
            
            # 從 __NEXT_DATA__ JSON 解析
            match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
            if not match:
                logger.error("No __NEXT_DATA__ found in page")
                self._notify_error("無法解析播放清單頁面")
                return
            
            data = json.loads(match.group(1))
            items = data['props']['pageProps']['payload']['getVector']['items']
            
            tracks = []
            for item in items:
                if item.get('t') == 'yt' and item.get('f'):
                    tracks.append(TrackInfo(
                        title=item.get('tt', '未知歌曲'),
                        youtube_id=item['f'],
                        duration=item.get('tm', 0),
                    ))
            
            if not tracks:
                logger.warning("No tracks found in playlist")
                self._notify_error("播放清單為空")
                return
            
            with self._lock:
                self._playlist = tracks
                if self._shuffle:
                    random.shuffle(self._playlist)
                self._playlist_index = 0
                
            logger.info("Loaded %d tracks from mbplayer playlist", len(tracks))
            
        except Exception as ex:
            logger.error("Failed to load playlist: %s", ex)
            self._notify_error(f"載入播放清單失敗: {ex}")

    def _play_current(self):
        """播放目前歌曲"""
        if not self._playlist:
            return
            
        track = self._playlist[self._playlist_index % len(self._playlist)]
        
        try:
            import yt_dlp
            
            youtube_url = f"https://www.youtube.com/watch?v={track.youtube_id}"
            logger.info("Extracting audio for: %s (%s)", track.title, youtube_url)
            
            # 取得音訊串流 URL
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'format': 'bestaudio/best',
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                
            if not info:
                logger.warning("Failed to extract info for %s", track.title)
                self._next_and_play()
                return
                
            # 優先抓較小的可用音訊格式，降低下載等待時間
            audio_url = None
            ext = 'webm'
            formats = [f for f in info.get('formats', []) if f.get('vcodec') == 'none' and f.get('acodec') != 'none']
            if formats:
                preferred = [f for f in formats if f.get('ext') in ('m4a', 'mp3')]
                candidates = preferred or formats
                best = min(
                    candidates,
                    key=lambda f: (
                        float(f.get('filesize_approx') or f.get('filesize') or 1e18),
                        float(f.get('abr') or 1e9),
                    ),
                )
                audio_url = best.get('url')
                ext = best.get('ext', 'webm')

            if not audio_url:
                audio_url = info.get('url')
                ext = info.get('ext', 'webm')

            if not audio_url:
                logger.warning("No audio URL found for %s", track.title)
                self._next_and_play()
                return

            # 直接用 ffplay 串流播放，避免完整下載造成長延遲
            self._stop_process()
            volume = max(0, min(100, int(self._volume * 100)))
            cmd = [
                "ffplay",
                "-nodisp",
                "-autoexit",
                "-loglevel",
                "error",
                "-volume",
                str(volume),
                audio_url,
            ]
            creationflags = 0
            if os.name == "nt":
                creationflags = subprocess.CREATE_NO_WINDOW
            self._process = subprocess.Popen(
                cmd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creationflags,
            )
            
            with self._lock:
                self._is_playing = True
                self._is_paused = False
                self._current_track = track
                
            self._notify_track_change(track)
            logger.info("Playing: %s", track.title)
            
            # 監聽播放結束
            self._watch_playback()
            
        except Exception as ex:
            logger.error("Failed to play track: %s", ex)
            self._notify_error(f"播放失敗: {ex}")
            self._next_and_play()

    def _watch_playback(self):
        """背景執行緒監聽播放狀態"""
        def _watch():
            import time
            while self._is_playing and not self._is_paused:
                proc = self._process
                if proc is None:
                    return
                if proc.poll() is not None:
                    self._stop()
                    self._next_and_play()
                    return
                time.sleep(1)
        
        threading.Thread(target=_watch, daemon=True).start()

    def _pause(self):
        self._stop()
        logger.info("Stopped")

    def _resume(self):
        self.play()

    def _stop(self):
        self._stop_process()
        self._is_playing = False
        self._is_paused = False
        self._current_track = None
        self._notify_track_change(None)
        logger.info("Stopped")

    def _next_and_play(self):
        """自動播放下一首"""
        if self._playlist:
            self._playlist_index = (self._playlist_index + 1) % len(self._playlist)
            self._play_current()

    def _notify_track_change(self, track: TrackInfo | None):
        if self._on_track_change:
            try:
                self._on_track_change(track)
            except Exception:
                pass

    def _notify_error(self, msg: str):
        if self._on_error:
            try:
                self._on_error(msg)
            except Exception:
                pass

    def _stop_process(self):
        proc = self._process
        self._process = None
        if not proc:
            return
        try:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except Exception:
                    proc.kill()
        except Exception:
            pass
