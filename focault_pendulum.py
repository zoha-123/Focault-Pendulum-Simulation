"""
Foucault Pendulum Simulator - Enhanced Interactive Version
==========================================================
An educational simulation demonstrating how Foucault pendulum
reveals Earth's rotation through precession of its oscillation plane.

Author: Zoha Imran (with AI Assistance)

License: MIT
"""

import pygame
import numpy as np
import math
import sys
from dataclasses import dataclass
from typing import Tuple, List, Optional
from enum import Enum


class LocationPreset(Enum):
    """Predefined latitude locations"""
    EQUATOR = 0
    MID_LAT = 45
    NORTH_POLE = 90


@dataclass
class Colors:
    """Modern color palette with high contrast"""
    BG_DARK = (15, 23, 42)
    BG_MEDIUM = (30, 41, 59)
    BG_LIGHT = (51, 65, 85)
    PANEL_BG = (30, 41, 59, 245)
    
    PRIMARY = (59, 130, 246)
    PRIMARY_HOVER = (96, 165, 250)
    SECONDARY = (168, 85, 247)
    ACCENT = (234, 179, 8)
    SUCCESS = (34, 197, 94)
    DANGER = (239, 68, 68)
    
    TEXT_PRIMARY = (248, 250, 252)
    TEXT_SECONDARY = (203, 213, 225)
    TEXT_MUTED = (148, 163, 184)
    BORDER = (71, 85, 105)
    
    PENDULUM = (239, 68, 68)
    TRAIL_START = (59, 130, 246)
    TRAIL_END = (168, 85, 247)
    FLOOR = (51, 65, 85)
    COMPASS = (148, 163, 184)
    INERTIAL_REF = (234, 179, 8)


class PhysicsEngine:
    """Handles all physics calculations for the Foucault pendulum"""
    
    def __init__(self, length: float = 10.0):
        self.g = 9.81
        self.L = length
        self.omega_e = 7.2921e-5
        self.omega_0 = np.sqrt(self.g / self.L)
        
    def calculate_inertial_position(self, time: float, amplitude: float, fixed_mode: bool = False) -> Tuple[float, float]:
        if fixed_mode:
            # In fixed mode, pendulum stays at a fixed position in inertial frame
            return amplitude, 0  # Fixed position
        else:
            # Normal oscillating pendulum
            x = amplitude * np.cos(self.omega_0 * time)
            y = amplitude * 0.3 * np.sin(self.omega_0 * time)
            return x, y
    
    def rotate_to_earth_frame(self, x: float, y: float, time: float, 
                              latitude: float, speed_factor: float) -> Tuple[float, float, float]:
        omega_p = self.omega_e * np.sin(np.radians(latitude))
        theta = omega_p * time * speed_factor
        
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)
        
        x_earth = x * cos_theta - y * sin_theta
        y_earth = x * sin_theta + y * cos_theta
        
        return x_earth, y_earth, theta
    
    def get_precession_period(self, latitude: float) -> float:
        sin_lat = np.sin(np.radians(latitude))
        if abs(sin_lat) < 0.01:
            return float('inf')
        return 24.0 / abs(sin_lat)
    
    def get_location_info(self, latitude: float, fixed_mode: bool = False) -> dict:
        """Get dynamic info based on current latitude and mode"""
        if fixed_mode:
            return {
                "name": "FIXED PENDULUM",
                "color": (168, 85, 247),
                "description": "Earth rotates beneath pendulum",
                "explanation": "Pendulum stays fixed while Earth rotates",
                "period": "N/A"
            }
        elif abs(latitude) < 5:
            return {
                "name": "EQUATOR",
                "color": (239, 68, 68),
                "description": "No visible rotation",
                "explanation": "Pendulum plane stays aligned with Earth",
                "period": "Infinite"
            }
        elif abs(latitude) > 85:
            return {
                "name": "POLE",
                "color": (34, 197, 94),
                "description": "Full rotation visible",
                "explanation": "Complete 360° rotation in 24 hours",
                "period": "24.0 hrs"
            }
        else:
            return {
                "name": "MID-LATITUDE",
                "color": (234, 179, 8),
                "description": "Partial rotation visible",
                "explanation": "Rotation rate depends on latitude",
                "period": f"{self.get_precession_period(latitude):.1f} hrs"
            }


