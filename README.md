##Foucault Pendulum Simulator
Features
Realistic Physics Simulation: Accurate mathematical model of Foucault pendulum motion
Dual Visualization Modes:
Normal Mode: Shows pendulum oscillation and precession
Fixed Mode: Pendulum stays fixed while Earth rotates beneath it
Interactive Controls: Adjust latitude, rotation speed, and other parameters
Educational Information Panel: Real-time explanations of what's happening at different latitudes
Modern UI Design: Clean, intuitive interface with high contrast colors
Keyboard Shortcuts: Quick access to common functions

Controls
Mouse Controls
Latitude Slider: Adjust the latitude (-90° to 90°)
Speed Slider: Control simulation speed (100x to 10000x)
Preset Buttons: Jump to Equator, Mid-Latitude, or Pole
Control Buttons: Pause/Resume, Reset, Toggle Info Panel, Toggle Fixed Mode
Keyboard Shortcuts
1: Jump to Equator
2: Jump to Mid-Latitude
3: Jump to Pole
F: Toggle Fixed Pendulum Mode
SPACE: Pause/Resume simulation
R: Reset simulation
I: Toggle information panel
ESC: Exit program
Educational Value
This simulation helps visualize and understand:

How Earth's rotation affects pendulum motion
The relationship between latitude and precession rate
Why the pendulum appears to rotate relative to Earth
The difference between inertial and rotating reference frames
Key Concepts Demonstrated
At the Equator: No visible precession (pendulum plane stays aligned with Earth)
At Mid-Latitudes: Partial precession proportional to latitude
At the Poles: Complete 360° rotation in 24 hours
Physics Model
The simulation uses the following physics equations:

1.Pendulum Motion:
x(t) = A * cos(ω₀ * t)

y(t) = A * 0.3 * sin(ω₀ * t)

where ω₀ = √(g/L) is the natural frequency

2.Earth Rotation Effects:
ωp = ωe * sin(latitude)

θ = ωp * t * speed_factor

where ωe is Earth's angular velocity

3.Coordinate Transformation:

x_earth = x * cos(θ) - y * sin(θ)

y_earth = x * sin(θ) + y * cos(θ)

Normal Mode: Showing pendulum oscillation and precession

<img width="1620" height="991" alt="image" src="https://github.com/user-attachments/assets/f7229f19-9a45-468b-995d-747593f6b2a5" />

Fixed Mode: Earth rotates beneath a fixed pendulum

<img width="1622" height="973" alt="image" src="https://github.com/user-attachments/assets/cae8c323-d710-4296-a624-b9847550e1ad" />


A physics-based simulation of the **Foucault pendulum**, demonstrating how Earth’s rotation causes the apparent precession of a pendulum’s oscillation plane.
Includes latitude-dependent behavior (poles, mid-latitudes, equator) with **time scaling** to make the otherwise slow precession observable.
Built purely for the **profundity and elegance of classical mechanics**, showing how a simple pendulum reveals the motion of an entire planet.

 
