# ui/effects.py — Visual effects like glow, shadow, and gradient effects

import tkinter as tk
import math
from typing import Tuple
import config
from ui.utils import hex_to_rgb, lerp_color


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
            self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill=color, outline="",
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
        return lerp_color(color1, color2, t)
        
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