class InfoPanel:
    """Dynamic educational information panel"""
    
    def __init__(self, screen: pygame.Surface, colors: Colors):
        self.screen = screen
        self.colors = colors
        self.visible = True
        self.font_title = pygame.font.Font(None, 28)
        self.font_body = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 18)
        
    def toggle(self):
        self.visible = not self.visible
        
    def draw(self, latitude: float, rotation_angle: float, physics: PhysicsEngine, fixed_mode: bool = False):
        if not self.visible:
            return
            
        # Compact panel with proper sizing
        panel_rect = pygame.Rect(10, 90, 300, 450)
        s = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        s.fill(self.colors.PANEL_BG)
        self.screen.blit(s, panel_rect.topleft)
        pygame.draw.rect(self.screen, self.colors.BORDER, panel_rect, 2, border_radius=8)
        
        y = 105
        x = 25
        
        # Get dynamic location info
        loc_info = physics.get_location_info(latitude, fixed_mode)
        
        # Title with location name
        title = self.font_title.render(f"Location: {loc_info['name']}", True, loc_info['color'])
        self.screen.blit(title, (x, y))
        y += 40
        
        # What's happening section
        happening_title = self.font_body.render("What's Happening:", True, self.colors.TEXT_PRIMARY)
        self.screen.blit(happening_title, (x, y))
        y += 30
        
        desc = self.font_small.render(loc_info['description'], True, self.colors.TEXT_SECONDARY)
        self.screen.blit(desc, (x + 10, y))
        y += 25
        
        exp = self.font_small.render(loc_info['explanation'], True, self.colors.TEXT_SECONDARY)
        self.screen.blit(exp, (x + 10, y))
        y += 35
        
        # Current status section
        status_title = self.font_body.render("Current Status:", True, self.colors.TEXT_PRIMARY)
        self.screen.blit(status_title, (x, y))
        y += 30
        
        # Status items with proper spacing
        if fixed_mode:
            status_items = [
                f"Mode: Fixed Pendulum",
                f"Latitude: {latitude:.1f}°",
                f"Earth Rotation: {np.degrees(rotation_angle):.1f}°"
            ]
        else:
            status_items = [
                f"Latitude: {latitude:.1f}°",
                f"Rotation: {np.degrees(rotation_angle):.1f}°",
                f"Period: {loc_info['period']}"
            ]
        
        for item in status_items:
            text = self.font_small.render(item, True, self.colors.TEXT_SECONDARY)
            self.screen.blit(text, (x + 10, y))
            y += 25
        
        y += 20
        
        # Controls section with proper spacing
        controls_title = self.font_body.render("Controls:", True, self.colors.TEXT_PRIMARY)
        self.screen.blit(controls_title, (x, y))
        y += 30
        
        controls = [
            "1: Jump to Equator",
            "2: Jump to Mid-Latitude",
            "3: Jump to Pole",
            "F: Toggle Fixed Mode",
            "SPACE: Pause/Resume",
            "R: Reset Simulation",
            "I: Toggle This Panel",
            "ESC: Exit Program"
        ]
        
        for control in controls:
            text = self.font_small.render(control, True, self.colors.TEXT_SECONDARY)
            if y + text.get_height() < panel_rect.bottom - 10:  # keep within panel
                self.screen.blit(text, (x + 10, y))
                y += text.get_height() + 4


