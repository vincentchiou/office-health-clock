# Game-Style UI Enhancement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the office health reminder application's UI with game-style visual effects, animations, and particle systems to create a more engaging and dynamic user experience.

**Architecture:** Implement a modular animation and particle system using Tkinter's Canvas capabilities. Create reusable animation components that can be applied to existing UI elements. Use game design principles for visual feedback, transitions, and effects.

**Tech Stack:** Python, Tkinter, Canvas-based rendering, custom animation engine, particle system.

---

## File Structure

### New Files
- `ui/animations.py` - Animation engine with easing functions, keyframe system, and transition effects
- `ui/particles.py` - Particle system for water drops, sparkles, and visual effects
- `ui/effects.py` - Visual effects like glow, shadow, and gradient effects

### Modified Files
- `ui/clock_window.py` - Enhanced indicators with animations
- `ui/reminder_window.py` - Animated dialogs with transitions
- `ui/water_panel.py` - Enhanced button interactions
- `config.py` - Animation and effect configuration parameters

---

## Task 1: Animation Engine Foundation

**Files:**
- Create: `ui/animations.py`
- Modify: `config.py:74-77` (add animation config)

- [ ] **Step 1: Create animation engine with easing functions**

```python
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
        return (--t) * t * t + 1
    
    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        if t < 0.5:
            return 4 * t * t * t
        return (t - 1) * (2 * t - 2) * (2 * t - 2) + 1
    
    @staticmethod
    def ease_out_bounce(t: float) -> float:
        if t < 1/2.75:
            return 7.5625 * t * t
        elif t < 2/2.75:
            t -= 1.5/2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5/2.75:
            t -= 2.25/2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625/2.75
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
```

- [ ] **Step 2: Add animation configuration to config.py**

```python
# Add to config.py after line 77 (ANIM_SLOW)

# Animation durations (seconds)
ANIM_DURATION_FAST = 0.1
ANIM_DURATION_NORMAL = 0.2
ANIM_DURATION_SLOW = 0.3
ANIM_DURATION_VERY_SLOW = 0.5

# Particle settings
PARTICLE_WATER_DROP_COUNT = 8
PARTICLE_SPARKLE_COUNT = 12
PARTICLE_LIFETIME = 1.0

# Glow effects
GLOW_INTENSITY = 0.3
GLOW_RADIUS = 10

# Bounce effects
BOUNCE_SCALE = 1.1
BOUNCE_DURATION = 0.2
```

- [ ] **Step 3: Verify animation engine works**

Run: `python -c "from ui.animations import AnimationManager; print('Animation engine loaded')"`
Expected: Output "Animation engine loaded"

---

## Task 2: Particle System

**Files:**
- Create: `ui/particles.py`

- [ ] **Step 1: Create particle system for visual effects**

