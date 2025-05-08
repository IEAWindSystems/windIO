import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
from matplotlib.patches import Arc, FancyArrowPatch

points = np.array([[ 1.00000e+00, -8.91000e-03],
       [ 9.83380e-01, -5.58000e-03],
       [ 9.64570e-01, -2.61000e-03],
       [ 9.43639e-01, -5.10000e-04],
       [ 9.20709e-01,  5.80000e-04],
       [ 8.95879e-01,  4.00000e-04],
       [ 8.69269e-01, -1.34000e-03],
       [ 8.41008e-01, -4.79000e-03],
       [ 8.11238e-01, -1.00200e-02],
       [ 7.80088e-01, -1.71500e-02],
       [ 7.47717e-01, -2.63100e-02],
       [ 7.14277e-01, -3.72200e-02],
       [ 6.79927e-01, -4.96600e-02],
       [ 6.44836e-01, -6.31810e-02],
       [ 6.09166e-01, -7.72210e-02],
       [ 5.73096e-01, -9.11610e-02],
       [ 5.36795e-01, -1.04421e-01],
       [ 5.00435e-01, -1.16521e-01],
       [ 4.64195e-01, -1.27101e-01],
       [ 4.28244e-01, -1.35911e-01],
       [ 3.92764e-01, -1.42831e-01],
       [ 3.57914e-01, -1.47801e-01],
       [ 3.23863e-01, -1.50802e-01],
       [ 2.90783e-01, -1.51882e-01],
       [ 2.58823e-01, -1.51082e-01],
       [ 2.28132e-01, -1.48471e-01],
       [ 1.98882e-01, -1.44111e-01],
       [ 1.71182e-01, -1.38101e-01],
       [ 1.45181e-01, -1.30521e-01],
       [ 1.21011e-01, -1.21551e-01],
       [ 9.87710e-02, -1.11361e-01],
       [ 7.85810e-02, -1.00181e-01],
       [ 6.05210e-02, -8.82510e-02],
       [ 4.47000e-02, -7.58210e-02],
       [ 3.11800e-02, -6.31210e-02],
       [ 2.00300e-02, -5.03510e-02],
       [ 1.13000e-02, -3.76400e-02],
       [ 5.03000e-03, -2.50200e-02],
       [ 1.26000e-03, -1.25600e-02],
       [ 0.00000e+00, -1.19000e-03],
       [ 1.26000e-03,  1.32600e-02],
       [ 5.03000e-03,  2.66700e-02],
       [ 1.13000e-02,  4.00100e-02],
       [ 2.00300e-02,  5.33910e-02],
       [ 3.11800e-02,  6.65510e-02],
       [ 4.47000e-02,  7.93810e-02],
       [ 6.05210e-02,  9.16710e-02],
       [ 7.85810e-02,  1.03231e-01],
       [ 9.87710e-02,  1.13851e-01],
       [ 1.21011e-01,  1.23321e-01],
       [ 1.45181e-01,  1.31461e-01],
       [ 1.71182e-01,  1.38141e-01],
       [ 1.98882e-01,  1.43251e-01],
       [ 2.28132e-01,  1.46731e-01],
       [ 2.58823e-01,  1.48661e-01],
       [ 2.90783e-01,  1.49081e-01],
       [ 3.23863e-01,  1.48071e-01],
       [ 3.57914e-01,  1.45781e-01],
       [ 3.92764e-01,  1.42301e-01],
       [ 4.28244e-01,  1.37761e-01],
       [ 4.64195e-01,  1.32291e-01],
       [ 5.00435e-01,  1.26011e-01],
       [ 5.36795e-01,  1.19091e-01],
       [ 5.73096e-01,  1.11691e-01],
       [ 6.09166e-01,  1.03911e-01],
       [ 6.44836e-01,  9.58710e-02],
       [ 6.79927e-01,  8.76610e-02],
       [ 7.14277e-01,  7.93910e-02],
       [ 7.47717e-01,  7.11610e-02],
       [ 7.80088e-01,  6.30910e-02],
       [ 8.11238e-01,  5.52810e-02],
       [ 8.41008e-01,  4.78000e-02],
       [ 8.69269e-01,  4.07400e-02],
       [ 8.95879e-01,  3.41700e-02],
       [ 9.20709e-01,  2.81200e-02],
       [ 9.43639e-01,  2.26600e-02],
       [ 9.64570e-01,  1.77500e-02],
       [ 9.83380e-01,  1.33300e-02],
       [ 1.00000e+00,  9.37000e-03]])[::-1]
points[:, 0] -= 0.3
points = np.hstack((points, np.zeros((points.shape[0], 1))))
chord = np.array([np.linspace(0., 1.0, 10),
                 np.zeros(10), np.zeros(10)]).T
chord[:, 0] -= 0.3
rot_angle = 20
# Create rotation object: 20 degrees about z-axis
rot = R.from_euler('z', rot_angle, degrees=True)

# Apply rotation
rotated_points = rot.apply(points)
rotated_chord = rot.apply(chord)

# Plotting
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(*rotated_points[:, :2].T, 'k')
# ax.fill(x_rot, y_rot, color='lightblue', alpha=0.3)
ax.plot(*rotated_chord[:, :2].T, 'k--')
# Reference coordinate system at leading edge
ax.plot(0, 0, 'ko')  # origin
ax.annotate('reference_axis (x, y, z)', xy=(-0.01, 0.01), xytext=(-0.35, 0.2), arrowprops=dict(arrowstyle='->', color="black", linewidth=1))
ax.arrow(0, 0, 0.3, 0, head_width=0.01, head_length=0.02, fc='k', ec='k')
ax.arrow(0, 0, 0, 0.3, head_width=0.01, head_length=0.02, fc='k', ec='k')
#ax.arrow(0, 0, 0.1, 0.1, head_width=0.01, head_length=0.02, fc='k', ec='k')
ax.text(0, 0.32, 'x', fontsize=12)
ax.text(0.32, 0, 'y', fontsize=12)
#ax.text(0.1, 0.13, 'z', fontsize=12)

# Draw twist rotation arc between x-axis and rotated chord line
arc = Arc(
    (0, 0),                    # center at origin
    width=0.5, height=0.5,     # size of the arc
    angle=0,                   # no rotation of the arc itself
    theta1=0, theta2=rot_angle,       # start and end angle in degrees
    color='blue', lw=2
)
# ax.add_patch(arc)

arrow = FancyArrowPatch(
    (0.25, 0), (0.25*np.cos(np.deg2rad(20)), 0.25*np.sin(np.deg2rad(20))),
    connectionstyle="arc3,rad=0.1",
    arrowstyle="->",
    mutation_scale=10,
    linewidth=2, color='blue'
)
ax.add_patch(arrow)
# Label the twist angle
ax.text(0.28, 0.05, r'twist, positive towards feather', color='black', fontsize=12)

offset_x = np.array([np.linspace(-0.3, 0., 10),
                     -0.05*np.ones(10), np.zeros(10)]).T
rot_angle = 20
# Create rotation object: 20 degrees about z-axis
rot = R.from_euler('z', rot_angle, degrees=True)

# Apply rotation
offset_x = rot.apply(offset_x)
ax.annotate(
    '', xy=offset_x[-1, :2], xytext=offset_x[0, :2],
    arrowprops=dict(arrowstyle='<->', color="blue", linewidth=2)
)
ax.annotate(
    'section_offset_x', xy=offset_x[-1, :2], xytext=np.array([-0.11, -0.12]),
    
)
# Style
ax.axis('equal')
plt.axis('off')

# plt.show()
plt.savefig("chord_reference_system.svg")
