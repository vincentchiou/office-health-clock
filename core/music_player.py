# core/music_player.py — 音樂播放模組（mbplayer 華語熱門排行榜）

from __future__ import annotations

import logging
import random
import threading
from dataclasses import dataclass
from typing import Callable

logger = logging.getLogger(__name__)

# 華語本週熱門排行榜 mbplayer 清單頁面
PLAYLIST_URL = "https://www.mbplayer.com/list/10086761"


@dataclass
class TrackInfo:
    """單曲資訊"""
    title: str
    url: str
    duration: int = 0  # seconds


class MusicPlayer:
    """
    音樂播放器：從 mbplayer 華語熱門排行榜抓取 YouTube 音訊串流並播放。
    
    依賴：
    - yt-dlp：提取 YouTube 音訊 URL
    - pygame：播放音訊
    """

    def __init__(self):
        self._is_playing = False
        self._is_paused = False
        self._current_track: TrackInfo | None = None
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
        """延遲初始化 pygame mixer（避免阻塞主程式啟動）"""
        if self._initialized:
            return True
        try:
            import pygame
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            self._initialized = True
            logger.info("Pygame mixer initialized")
            return True
        except Exception as ex:
            logger.error("Failed to init pygame mixer: %s", ex)
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
        if self._initialized:
            try:
                import pygame
                pygame.mixer.music.set_volume(self._volume)
            except Exception:
                pass

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
        if self._initialized:
            try:
                import pygame
                pygame.mixer.quit()
            except Exception:
                pass

    # ── 內部方法 ──────────────────────────────────────────

    def _load_playlist(self):
        """從 mbplayer 載入播放清單"""
        try:
            import yt_dlp
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,  # 只取得清單，不下載
                'playlistend': 30,     # 最多 30 首
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(PLAYLIST_URL, download=False)
                
            if not info or 'entries' not in info:
                logger.warning("No playlist entries found")
                return
                
            tracks = []
            for entry in info['entries']:
                if entry and entry.get('url'):
                    tracks.append(TrackInfo(
                        title=entry.get('title', '未知歌曲'),
                        url=entry['url'],
                        duration=entry.get('duration', 0),
                    ))
            
            with self._lock:
                self._playlist = tracks
                if self._shuffle:
                    random.shuffle(self._playlist)
                self._playlist_index = 0
                
            logger.info("Loaded %d tracks from playlist", len(tracks))
            
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
            import pygame
            
            # 取得音訊串流 URL
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'format': 'bestaudio/best',
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(track.url, download=False)
                
            if not info:
                logger.warning("Failed to extract info for %s", track.title)
                self._next_and_play()
                return
                
            # 取得最佳音訊格式
            audio_url = info.get('url')
            if not audio_url:
                # 嘗試從 formats 中找音訊
                formats = info.get('formats', [])
                audio_formats = [f for f in formats if f.get('acodec') != 'none']
                if audio_formats:
                    best = max(audio_formats, key=lambda f: f.get('abr', 0))
                    audio_url = best.get('url')
            
            if not audio_url:
                logger.warning("No audio URL found for %s", track.title)
                self._next_and_play()
                return
                
            # 播放音訊
            pygame.mixer.music.load(audio_url)
            pygame.mixer.music.set_volume(self._volume)
            pygame.mixer.music.play()
            
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
                try:
                    import pygame
                    if not pygame.mixer.music.get_busy():
                        # 播放結束，自動下一首
                        self._next_and_play()
                        return
                except Exception:
                    pass
                time.sleep(1)
        
        threading.Thread(target=_watch, daemon=True).start()

    def _pause(self):
        try:
            import pygame
            pygame.mixer.music.pause()
            self._is_paused = True
            logger.info("Paused")
        except Exception as ex:
            logger.error("Failed to pause: %s", ex)

    def _resume(self):
        try:
            import pygame
            pygame.mixer.music.unpause()
            self._is_paused = False
            logger.info("Resumed")
        except Exception as ex:
            logger.error("Failed to resume: %s", ex)

    def _stop(self):
        try:
            if self._initialized:
                import pygame
                pygame.mixer.music.stop()
            self._is_playing = False
            self._is_paused = False
            self._current_track = None
            self._notify_track_change(None)
            logger.info("Stopped")
        except Exception as ex:
            logger.error("Failed to stop: %s", ex)

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