class ControlPanel:
    """Compact control panel"""
    
    def __init__(self, screen: pygame.Surface, colors: Colors):
        self.screen = screen
        self.colors = colors
        self.font_heading = pygame.font.Font(None, 26)
        self.font_body = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 18)
        
        self.width = screen.get_width()
        self.panel_rect = pygame.Rect(self.width - 270, 90, 260, 370)  # Increased height for new button
        self.setup_ui_elements()
        
        self.dragging_lat = False
        self.dragging_speed = False
        
    def setup_ui_elements(self):
        x = self.panel_rect.x + 20
        y = self.panel_rect.y + 55
        
        # Latitude slider
        self.lat_label_pos = (x, y)
        self.lat_slider_rect = pygame.Rect(x, y + 22, 220, 6)
        self.lat_value_pos = (x + 180, y)
        
        # Speed slider
        y += 65
        self.speed_label_pos = (x, y)
        self.speed_slider_rect = pygame.Rect(x, y + 22, 220, 6)
        self.speed_value_pos = (x + 180, y)
        
        # Preset buttons
        y += 70
        button_width = 70
        spacing = 5
        self.equator_btn = pygame.Rect(x, y, button_width, 32)
        self.mid_btn = pygame.Rect(x + button_width + spacing, y, button_width, 32)
        self.pole_btn = pygame.Rect(x + 2 * (button_width + spacing), y, button_width, 32)
        
        # Control buttons
        y += 50
        self.pause_btn = pygame.Rect(x, y, 108, 32)
        self.reset_btn = pygame.Rect(x + 117, y, 103, 32)
        
        # Info toggle
        y += 50
        self.info_btn = pygame.Rect(x, y, 220, 32)
        
        # Fixed mode toggle
        y += 40
        self.fixed_btn = pygame.Rect(x, y, 220, 32)
        
    def draw(self, latitude: float, lat_slider_pos: float, 
             speed_factor: float, speed_slider_pos: float, paused: bool, fixed_mode: bool):
        # Panel background
        s = pygame.Surface((self.panel_rect.width, self.panel_rect.height), pygame.SRCALPHA)
        s.fill(self.colors.PANEL_BG)
        self.screen.blit(s, self.panel_rect.topleft)
        pygame.draw.rect(self.screen, self.colors.BORDER, self.panel_rect, 2, border_radius=8)
        
        # Title
        title = self.font_heading.render("Controls", True, self.colors.PRIMARY)
        self.screen.blit(title, (self.panel_rect.x + 20, self.panel_rect.y + 18))
        
        # Sliders
        self._draw_slider("Latitude", self.lat_label_pos, self.lat_slider_rect, 
                         lat_slider_pos, f"{latitude:.1f}°", self.lat_value_pos)
        self._draw_slider("Speed", self.speed_label_pos, self.speed_slider_rect,
                         speed_slider_pos, f"{speed_factor:.0f}x", self.speed_value_pos)
        
        # Buttons
        mouse_pos = pygame.mouse.get_pos()
        self._draw_button(self.equator_btn, "Equator", mouse_pos, self.colors.DANGER)
        self._draw_button(self.mid_btn, "Mid-Lat", mouse_pos, self.colors.ACCENT)
        self._draw_button(self.pole_btn, "Pole", mouse_pos, self.colors.SUCCESS)
        
        pause_text = "Resume" if paused else "Pause"
        self._draw_button(self.pause_btn, pause_text, mouse_pos, self.colors.PRIMARY)
        self._draw_button(self.reset_btn, "Reset", mouse_pos, self.colors.SECONDARY)
        self._draw_button(self.info_btn, "Toggle Info", mouse_pos, self.colors.PRIMARY)
        
        # Fixed mode button with special highlighting
        fixed_color = self.colors.SECONDARY if fixed_mode else self.colors.PRIMARY
        fixed_text = "Normal Mode" if fixed_mode else "Fixed Pendulum Mode"
        self._draw_button(self.fixed_btn, fixed_text, mouse_pos, fixed_color)
        
    def _draw_slider(self, label: str, label_pos: Tuple[int, int], 
                     slider_rect: pygame.Rect, slider_pos: float, 
                     value_text: str, value_pos: Tuple[int, int]):
        text = self.font_body.render(label, True, self.colors.TEXT_PRIMARY)
        self.screen.blit(text, label_pos)
        
        value = self.font_small.render(value_text, True, self.colors.ACCENT)
        self.screen.blit(value, value_pos)
        
        pygame.draw.rect(self.screen, self.colors.BG_LIGHT, slider_rect, border_radius=3)
        
        fill_rect = pygame.Rect(slider_rect.x, slider_rect.y, slider_pos, slider_rect.height)
        pygame.draw.rect(self.screen, self.colors.PRIMARY, fill_rect, border_radius=3)
        
        handle_x = slider_rect.x + slider_pos
        pygame.draw.circle(self.screen, self.colors.TEXT_PRIMARY, 
                          (int(handle_x), slider_rect.centery), 9)
        pygame.draw.circle(self.screen, self.colors.PRIMARY, 
                          (int(handle_x), slider_rect.centery), 7)
        
    def _draw_button(self, rect: pygame.Rect, text: str, mouse_pos: Tuple[int, int], color):
        is_hover = rect.collidepoint(mouse_pos)
        btn_color = self.colors.PRIMARY_HOVER if is_hover else color
        
        pygame.draw.rect(self.screen, btn_color, rect, border_radius=6)
        pygame.draw.rect(self.screen, self.colors.BORDER, rect, 1, border_radius=6)
        
        text_surface = self.font_body.render(text, True, self.colors.TEXT_PRIMARY)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)


