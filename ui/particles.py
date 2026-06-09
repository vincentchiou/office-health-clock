# ui/particles.py — Particle system for water drops, sparkles, and effects

import tkinter as tk
import math
import random
import time
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
import config


# Named constants for particle physics
_SIZE_DECAY_RATE = 0.99  # per-frame decay at 60fps baseline
_SIZE_DECAY_BASE = 0.99 ** 60  # precomputed per-second decay


@dataclass
class _EmitConfig:
    """Configuration for a particle emission type."""
    speed_min: float
    speed_max: float
    size_min: float
    size_max: float
    colors: list
    lifetime_min: float
    lifetime_max: float
    gravity: float
    vy_offset: float = 0.0


_EMIT_CONFIGS = {
    "water_drop": _EmitConfig(
        speed_min=50, speed_max=150,
        size_min=3, size_max=6,
        colors=[config.COLOR_WATER, config.COLOR_WATER_HOVER],
        lifetime_min=0.5, lifetime_max=1.0,
        gravity=200, vy_offset=-50,
    ),
    "sparkle": _EmitConfig(
        speed_min=20, speed_max=80,
        size_min=1, size_max=3,
        colors=[config.COLOR_WATER_DONE, config.COLOR_MED_DONE],
        lifetime_min=0.3, lifetime_max=0.8,
        gravity=0,
    ),
    "confetti": _EmitConfig(
        speed_min=100, speed_max=300,
        size_min=4, size_max=8,
        colors=[config.COLOR_WATER_DONE, config.COLOR_MED_DONE, config.COLOR_TIMER, config.COLOR_WARN],
        lifetime_min=1.0, lifetime_max=2.0,
        gravity=300, vy_offset=-200,
    ),
}


@dataclass
class Particle:
    """Individual particle"""
    x: float
    y: float
    vx: float
    vy: float
    size: float
    color: str
    alpha: float
    lifetime: float
    max_lifetime: float
    gravity: float = 0.0

    def update(self, dt: float):
        """Update particle position and lifetime"""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.lifetime -= dt
        self.alpha = max(0.0, self.lifetime / self.max_lifetime)
        self.size *= _SIZE_DECAY_BASE ** dt


class ParticleSystem:
    """Particle system for visual effects"""

    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.particles: List[Particle] = []
        self.is_running = False
        self.animation_id = None

    def _emit(self, x: float, y: float, count: int, config_key: str):
        """Generic emit with a named configuration."""
        count = max(0, count)
        cfg = _EMIT_CONFIGS[config_key]
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(cfg.speed_min, cfg.speed_max)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed + cfg.vy_offset

            lifetime = random.uniform(cfg.lifetime_min, cfg.lifetime_max)
            self.particles.append(Particle(
                x=x, y=y,
                vx=vx, vy=vy,
                size=random.uniform(cfg.size_min, cfg.size_max),
                color=random.choice(cfg.colors),
                alpha=1.0,
                lifetime=lifetime,
                max_lifetime=lifetime,
                gravity=cfg.gravity,
            ))

        if not self.is_running:
            self.start_animation()

    def emit_water_drops(self, x: float, y: float, count: int = config.PARTICLE_WATER_DROP_COUNT):
        """Emit water drop particles"""
        self._emit(x, y, count, "water_drop")

    def emit_sparkles(self, x: float, y: float, count: int = config.PARTICLE_SPARKLE_COUNT):
        """Emit sparkle particles"""
        self._emit(x, y, count, "sparkle")

    def emit_confetti(self, x: float, y: float, count: int = 20):
        """Emit confetti particles for celebration"""
        self._emit(x, y, count, "confetti")

    def start_animation(self):
        """Start particle animation loop"""
        self.is_running = True
        self.last_time = time.time()
        self._animate()

    def _animate(self):
        """Animation loop"""
        if not self.is_running or not self.particles:
            self.is_running = False
            return

        current_time = time.time()
        dt = min(0.1, current_time - self.last_time)
        self.last_time = current_time

        for particle in self.particles:
            particle.update(dt)

        self.particles = [p for p in self.particles if p.lifetime > 0]

        self.canvas.delete("particles")
        for particle in self.particles:
            if particle.alpha > 0.1:
                self._draw_particle(particle)

        if self.particles:
            self.animation_id = self.canvas.after(16, self._animate)
        else:
            self.is_running = False

    def _draw_particle(self, particle: Particle):
        """Draw a single particle"""
        x, y = particle.x, particle.y
        size = particle.size

        self.canvas.create_oval(
            x - size, y - size, x + size, y + size,
            fill=particle.color,
            outline="",
            stipple="gray50" if particle.alpha < 1.0 else "",
            tags="particles"
        )

    def clear(self):
        """Clear all particles"""
        self.particles.clear()
        self.canvas.delete("particles")
        self.is_running = False
        if self.animation_id:
            self.canvas.after_cancel(self.animation_id)
            self.animation_id = None
