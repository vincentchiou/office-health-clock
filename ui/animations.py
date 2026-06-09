# ui/animations.py — Animation engine with easing functions and keyframe system

import time
import math
from typing import Callable, Dict, List, Optional, Tuple, Any


class EasingFunctions:
    """Collection of easing functions for smooth animations"""

    @staticmethod
    def linear(t: float) -> float:
        return t

    @staticmethod
    def ease_in_quad(t: float) -> float:
        return t * t

    @staticmethod
    def ease_out_quad(t: float) -> float:
        return t * (2 - t)

    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        if t < 0.5:
            return 2 * t * t
        return -1 + (4 - 2 * t) * t

    @staticmethod
    def ease_in_cubic(t: float) -> float:
        return t * t * t

    @staticmethod
    def ease_out_cubic(t: float) -> float:
        t -= 1
        return t * t * t + 1

    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        if t < 0.5:
            return 4 * t * t * t
        return (t - 1) * (2 * t - 2) * (2 * t - 2) + 1

    @staticmethod
    def ease_out_bounce(t: float) -> float:
        if t < 1 / 2.75:
            return 7.5625 * t * t
        elif t < 2 / 2.75:
            t -= 1.5 / 2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5 / 2.75:
            t -= 2.25 / 2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625 / 2.75
            return 7.5625 * t * t + 0.984375

    @staticmethod
    def ease_out_elastic(t: float) -> float:
        if t == 0 or t == 1:
            return t
        return math.pow(2, -10 * t) * math.sin((t - 0.1) * 5 * math.pi) + 1


class Animation:
    """Base animation class"""

    def __init__(self, duration: float = 1.0, easing: str = "linear"):
        self.duration = duration
        self.easing = getattr(EasingFunctions, easing, EasingFunctions.linear)
        self.start_time = None
        self.is_playing = False
        self.is_reverse = False
        self.loop = False
        self.on_complete = None

    def start(self, reverse: bool = False):
        self.start_time = time.time()
        self.is_playing = True
        self.is_reverse = reverse

    def stop(self):
        self.is_playing = False
        self.start_time = None

    def update(self) -> Tuple[bool, float]:
        """Returns (is_active, progress 0-1)"""
        if not self.is_playing or self.start_time is None:
            return False, 0.0

        elapsed = time.time() - self.start_time
        progress = min(1.0, elapsed / self.duration)

        if self.is_reverse:
            progress = 1.0 - progress

        if progress >= 1.0:
            if self.loop:
                self.start_time = time.time()
                return True, 0.0
            else:
                self.is_playing = False
                if self.on_complete:
                    self.on_complete()
                return False, 1.0

        return True, self.easing(progress)


class AnimationManager:
    """Manages multiple animations"""

    def __init__(self):
        self.animations: Dict[str, Animation] = {}
        self.update_callback: Optional[Callable] = None

    def create_animation(self, name: str, duration: float = 1.0,
                         easing: str = "linear") -> Animation:
        anim = Animation(duration, easing)
        self.animations[name] = anim
        return anim

    def get_animation(self, name: str) -> Optional[Animation]:
        return self.animations.get(name)

    def update(self):
        """Update all animations"""
        for name, anim in list(self.animations.items()):
            if anim.is_playing:
                is_active, progress = anim.update()
                if self.update_callback:
                    self.update_callback(name, progress)
                if not is_active:
                    del self.animations[name]

    def has_playing(self) -> bool:
        return any(anim.is_playing for anim in self.animations.values())


class KeyframeAnimation:
    """Keyframe-based animation for complex sequences"""

    def __init__(self, duration: float):
        self.duration = duration
        self.keyframes: List[Tuple[float, Dict[str, Any]]] = []
        self.current_time = 0.0
        self.is_playing = False
        self.on_update = None

    def add_keyframe(self, time_pct: float, properties: Dict[str, Any]):
        """Add keyframe at time percentage (0-1) with properties"""
        self.keyframes.append((time_pct, properties))
        self.keyframes.sort(key=lambda x: x[0])

    def start(self):
        self.current_time = 0.0
        self.is_playing = True

    def update(self, dt: float) -> bool:
        """Update animation, returns False when complete"""
        if not self.is_playing:
            return False

        self.current_time += dt
        if self.current_time >= self.duration:
            self.is_playing = False
            return False

        # Interpolate between keyframes
        progress = self.current_time / self.duration
        properties = self._interpolate(progress)

        if self.on_update:
            self.on_update(properties)

        return True

    def _interpolate(self, progress: float) -> Dict[str, Any]:
        """Interpolate between keyframes"""
        if not self.keyframes:
            return {}

        # Find surrounding keyframes
        prev_kf = self.keyframes[0]
        next_kf = self.keyframes[-1]

        for i, (time_pct, props) in enumerate(self.keyframes):
            if time_pct <= progress:
                prev_kf = (time_pct, props)
                if i + 1 < len(self.keyframes):
                    next_kf = self.keyframes[i + 1]
                else:
                    next_kf = (time_pct, props)

        # Calculate interpolation factor
        if prev_kf[0] == next_kf[0]:
            t = 0.0
        else:
            t = (progress - prev_kf[0]) / (next_kf[0] - prev_kf[0])

        # Interpolate properties
        result = {}
        prev_props = prev_kf[1]
        next_props = next_kf[1]

        for key in set(list(prev_props.keys()) + list(next_props.keys())):
            if key in prev_props and key in next_props:
                if isinstance(prev_props[key], (int, float)):
                    result[key] = prev_props[key] + (next_props[key] - prev_props[key]) * t
                else:
                    result[key] = prev_props[key] if t < 0.5 else next_props[key]
            elif key in prev_props:
                result[key] = prev_props[key]
            else:
                result[key] = next_props[key]

        return result