class Visualizer:
    """Handles visualization rendering"""
    
    def __init__(self, screen: pygame.Surface, colors: Colors):
        self.screen = screen
        self.colors = colors
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.center_x = self.width // 2
        self.center_y = self.height // 2 + 30
        self.floor_radius = 170
        self.trail: List[Tuple[float, float]] = []
        self.max_trail_points = 400
        
        self.font_title = pygame.font.Font(None, 44)
        self.font_subtitle = pygame.font.Font(None, 22)
        self.font_compass = pygame.font.Font(None, 26)
        
    def draw_background(self):
        self.screen.fill(self.colors.BG_DARK)
        
    def draw_title(self):
        title = self.font_title.render("Foucault Pendulum", True, self.colors.PRIMARY)
        title_rect = title.get_rect(center=(self.width // 2, 32))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_subtitle.render("Earth's Rotation Revealed", 
                                             True, self.colors.TEXT_SECONDARY)
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, 60))
        self.screen.blit(subtitle, subtitle_rect)
        
    def draw_floor(self, rotation_angle: float):
        # Main floor
        pygame.draw.circle(self.screen, self.colors.FLOOR, 
                          (self.center_x, self.center_y), self.floor_radius)
        pygame.draw.circle(self.screen, self.colors.BORDER, 
                          (self.center_x, self.center_y), self.floor_radius, 2)
        
        # Concentric circles
        for r in [45, 90, 135, 170]:
            pygame.draw.circle(self.screen, self.colors.BORDER, 
                             (self.center_x, self.center_y), r, 1)
        
        # Compass
        directions = [('N', 90), ('E', 0), ('S', -90), ('W', 180)]
        for label, angle in directions:
            rotated_angle = math.radians(angle) - rotation_angle
            end_x = self.center_x + self.floor_radius * 0.85 * np.cos(rotated_angle)
            end_y = self.center_y - self.floor_radius * 0.85 * np.sin(rotated_angle)
            
            pygame.draw.line(self.screen, self.colors.COMPASS, 
                           (self.center_x, self.center_y), (end_x, end_y), 2)
            
            text = self.font_compass.render(label, True, self.colors.TEXT_PRIMARY)
            text_rect = text.get_rect(center=(end_x, end_y))
            
            pygame.draw.circle(self.screen, self.colors.BG_MEDIUM, 
                             (int(end_x), int(end_y)), 16)
            pygame.draw.circle(self.screen, self.colors.COMPASS, 
                             (int(end_x), int(end_y)), 16, 2)
            self.screen.blit(text, text_rect)
        
        # Center
        pygame.draw.circle(self.screen, self.colors.ACCENT, 
                          (self.center_x, self.center_y), 7)
        pygame.draw.circle(self.screen, self.colors.TEXT_PRIMARY, 
                          (self.center_x, self.center_y), 7, 2)
        
    def draw_inertial_reference(self):
        ref_length = 90
        start_x = self.center_x - self.floor_radius - 70
        start_y = self.center_y - self.floor_radius - 70
        end_x = start_x + ref_length
        end_y = start_y
        
        pygame.draw.line(self.screen, self.colors.INERTIAL_REF,
                        (start_x, start_y), (end_x, end_y), 4)
        
        arrow_points = [
            (end_x, end_y),
            (end_x - 14, end_y - 7),
            (end_x - 14, end_y + 7)
        ]
        pygame.draw.polygon(self.screen, self.colors.INERTIAL_REF, arrow_points)
        
        label = self.font_subtitle.render("Inertial Frame", True, self.colors.INERTIAL_REF)
        self.screen.blit(label, (start_x, start_y - 28))
        
    def draw_pendulum(self, x: float, y: float, fixed_mode: bool = False):
        bob_x = self.center_x + x
        bob_y = self.center_y + y
        
        # Trail - only in normal mode
        if not fixed_mode:
            self.trail.append((bob_x, bob_y))
            if len(self.trail) > self.max_trail_points:
                self.trail.pop(0)
            
            if len(self.trail) > 1:
                for i in range(1, len(self.trail)):
                    alpha = i / len(self.trail)
                    r = int(self.colors.TRAIL_START[0] * (1 - alpha) + self.colors.TRAIL_END[0] * alpha)
                    g = int(self.colors.TRAIL_START[1] * (1 - alpha) + self.colors.TRAIL_END[1] * alpha)
                    b = int(self.colors.TRAIL_START[2] * (1 - alpha) + self.colors.TRAIL_END[2] * alpha)
                    color = (r, g, b)
                    width = int(1 + alpha * 3)
                    pygame.draw.line(self.screen, color, self.trail[i-1], self.trail[i], width)
        
        # Wire
        pygame.draw.line(self.screen, self.colors.TEXT_SECONDARY,
                        (self.center_x, self.center_y - 130),
                        (bob_x, bob_y), 3)
        
        # Bob - different color in fixed mode
        bob_color = self.colors.SECONDARY if fixed_mode else self.colors.PENDULUM
        pygame.draw.circle(self.screen, bob_color, 
                          (int(bob_x), int(bob_y)), 11)
        pygame.draw.circle(self.screen, self.colors.TEXT_PRIMARY, 
                          (int(bob_x), int(bob_y)), 11, 2)
        
        # Add a glow effect in fixed mode
        if fixed_mode:
            for r in range(15, 11, -1):
                alpha = (15 - r) / 4
                glow_color = (
                    int(self.colors.SECONDARY[0] * alpha + 255 * (1 - alpha)),
                    int(self.colors.SECONDARY[1] * alpha + 255 * (1 - alpha)),
                    int(self.colors.SECONDARY[2] * alpha + 255 * (1 - alpha))
                )
                pygame.draw.circle(self.screen, glow_color, 
                                 (int(bob_x), int(bob_y)), r)
        
    def clear_trail(self):
        self.trail.clear()


