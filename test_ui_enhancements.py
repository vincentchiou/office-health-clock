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

    print("[OK] Animation engine works")
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
    print("[OK] Particle system works")
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
    print("[OK] Visual effects work")
    return True

def test_ui_imports():
    """Test all UI module imports"""
    from ui.clock_window import ClockWindow, CircleIndicator, GaugeIndicator, SystemMetricCard
    from ui.reminder_window import ReminderWindow, AnimatedIcon
    from ui.water_panel import WaterPanel
    from core.weather_service import WeatherService

    icon, desc = WeatherService._weather_code_to_icon(0)
    assert icon == "☀"
    assert desc == "晴朗"

    print("[OK] All UI modules import correctly")
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
            print(f"[FAIL] {test.__name__} failed: {e}")
            failed += 1

    print()
    print(f"Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("All tests passed! [OK]")
    else:
        print("Some tests failed! [FAIL]")
        sys.exit(1)