```python
# ui/particles.py — Particle system for water drops, sparkles, and effects

import tkinter as tk
import math
import random
from typing import List, Tuple, Optional
from dataclasses import dataclass
import config


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
        self.size *= 0.99  # Slight shrink over time


class ParticleSystem:
    """Particle system for visual effects"""
    
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.particles: List[Particle] = []
        self.is_running = False
        self.animation_id = None
        
    def emit_water_drops(self, x: float, y: float, count: int = 8):
        """Emit water drop particles"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 50  # Upward bias
            
            particle = Particle(
                x=x, y=y,
                vx=vx, vy=vy,
                size=random.uniform(3, 6),
                color=random.choice([config.COLOR_WATER, config.COLOR_WATER_HOVER]),
                alpha=1.0,
                lifetime=random.uniform(0.5, 1.0),
                max_lifetime=1.0,
                gravity=200  # Gravity pulls down
            )
            self.particles.append(particle)
            
        if not self.is_running:
            self.start_animation()
            
    def emit_sparkles(self, x: float, y: float, count: int = 12):
        """Emit sparkle particles"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(20, 80)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            particle = Particle(
                x=x, y=y,
                vx=vx, vy=vy,
                size=random.uniform(1, 3),
                color=random.choice([config.COLOR_WATER_DONE, config.COLOR_MED_DONE]),
                alpha=1.0,
                lifetime=random.uniform(0.3, 0.8),
                max_lifetime=0.8,
                gravity=0
            )
            self.particles.append(particle)
            
        if not self.is_running:
            self.start_animation()
            
    def emit_confetti(self, x: float, y: float, count: int = 20):
        """Emit confetti particles for celebration"""
        colors = [config.COLOR_WATER_DONE, config.COLOR_MED_DONE, config.COLOR_TIMER, config.COLOR_WARN]
        
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(100, 300)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 200  # Upward bias
            
            particle = Particle(
                x=x, y=y,
                vx=vx, vy=vy,
                size=random.uniform(4, 8),
                color=random.choice(colors),
                alpha=1.0,
                lifetime=random.uniform(1.0, 2.0),
                max_lifetime=2.0,
                gravity=300
            )
            self.particles.append(particle)
            
        if not self.is_running:
            self.start_animation()
            
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
        dt = min(0.1, current_time - self.last_time)  # Cap delta time
        self.last_time = current_time
        
        # Update particles
        for particle in self.particles[:]:
            particle.update(dt)
            if particle.lifetime <= 0:
                self.particles.remove(particle)
                
        # Draw particles
        self.canvas.delete("particles")
        for particle in self.particles:
            if particle.alpha > 0.1:  # Only draw visible particles
                self._draw_particle(particle)
                
        # Continue animation
        if self.particles:
            self.animation_id = self.canvas.after(16, self._animate)  # ~60fps
        else:
            self.is_running = False
            
    def _draw_particle(self, particle: Particle):
        """Draw a single particle"""
        x, y = particle.x, particle.y
        size = particle.size
        
        # Create particle with glow effect
        self.canvas.create_oval(
            x - size, y - size, x + size, y + size,
            fill=particle.color,
            outline="",
            stipple="@" if particle.alpha < 1.0 else "",
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
```

- [ ] **Step 2: Verify particle system works**

Run: `python -c "from ui.particles import ParticleSystem; print('Particle system loaded')"`
Expected: Output "Particle system loaded"

---

## Task 3: Visual Effects Library

**Files:**
- Create: `ui/effects.py`

- [ ] **Step 1: Create visual effects library**