class FoucaultPendulumSimulator:
    """Main simulation controller"""
    
    def __init__(self):
        pygame.init()
        
        self.width = 1100
        self.height = 750
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Foucault Pendulum Simulator")
        
        self.colors = Colors()
        self.physics = PhysicsEngine()
        self.visualizer = Visualizer(self.screen, self.colors)
        self.control_panel = ControlPanel(self.screen, self.colors)
        self.info_panel = InfoPanel(self.screen, self.colors)
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True
        self.paused = False
        self.fixed_mode = False  # New fixed mode flag
        
        self.amplitude = 130
        self.latitude = 48.8566
        self.time = 0
        self.dt = 0.016
        self.speed_factor = 3600
        self.rotation_angle = 0
        
        self.lat_slider_pos = self._map_to_slider(self.latitude, -90, 90)
        self.speed_slider_pos = self._map_to_slider(self.speed_factor, 100, 10000)
        
        print("\n" + "="*60)
        print("FOUCAULT PENDULUM SIMULATOR")
        print("="*60)
        print("\nKeyboard Controls:")
        print("  1/2/3: Equator/Mid-Latitude/Pole")
        print("  F: Toggle Fixed Pendulum Mode")
        print("  SPACE: Pause/Resume")
        print("  R: Reset")
        print("  I: Toggle Info Panel")
        print("  ESC: Exit")
        print("="*60 + "\n")
        
    def _map_to_slider(self, value: float, min_val: float, max_val: float) -> float:
        return (value - min_val) / (max_val - min_val) * 220
    
    def _map_from_slider(self, pos: float, min_val: float, max_val: float) -> float:
        return min_val + (pos / 220) * (max_val - min_val)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_down(event.pos)
                
            elif event.type == pygame.MOUSEBUTTONUP:
                self.control_panel.dragging_lat = False
                self.control_panel.dragging_speed = False
                
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event.pos)
                
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)
    
    def _handle_mouse_down(self, pos: Tuple[int, int]):
        if self.control_panel.lat_slider_rect.collidepoint(pos):
            self.control_panel.dragging_lat = True
        elif self.control_panel.speed_slider_rect.collidepoint(pos):
            self.control_panel.dragging_speed = True
        elif self.control_panel.equator_btn.collidepoint(pos):
            self._set_latitude(0)
        elif self.control_panel.mid_btn.collidepoint(pos):
            self._set_latitude(45)
        elif self.control_panel.pole_btn.collidepoint(pos):
            self._set_latitude(90)
        elif self.control_panel.pause_btn.collidepoint(pos):
            self.paused = not self.paused
        elif self.control_panel.reset_btn.collidepoint(pos):
            self.reset()
        elif self.control_panel.info_btn.collidepoint(pos):
            self.info_panel.toggle()
        elif self.control_panel.fixed_btn.collidepoint(pos):
            self.fixed_mode = not self.fixed_mode
            self.reset()
    
    def _handle_mouse_motion(self, pos: Tuple[int, int]):
        if self.control_panel.dragging_lat:
            x = pos[0] - self.control_panel.lat_slider_rect.x
            self.lat_slider_pos = max(0, min(220, x))
            self.latitude = self._map_from_slider(self.lat_slider_pos, -90, 90)
            self.reset()
        elif self.control_panel.dragging_speed:
            x = pos[0] - self.control_panel.speed_slider_rect.x
            self.speed_slider_pos = max(0, min(220, x))
            self.speed_factor = self._map_from_slider(self.speed_slider_pos, 100, 10000)
    
    def _handle_keydown(self, key: int):
        if key == pygame.K_ESCAPE:
            self.running = False
        elif key == pygame.K_SPACE:
            self.paused = not self.paused
        elif key == pygame.K_r:
            self.reset()
        elif key == pygame.K_i:
            self.info_panel.toggle()
        elif key == pygame.K_f:
            self.fixed_mode = not self.fixed_mode
            self.reset()
        elif key == pygame.K_1:
            self._set_latitude(0)
        elif key == pygame.K_2:
            self._set_latitude(45)
        elif key == pygame.K_3:
            self._set_latitude(90)
    
    def _set_latitude(self, latitude: float):
        self.latitude = latitude
        self.lat_slider_pos = self._map_to_slider(latitude, -90, 90)
        self.reset()
    
    def reset(self):
        self.time = 0
        self.rotation_angle = 0
        self.visualizer.clear_trail()
    
    def update(self):
        if not self.paused:
            self.time += self.dt
            x_inertial, y_inertial = self.physics.calculate_inertial_position(
                self.time, self.amplitude, self.fixed_mode)
            x_earth, y_earth, self.rotation_angle = self.physics.rotate_to_earth_frame(
                x_inertial, y_inertial, self.time, self.latitude, self.speed_factor)
            return x_earth, y_earth
        return None, None
    
    def draw(self, x: Optional[float], y: Optional[float]):
        self.visualizer.draw_background()
        self.visualizer.draw_title()
        self.visualizer.draw_floor(self.rotation_angle)
        self.visualizer.draw_inertial_reference()
        
        if x is not None and y is not None:
            self.visualizer.draw_pendulum(x, y, self.fixed_mode)
        
        self.control_panel.draw(self.latitude, self.lat_slider_pos,
                               self.speed_factor, self.speed_slider_pos, 
                               self.paused, self.fixed_mode)
        self.info_panel.draw(self.latitude, self.rotation_angle, self.physics, self.fixed_mode)
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            x, y = self.update()
            self.draw(x, y)
            self.clock.tick(self.fps)
        
        pygame.quit()
        sys.exit()


def main():
    simulator = FoucaultPendulumSimulator()
    simulator.run()


if __name__ == "__main__":

    main()