```python
# ui/effects.py — Visual effects like glow, shadow, and gradient effects

import tkinter as tk
import math
from typing import Tuple, Optional
import config


class GlowEffect:
    """Glow effect around elements"""
    
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        
    def draw_glow(self, x: float, y: float, radius: float, 
                  color: str, intensity: float = 0.3):
        """Draw a glow effect at position"""
        # Multiple concentric circles with decreasing opacity
        for i in range(3):
            r = radius + i * 2
            alpha = intensity * (1 - i / 3)
            self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill=color, outline="",
                stipple="@" if alpha < 1.0 else "",
                tags="glow"
            )
            
    def clear_glow(self):
        """Clear all glow effects"""
        self.canvas.delete("glow")


class ShadowEffect:
    """Shadow effect for elements"""
    
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        
    def draw_shadow(self, x: float, y: float, width: float, height: float,
                   offset: Tuple[float, float] = (3, 3), color: str = config.SHADOW_DARK):
        """Draw a shadow effect"""
        # Multiple shadow layers
        for i in range(3):
            ox = offset[0] + i
            oy = offset[1] + i
            self.canvas.create_rectangle(
                x + ox, y + oy, x + width + ox, y + height + oy,
                fill=color, outline="",
                stipple="@" if i < 2 else "",
                tags="shadow"
            )
            
    def clear_shadow(self):
        """Clear all shadow effects"""
        self.canvas.delete("shadow")


class GradientEffect:
    """Gradient background effects"""
    
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        
    def draw_radial_gradient(self, x: float, y: float, radius: float,
                           color_center: str, color_edge: str, steps: int = 10):
        """Draw a radial gradient"""
        for i in range(steps, 0, -1):
            r = radius * (i / steps)
            # Simple color interpolation
            color = self._lerp_color(color_center, color_edge, i / steps)
            self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill=color, outline="",
                tags="gradient"
            )
            
    def draw_linear_gradient(self, x1: float, y1: float, x2: float, y2: float,
                           color_start: str, color_end: str, steps: int = 10):
        """Draw a linear gradient"""
        dx = (x2 - x1) / steps
        dy = (y2 - y1) / steps
        
        for i in range(steps):
            t = i / steps
            color = self._lerp_color(color_start, color_end, t)
            x = x1 + dx * i
            y = y1 + dy * i
            self.canvas.create_rectangle(
                x, y, x + dx + 1, y + dy + 1,
                fill=color, outline="",
                tags="gradient"
            )
            
    def _lerp_color(self, color1: str, color2: str, t: float) -> str:
        """Linear interpolation between two hex colors"""
        # Convert hex to RGB
        r1, g1, b1 = self._hex_to_rgb(color1)
        r2, g2, b2 = self._hex_to_rgb(color2)
        
        # Interpolate
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        
        return f"#{r:02x}{g:02x}{b:02x}"
        
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
    def clear_gradient(self):
        """Clear all gradient effects"""
        self.canvas.delete("gradient")


class PulseEffect:
    """Pulsing effect for attention"""
    
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.pulse_id = None
        self.is_pulsing = False
        
    def start_pulse(self, x: float, y: float, radius: float, 
                   color: str, speed: float = 1.0):
        """Start pulsing effect"""
        self.is_pulsing = True
        self.pulse_data = {
            'x': x, 'y': y, 'radius': radius,
            'color': color, 'speed': speed, 'phase': 0
        }
        self._pulse_step()
        
    def _pulse_step(self):
        """Animate pulse"""
        if not self.is_pulsing:
            return
            
        data = self.pulse_data
        data['phase'] += 0.1 * data['speed']
        scale = 1.0 + 0.2 * math.sin(data['phase'])
        
        # Clear previous pulse
        self.canvas.delete("pulse")
        
        # Draw new pulse
        r = data['radius'] * scale
        self.canvas.create_oval(
            data['x'] - r, data['y'] - r,
            data['x'] + r, data['y'] + r,
            outline=data['color'], width=2,
            tags="pulse"
        )
        
        # Schedule next frame
        self.pulse_id = self.canvas.after(50, self._pulse_step)
        
    def stop_pulse(self):
        """Stop pulsing effect"""
        self.is_pulsing = False
        if self.pulse_id:
            self.canvas.after_cancel(self.pulse_id)
            self.pulse_id = None
        self.canvas.delete("pulse")
```

- [ ] **Step 2: Verify effects library works**

Run: `python -c "from ui.effects import GlowEffect, PulseEffect; print('Effects library loaded')"`
Expected: Output "Effects library loaded"

---

## Task 4: Enhanced Clock Window Indicators

**Files:**
- Modify: `ui/clock_window.py:11-66` (CircleIndicator class)
- Modify: `ui/clock_window.py:68-132` (GaugeIndicator class)

- [ ] **Step 1: Enhance CircleIndicator with animations**

Replace the CircleIndicator class in ui/clock_window.py:

```python
class CircleIndicator:
    """Enhanced circular progress indicator with animations"""
    
    def __init__(self, parent, size=80, color=config.COLOR_WATER, bg_color=config.SYS_BAR_BG):
        self.size = size
        self.color = color
        self.bg_color = bg_color
        self.canvas = tk.Canvas(parent, width=size, height=size, 
                               bg=config.BG_COLOR, highlightthickness=0, bd=0)
        self.progress = 0
        self.target_progress = 0
        self.animation_id = None
        self.pulse_effect = None
        
    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)
        
    def update(self, progress, text="", sub_text=""):
        """Update with smooth animation"""
        self.target_progress = min(1.0, max(0.0, progress))
        
        # Start animation if not already running
        if self.animation_id is None:
            self._animate_progress()
            
    def _animate_progress(self):
        """Animate progress change"""
        diff = self.target_progress - self.progress
        
        if abs(diff) < 0.01:
            self.progress = self.target_progress
            self._draw()
            return
            
        # Smooth interpolation
        self.progress += diff * 0.1
        self._draw()
        self.animation_id = self.canvas.after(16, self._animate_progress)
        
    def _draw(self):
        """Draw the indicator"""
        self.canvas.delete("all")
        
        cx, cy = self.size // 2, self.size // 2
        radius = self.size // 2 - 8
        
        # Draw background arc
        self._draw_arc(cx, cy, radius, 1.0, self.bg_color, width=8)
        
        # Draw progress arc with glow effect
        if self.progress > 0:
            # Draw glow
            for i in range(3):
                r = radius + i * 2
                alpha = 0.3 * (1 - i / 3)
                self._draw_arc(cx, cy, r, self.progress, self.color, width=2)
                
            # Draw main arc
            self._draw_arc(cx, cy, radius, self.progress, self.color, width=8)
        
        # Draw center text
        text = f"{int(self.progress * 100)}%"
        self.canvas.create_text(cx, cy - 5, text=text, 
                               font=config.FONT_CIRCLE, fill=config.TEXT_PRIMARY)
        
    def _draw_arc(self, cx, cy, radius, progress, color, width=8):
        """Draw an arc"""
        start_angle = 90  # Start from top
        extent = 360 * progress
        
        # Use multiple line segments to simulate arc
        points = []
        steps = max(2, int(36 * progress))
        for i in range(steps + 1):
            angle = math.radians(start_angle - (extent * i / steps))
            x = cx + radius * math.cos(angle)
            y = cy - radius * math.sin(angle)
            points.append((x, y))
        
        # Draw line segments
        for i in range(len(points) - 1):
            self.canvas.create_line(points[i], points[i+1], 
                                   fill=color, width=width, capstyle=tk.ROUND)
```

- [ ] **Step 2: Enhance GaugeIndicator with needle animation**

Replace the GaugeIndicator class in ui/clock_window.py:

```python
class GaugeIndicator:
    """Enhanced gauge indicator with animated needle"""
    
    def __init__(self, parent, size=100, color=config.COLOR_TIMER):
        self.size = size
        self.color = color
        self.canvas = tk.Canvas(parent, width=size, height=size,
                               bg=config.BG_COLOR, highlightthickness=0, bd=0)
        self.progress = 0
        self.target_progress = 0
        self.current_needle_angle = 180  # Start position
        self.animation_id = None
        
    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)
        
    def update(self, progress, text="", color=None):
        """Update with smooth needle animation"""
        if color is None:
            color = self.color
            
        self.target_progress = min(1.0, max(0.0, progress))
        self.color = color
        
        # Start animation if not already running
        if self.animation_id is None:
            self._animate_gauge()
            
    def _animate_gauge(self):
        """Animate gauge needle"""
        diff = self.target_progress - self.progress
        
        if abs(diff) < 0.01:
            self.progress = self.target_progress
            self._draw()
            return
            
        # Smooth interpolation
        self.progress += diff * 0.1
        self._draw()
        self.animation_id = self.canvas.after(16, self._animate_gauge)
        
    def _draw(self):
        """Draw the gauge"""
        self.canvas.delete("all")
        
        cx, cy = self.size // 2, self.size // 2 + 10
        radius = self.size // 2 - 15
        
        # Draw background arc (semicircle)
        self._draw_semicircle(cx, cy, radius, 1.0, config.SYS_BAR_BG, width=10)
        
        # Draw progress arc with glow
        if self.progress > 0:
            # Glow effect
            for i in range(2):
                r = radius + i * 3
                self._draw_semicircle(cx, cy, r, self.progress, self.color, width=2)
                
            # Main arc
            self._draw_semicircle(cx, cy, radius, self.progress, self.color, width=10)
        
        # Draw needle with smooth rotation
        target_angle = 180 + 180 * self.progress
        self.current_needle_angle += (target_angle - self.current_needle_angle) * 0.1
        self._draw_needle(cx, cy, radius - 15, self.current_needle_angle, self.color)
        
        # Draw center text
        text = f"{int(self.progress * 100)}%"
        self.canvas.create_text(cx, cy - 10, text=text,
                               font=config.FONT_CIRCLE, fill=config.TEXT_PRIMARY)
        
    def _draw_semicircle(self, cx, cy, radius, progress, color, width=10):
        """Draw a semicircle"""
        start_angle = 180
        extent = 180 * progress
        
        points = []
        steps = max(2, int(36 * progress))
        for i in range(steps + 1):
            angle = math.radians(start_angle + (extent * i / steps))
            x = cx + radius * math.cos(angle)
            y = cy - radius * math.sin(angle)
            points.append((x, y))
        
        for i in range(len(points) - 1):
            self.canvas.create_line(points[i], points[i+1],
                                   fill=color, width=width, capstyle=tk.ROUND)
    
    def _draw_needle(self, cx, cy, length, angle_degrees, color):
        """Draw the needle"""
        angle = math.radians(angle_degrees)
        x = cx + length * math.cos(angle)
        y = cy - length * math.sin(angle)
        
        # Needle root
        self.canvas.create_oval(cx-4, cy-4, cx+4, cy+4, 
                               fill=color, outline="")
        # Needle line
        self.canvas.create_line(cx, cy, x, y, fill=color, width=3, capstyle=tk.ROUND)
```

- [ ] **Step 3: Test enhanced indicators**

Run: `python -c "from ui.clock_window import CircleIndicator, GaugeIndicator; print('Enhanced indicators loaded')"`
Expected: Output "Enhanced indicators loaded"

---

## Task 5: Enhanced Reminder Window Animations

**Files:**
- Modify: `ui/reminder_window.py:16-49` (AnimatedIcon class)
- Modify: `ui/reminder_window.py:86-347` (ReminderWindow class)

- [ ] **Step 1: Enhance AnimatedIcon with particle effects**

Replace the AnimatedIcon class in ui/reminder_window.py:

```python
class AnimatedIcon:
    """Enhanced animated icon with particle effects"""
    
    def __init__(self, parent, icon, size=80, color=config.BTN_PRIMARY):
        self.icon = icon
        self.size = size
        self.color = color
        self.canvas = tk.Canvas(parent, width=size, height=size,
                               bg=config.BG_COLOR, highlightthickness=0, bd=0)
        self.frame = 0
        self.pulse_phase = 0
        self.glow_phase = 0
        self.animation_id = None
        
    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)
        
    def start_animation(self):
        """Start continuous animation"""
        self.animation_id = self.canvas.after(50, self._animate)
        
    def _animate(self):
        """Animate the icon"""
        self.frame += 1
        self.pulse_phase += 0.1
        self.glow_phase += 0.05
        
        self.draw()
        self.animation_id = self.canvas.after(50, self._animate)
        
    def draw(self):
        """Draw the animated icon"""
        self.canvas.delete("all")
        cx, cy = self.size // 2, self.size // 2
        
        # Pulsing glow effect
        pulse_scale = 1.0 + 0.1 * math.sin(self.pulse_phase)
        
        # Draw multiple glow layers
        for i in range(4):
            r = 35 + i * 3 * pulse_scale
            alpha = 0.4 * (1 - i / 4)
            self.canvas.create_oval(cx - r, cy - r, 
                                   cx + r, cy + r,
                                   fill="", outline=self.color, width=1)
        
        # Main circle with dynamic border
        border_width = 3 + int(2 * math.sin(self.glow_phase))
        self.canvas.create_oval(cx - 32, cy - 32, cx + 32, cy + 32,
                               fill=config.BG_ELEVATED, outline=self.color, width=border_width)
        
        # Icon text with shadow effect
        self.canvas.create_text(cx + 1, cy + 1, text=self.icon,
                               font=("Segoe UI", 32), fill=config.SHADOW_DARK)
        self.canvas.create_text(cx, cy, text=self.icon,
                               font=("Segoe UI", 32), fill=self.color)
        
    def stop_animation(self):
        """Stop animation"""
        if self.animation_id:
            self.canvas.after_cancel(self.animation_id)
            self.animation_id = None
```

- [ ] **Step 2: Add entrance animation to ReminderWindow**

Add animation methods to the ReminderWindow class:

```python
# Add these methods to the ReminderWindow class

def _animate_dialog_entrance(self, dialog):
    """Animate dialog entrance with scale and fade"""
    # Start small and scale up
    dialog.scale = 0.1
    dialog.alpha = 0.0
    
    def animate_step():
        dialog.scale += 0.05
        dialog.alpha += 0.05
        
        if dialog.scale >= 1.0:
            dialog.scale = 1.0
            dialog.alpha = 1.0
            return
            
        # Apply scale effect (simulated with geometry)
        width = int(440 * dialog.scale)
        height = int(380 * dialog.scale)
        x = (dialog.winfo_screenwidth() - width) // 2
        y = (dialog.winfo_screenheight() - height) // 2
        
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.attributes("-alpha", dialog.alpha)
        
        dialog.after(16, animate_step)
        
    animate_step()

def _animate_dialog_exit(self, dialog, overlay, callback=None):
    """Animate dialog exit"""
    def animate_step():
        dialog.scale -= 0.1
        dialog.alpha -= 0.1
        
        if dialog.scale <= 0.0:
            dialog.destroy()
            overlay.destroy()
            if callback:
                callback()
            return
            
        # Apply exit effect
        width = int(440 * dialog.scale)
        height = int(380 * dialog.scale)
        x = (dialog.winfo_screenwidth() - width) // 2
        y = (dialog.winfo_screenheight() - height) // 2
        
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.attributes("-alpha", dialog.alpha)
        
        dialog.after(16, animate_step)
        
    animate_step()
```

- [ ] **Step 3: Test enhanced reminder window**

Run: `python -c "from ui.reminder_window import AnimatedIcon; print('Enhanced reminder window loaded')"`
Expected: Output "Enhanced reminder window loaded"

---

## Task 6: Enhanced Water Panel Buttons

**Files:**
- Modify: `ui/water_panel.py:7-53` (WaterPanel class)

- [ ] **Step 1: Enhance buttons with hover animations**

Replace the WaterPanel class in ui/water_panel.py:

```python
class WaterPanel(tk.Frame):
    """
    Enhanced water panel with animated buttons and visual feedback
    """
    
    def __init__(self, parent, on_drink, **kwargs):
        super().__init__(parent, bg=config.BG_COLOR, **kwargs)
        self._on_drink = on_drink
        self._buttons = []
        self._build()
        
    def _build(self):
        for i, ml in enumerate(config.WATER_QUICK_AMOUNTS):
            btn_frame = tk.Frame(self, bg=config.BG_COLOR)
            btn_frame.pack(side="left", padx=3, pady=2)
            
            btn = tk.Button(
                btn_frame,
                text=f"+{ml}ml",
                font=config.FONT_BTN,
                bg=config.BTN_BG,
                fg=config.COLOR_WATER,
                activebackground=config.BTN_HOVER,
                activeforeground=config.COLOR_WATER_DONE,
                relief="flat",
                padx=8, pady=4,
                cursor="hand2",
                command=lambda m=ml: self._on_drink_with_effect(m, btn),
            )
            btn.pack()
            
            # Store button reference
            self._buttons.append((btn, ml))
            
            # Enhanced hover effects with animation
            self._setup_button_effects(btn, ml)
            
    def _setup_button_effects(self, btn, ml):
        """Setup enhanced button effects"""
        original_bg = config.BTN_BG
        original_fg = config.COLOR_WATER
        hover_bg = config.BG_TERTIARY
        hover_fg = config.COLOR_WATER_HOVER
        press_bg = config.BORDER_COLOR
        press_fg = config.COLOR_WATER_DONE
        
        # Hover animation variables
        btn.hover_scale = 1.0
        btn.is_hovered = False
        btn.is_pressed = False
        
        def on_enter(e):
            btn.is_hovered = True
            self._animate_button_hover(btn, True, hover_bg, hover_fg)
            
        def on_leave(e):
            btn.is_hovered = False
            if not btn.is_pressed:
                self._animate_button_hover(btn, False, original_bg, original_fg)
            
        def on_press(e):
            btn.is_pressed = True
            btn.config(bg=press_bg, fg=press_fg)
            
        def on_release(e):
            btn.is_pressed = False
            if btn.is_hovered:
                btn.config(bg=hover_bg, fg=hover_fg)
            else:
                btn.config(bg=original_bg, fg=original_fg)
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<ButtonPress-1>", on_press)
        btn.bind("<ButtonRelease-1>", on_release)
        
    def _animate_button_hover(self, btn, is_enter, target_bg, target_fg):
        """Animate button hover effect"""
        current_bg = btn.cget("bg")
        current_fg = btn.cget("fg")
        
        # Simple color transition
        btn.config(bg=target_bg, fg=target_fg)
        
    def _on_drink_with_effect(self, ml, btn):
        """Handle drink with visual effect"""
        # Flash effect
        original_bg = btn.cget("bg")
        btn.config(bg=config.COLOR_WATER_DONE)
        btn.after(100, lambda: btn.config(bg=original_bg))
        
        # Call the drink callback
        self._on_drink(ml)
```

- [ ] **Step 2: Test enhanced water panel**

Run: `python -c "from ui.water_panel import WaterPanel; print('Enhanced water panel loaded')"`
Expected: Output "Enhanced water panel loaded"

---

## Task 7: Integration and Testing

**Files:**
- Modify: `ui/clock_window.py:135-529` (ClockWindow class)
- Modify: `ui/reminder_window.py:86-347` (ReminderWindow class)

- [ ] **Step 1: Add particle effects to ClockWindow**

Add particle system integration to ClockWindow class:

```python
# Add to ClockWindow.__init__ method
self._particle_system = None
self._setup_particles()

# Add new method to ClockWindow class
def _setup_particles(self):
    """Setup particle system for visual effects"""
    try:
        from ui.particles import ParticleSystem
        # Create a canvas for particles (we'll use the main canvas)
        self._particle_canvas = tk.Canvas(self._main, bg=config.BG_COLOR, 
                                         highlightthickness=0, bd=0)
        self._particle_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._particle_system = ParticleSystem(self._particle_canvas)
    except ImportError:
        self._particle_system = None

def _celebrate_water_goal(self):
    """Celebrate reaching water goal with confetti"""
    if self._particle_system:
        # Get center position
        x = config.WINDOW_WIDTH // 2
        y = config.WINDOW_HEIGHT // 2
        self._particle_system.emit_confetti(x, y, 30)
```

- [ ] **Step 2: Add animation triggers to ReminderWindow**

Modify the show methods to trigger animations:

```python
# Modify show_water method in ReminderWindow class
def show_water(self, total_ml: int, target_ml: int, on_drink=None, on_skip=None):
    _play_alert()
    remaining = max(0, target_ml - total_ml)
    pct = min(1.0, total_ml / target_ml) if target_ml else 0

    def _drink(ml):
        if on_drink:
            on_drink(ml)

    def _skip():
        if on_skip:
            on_skip()

    self._show(
        title="記得喝水！",
        icon="💧",
        icon_color=config.COLOR_WATER,
        lines=[
            f"今日：{total_ml} / {target_ml} ml",
            f"還差 {remaining} ml 達標",
        ],
        buttons=[
            ("+200 ml", lambda: _drink(200)),
            ("+350 ml", lambda: _drink(350)),
            ("+500 ml", lambda: _drink(500)),
        ],
        skip_text="跳過，稍後提醒",
        on_close=_skip,
        accent_color=config.COLOR_WATER,
        progress=pct,
        progress_text=f"{int(pct*100)}%",
    )
```

- [ ] **Step 3: Test complete integration**

Run: `python -c "import ui.clock_window; import ui.reminder_window; import ui.water_panel; print('All UI modules loaded successfully')"`
Expected: Output "All UI modules loaded successfully"

---

## Task 8: Final Testing and Optimization

**Files:**
- Create: `test_ui_enhancements.py`

- [ ] **Step 1: Create test script for UI enhancements**

```python
# test_ui_enhancements.py — Test UI enhancements

import tkinter as tk
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_animation_engine():
    """Test animation engine"""
    from ui.animations import AnimationManager, Animation
    
    manager = AnimationManager()
    anim = manager.create_animation("test", 1.0, "ease_in_out_quad")
    
    print("✓ Animation engine works")
    return True

def test_particle_system():
    """Test particle system"""
    from ui.particles import ParticleSystem
    
    root = tk.Tk()
    root.withdraw()
    canvas = tk.Canvas(root, width=100, height=100)
    
    ps = ParticleSystem(canvas)
    ps.emit_water_drops(50, 50, 5)
    
    root.destroy()
    print("✓ Particle system works")
    return True

def test_effects():
    """Test visual effects"""
    from ui.effects import GlowEffect, ShadowEffect, GradientEffect
    
    root = tk.Tk()
    root.withdraw()
    canvas = tk.Canvas(root, width=100, height=100)
    
    glow = GlowEffect(canvas)
    shadow = ShadowEffect(canvas)
    gradient = GradientEffect(canvas)
    
    root.destroy()
    print("✓ Visual effects work")
    return True

def test_ui_imports():
    """Test all UI module imports"""
    from ui.clock_window import ClockWindow, CircleIndicator, GaugeIndicator
    from ui.reminder_window import ReminderWindow, AnimatedIcon
    from ui.water_panel import WaterPanel
    
    print("✓ All UI modules import correctly")
    return True

if __name__ == "__main__":
    print("Testing UI enhancements...")
    print()
    
    tests = [
        test_animation_engine,
        test_particle_system,
        test_effects,
        test_ui_imports,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
    
    print()
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("All tests passed! ✓")
    else:
        print("Some tests failed! ✗")
        sys.exit(1)
```

- [ ] **Step 2: Run test script**

Run: `python test_ui_enhancements.py`
Expected: All tests pass with "All tests passed! ✓"

- [ ] **Step 3: Performance optimization check**

Run: `python -c "import time; start=time.time(); from ui.clock_window import ClockWindow; from ui.reminder_window import ReminderWindow; from ui.water_panel import WaterPanel; end=time.time(); print(f'Import time: {end-start:.3f}s')"`
Expected: Import time under 0.5 seconds

---

## Summary

This plan enhances the office health reminder application with game-style visual effects:

1. **Animation Engine** - Smooth easing functions and keyframe animations
2. **Particle System** - Water drops, sparkles, and confetti effects
3. **Visual Effects** - Glow, shadow, and gradient effects
4. **Enhanced Indicators** - Animated progress circles and gauges
5. **Animated Dialogs** - Entrance/exit animations for reminder windows
6. **Button Interactions** - Enhanced hover and press effects
7. **Integration** - Complete system with particle effects and animations

The enhancements maintain the application's functionality while adding engaging visual feedback that makes the health reminders more attention-grabbing and enjoyable to use.