
import numpy as np
from scipy.integrate import quad
from scipy.interpolate import PchipInterpolator
from scipy.spatial.transform import Rotation as R

import matplotlib.pylab as plt
import matplotlib.patches as patches 
from matplotlib.patches import PathPatch, FancyArrowPatch, Arc
from matplotlib.path import Path

af = np.array([
       [ 1.0, 0.0],
       [ 1.00000e+00, -8.91000e-03],
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
       [ 1.00000e+00,  9.37000e-03],
       [1.0, 0.0]])[::-1]

def compute_curve_length(x, y):
    st = np.zeros_like(x)
    st[1:] = np.cumsum(np.sqrt(np.diff(x) ** 2 + np.diff(y) ** 2))
    xi = PchipInterpolator(st, x)
    yi = PchipInterpolator(st, y)

    def grad_mag(s):
        return np.sqrt(xi(s, 1) ** 2 + yi(s, 1) ** 2 )

    s = np.zeros_like(x)
    for i, (st1, st2) in enumerate(zip(st[:-1], st[1:]), 1):
        s[i] = quad(grad_mag, st1, st2)[0] + s[i - 1]
    return s

class InterpArc:
    def __init__(self, s, x, y):
        self._xi = PchipInterpolator(s, x)
        self._yi = PchipInterpolator(s, y)

    def __call__(self, s):
        return np.array([self._xi(s), self._yi(s)]).T

class InterpX:
    def __init__(self, x, y, side=None):
        self._side = side
        iLE = np.argmin(x)
        self._yi_u = PchipInterpolator(x[:iLE][::-1], y[:iLE][::-1])
        self._yi_l = PchipInterpolator(x[iLE:], y[iLE:])

    def __call__(self, x):
        if self._side == "suction":
            return np.array([x, self._yi_u(x)]).T
        elif self._side == "pressure":
            return np.array([x, self._yi_l(x)]).T
        else:
            return np.array([[x, self._yi_u(x)],
                            [x, self._yi_l(x)]])



def plot_af(ax):

    ax.plot(af[:, 0], af[:,1], "k-", linewidth=2)
    return ax

# plot the reference airfoil coordinate system
if True:

    fig, ax = plt.subplots(figsize=(10, 4))

    points = af.copy()
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
    ax.plot(*rotated_points[:, :2].T, 'k')
    # ax.fill(x_rot, y_rot, color='lightblue', alpha=0.3)
    ax.plot(*rotated_chord[:, :2].T, 'k--')
    # Reference coordinate system at leading edge

    ax.plot(-0.5, -0.3, 'ko')  # origin

    ax.arrow(-0.5, -0.3, 0.3, 0., head_width=0.01, head_length=0.02, fc='k', ec='k')
    ax.arrow(-0.5, -0.3, -0., 0.3, head_width=0.01, head_length=0.02, fc='k', ec='k')
    ax.arrow(-0.5, -0.3, 0.1, 0.05, head_width=0.01, head_length=0.02, fc='k', ec='k')
    ax.text(-0.5, 0.02, 'x', fontsize=12)
    ax.text(-0.18, -0.3, 'y', fontsize=12)
    ax.text(-0.39, -0.24, 'z', fontsize=12)

    sys = ax.annotate('Reference system',
                xy=(-0.5, -0.25),
                xytext=(-0.85, -0.2),
                arrowprops=dict(arrowstyle='->',
                                color="black",
                                linewidth=1))
    ref_axis = [0.02, -0.04]
    ax.plot(*ref_axis, 'ko')  # origin
    ax.annotate('Reference axis (x, y, z)', xy=ref_axis, xytext=(0.3, -0.2), arrowprops=dict(arrowstyle='->', color="black", linewidth=1))

    # ax.plot(0, 0, 'ko')  # origin
    # ax.annotate('reference_axis (x, y, z)', xy=(-0.01, 0.01), xytext=(-0.35, 0.2), arrowprops=dict(arrowstyle='->', color="black", linewidth=1))
    # ax.arrow(0, 0, 0.3, 0, head_width=0.01, head_length=0.02, fc='k', ec='k')
    # ax.arrow(0, 0, 0, 0.3, head_width=0.01, head_length=0.02, fc='k', ec='k')
    # #ax.arrow(0, 0, 0.1, 0.1, head_width=0.01, head_length=0.02, fc='k', ec='k')
    # ax.text(0, 0.32, 'x', fontsize=12)
    # ax.text(0.32, 0, 'y', fontsize=12)
    # #ax.text(0.1, 0.13, 'z', fontsize=12)

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

    ax.plot(np.linspace(-.4, 0.5, 5), np.zeros(5), 'k--', linewidth=1)


    offset_x = np.array([np.linspace(-0.3, 0., 10),
                        -0.05*np.ones(10), np.zeros(10)]).T
    rot_angle = 20
    # Create rotation object: 20 degrees about z-axis
    rot = R.from_euler('z', rot_angle, degrees=True)

    # Apply rotation
    offset_x = rot.apply(offset_x)
    ax.annotate(
        '', xy=offset_x[-1, :2], xytext=[-0.28, -0.16],
        arrowprops=dict(arrowstyle='<-', color="blue", linewidth=2)
    )
    ax.annotate(
        'section_offset_y', xy=offset_x[-1, :2], xytext=np.array([-0.14, -0.12]),
        
    )

    ax.annotate(
        '', xy=[0, 0], xytext=ref_axis,
        arrowprops=dict(arrowstyle='->', color="blue", linewidth=2)
    )
    ax.annotate(
        'section_offset_x', xy=[0, 0.1], xytext=[0.02, -0.03],
        
    )

    ac = [-0.06, -0.02]
    ax.plot(*ac, 'ko')  # origin
    ax.annotate('Aerodynamic center (-)', xy=ac, xytext=(-0.3, 0.2), arrowprops=dict(arrowstyle='->', color="black", linewidth=1))


    # Style
    ax.axis('equal')
    plt.axis('off')

    # plt.show()
    plt.savefig("chord_reference_system.svg")


def plot_start_end_nd_arcTE(ax):

    # Define custom Bezier path vertices and codes
    verts = [
        [1.02, 0.005],      # Move to start
        [1.02, 0.02],      # Control point 1
        [1.02, 0.03],      # Control point 1
        [0.96, 0.045],    # Control point 2
        [0.90, 0.06],    # Control point 2
    ]

    codes = [
        Path.MOVETO,   # Move to start
        Path.LINETO,
        Path.CURVE4,   # Quadratic Bezier control point 2
        Path.CURVE4,   # Quadratic Bezier control point 2
        Path.CURVE4,   # Quadratic Bezier control point 2
    ]

    path = Path(verts, codes)

    # Add the Bezier path (no arrowhead)
    curve_patch = PathPatch(
        path,
        facecolor='none',
        edgecolor='blue',
        linewidth=2
    )
    ax.add_patch(curve_patch)

    # Add an arrowhead at the end point of the curve
    arrow = FancyArrowPatch(
        posA=verts[-1],  # from last control point
        posB=(0.85, 0.07),  # to end point
        arrowstyle='->',
        mutation_scale=10,
        color='blue',
        linewidth=2
    )
    ax.add_patch(arrow)

    # Define custom Bezier path vertices and codes
    verts = [
        [0.85, -0.03],    # Control point 2
        [0.96, -0.01],    # Control point 2
        [1.02, -0.03],      # Control point 1
        [1.02, -0.035],      # Control point 1
        [1.02, -0.005],      # Move to start
    ]

    codes = [
        Path.MOVETO,   # Move to start
        Path.CURVE4,   # Quadratic Bezier control point 2
        Path.CURVE4,   # Quadratic Bezier control point 2
        Path.CURVE4,   # Quadratic Bezier control point 2
        Path.LINETO,
    ]

    path = Path(verts, codes)

    # Add the Bezier path (no arrowhead)
    curve_patch = PathPatch(
        path,
        facecolor='none',
        edgecolor='blue',
        linewidth=2
    )
    ax.add_patch(curve_patch)
    # Add an arrowhead at the end point of the curve
    arrow = FancyArrowPatch(
        posA=(1.02, -0.02),  # from last control point
        posB=(1.02, 0.01),  # to end point
        arrowstyle='->',
        mutation_scale=10,
        color='blue',
        linewidth=2
    )
    ax.add_patch(arrow)



    ax.annotate(
        "nd_arc_position = 0.0", 
        xy=(1.02, 0.),                     # point to annotate
        xytext=(1.05, 0.),  # text position offset
        fontsize=15,
        fontfamily='monospace',
        color='black'
    )
    ax.annotate(
        "nd_arc_position = 1.0", 
        xy=(1.02, 0.),                     # point to annotate
        xytext=(1.05, -0.05),  # text position offset
        fontsize=15,
        fontfamily='monospace',
        color='black'
    )

    return ax

if True:
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(af[1:-1, 0], af[1:-1, 1], "k-", linewidth=2)
    ax = plot_start_end_nd_arcTE(ax)
    # plot the LE
    s = compute_curve_length(af[:, 0], af[:, 1])
    s /= s[-1]
    interp = InterpArc(s, af[:, 0], af[:, 1])
    LE = interp(0.5005)
    plt.plot(LE[0], LE[1], "ro", linewidth=5)

    ax.annotate(
        'Leading edge (LE)', xy=LE[:2], xytext=np.array([-0.5, 0.1]),
        arrowprops=dict(arrowstyle='->', color="black", linewidth=1)
    )
    plt.axis('off')
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig("airfoil_nd_arc.svg")

# plot trailing edge detail
if True:
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(af[1:-1, 0], af[1:-1, 1], "k-", linewidth=2)
    # ax = plot_start_end_nd_arcTE(ax)
    # plot the LE

    plt.plot(af[0, 0], af[0, 1], "ro", linewidth=5)
    plt.plot(af[1, 0], af[1, 1], "ro", linewidth=5)
    plt.plot(af[-2, 0], af[-2, 1], "ro", linewidth=5)

    ax.annotate(
        'TE', xy=af[0, :], xytext=np.array([1.1, 0.0]),
        arrowprops=dict(arrowstyle='->', color="black", linewidth=1)
    )
    ax.annotate(
        'TEss', xy=af[1, :], xytext=np.array([1.1, 0.05]),
        arrowprops=dict(arrowstyle='->', color="black", linewidth=1)
    )
    ax.annotate(
        'TEps', xy=af[-2, :], xytext=np.array([1.1, -0.05]),
        arrowprops=dict(arrowstyle='->', color="black", linewidth=1)
    )
    plt.axis('off')
    plt.axis("equal")

#    plt.tight_layout()
    plt.xlim([0.5, 1.2])
    plt.ylim([-0.15, 0.15])

    plt.savefig("airfoil_TE.svg")

# fixed+offset

if True:
    fig, ax = plt.subplots(figsize=(10, 4))
    ax = plot_af(ax)

    s = compute_curve_length(af[1:-1, 0], af[1:-1, 1])
    s /= s[-1]
    interp = InterpArc(s, af[1:-1, 0], af[1:-1, 1])
    cap = interp(np.linspace(0., 0.1, 30))
    cap_pts = interp(np.linspace(0., 0.1, 2))
    plt.plot(cap[:, 0], cap[:, 1], "r-", linewidth=5)
    plt.plot(cap_pts[:, 0], cap_pts[:, 1], 'go', markersize=10)

    ix = 1
    for label, pt in zip(["start_nd_arc", "end_nd_arc"], cap_pts):
        ax.annotate(
            label, 
            xy=pt,                     # point to annotate
            xytext=(pt[0], pt[1]+0.02 * ix),  # text position offset
            arrowprops=dict(arrowstyle='->', color='black'),
            fontsize=15,
            fontfamily='monospace',
            color='black'
        )
        ix += 1

    # plot the width
    arrow = FancyArrowPatch(
        (cap_pts[0][0]+0.0, cap_pts[0][1]-0.03), (cap_pts[1][0]-0.015, cap_pts[1][1]-0.03),
        connectionstyle="arc3,rad=0.02",
        arrowstyle="<->",
        mutation_scale=10,
        linewidth=2, color='blue'
    )
    ax.add_patch(arrow)
    ax.text(cap_pts[1][0]+0.02, cap_pts[1][1]-0.12, 'offset', color='black', fontfamily='monospace', fontsize=12)


    plt.axis('off')
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig("airfoil_fixed_offset.svg")


# midpoint+width

if True:
    fig, ax = plt.subplots(figsize=(10, 4))
    ax = plot_af(ax)

    s = compute_curve_length(af[:, 0], af[:, 1])
    s /= s[-1]
    interp = InterpArc(s, af[:, 0], af[:, 1])
    cap = interp(np.linspace(0.47, 0.53, 30))
    cap_pts = interp(np.linspace(0.47, 0.53, 3))
    plt.plot(cap[:, 0], cap[:, 1], "r-", linewidth=5)
    plt.plot(cap_pts[:, 0], cap_pts[:, 1], 'go', markersize=10)

    ix = 1
    for label, pt in zip(["start_nd_arc", "midpoint_nd_arc", "end_nd_arc"], cap_pts):
        ax.annotate(
            label, 
            xy=pt,                     # point to annotate
            xytext=(pt[0]+0.03, pt[1]),  # text position offset
            arrowprops=dict(arrowstyle='->', color='black'),
            fontsize=15,
            fontfamily='monospace',
            color='black'
        )
        ix += 1

    # plot the width
    arrow = FancyArrowPatch(
        (cap_pts[0][0]-0.02, cap_pts[0][1]+0.01), (cap_pts[2][0]-0.02, cap_pts[2][1]-0.01),
        connectionstyle="arc3,rad=0.4",
        arrowstyle="<->",
        mutation_scale=10,
        linewidth=2, color='blue'
    )
    ax.add_patch(arrow)
    ax.text(cap_pts[1][0]-0.1, cap_pts[1][1], 'width', color='black', fontfamily='monospace', fontsize=12)


    plt.axis('off')
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig("airfoil_midpoint_nd_arc.svg")


# start_nd_arc + offset
if True:
    fig, ax = plt.subplots(figsize=(10, 4))
    ax = plot_af(ax)

    s = compute_curve_length(af[1:-1, 0], af[1:-1, 1])
    s /= s[-1]
    interp = InterpArc(s, af[1:-1, 0], af[1:-1, 1])
    te_reinf = interp(np.linspace(0., 0.1, 30))
    te_reinf_pts = interp(np.linspace(0., 0.1, 2))
    plt.plot(te_reinf[:, 0], te_reinf[:, 1], "r-", linewidth=5)
    plt.plot(te_reinf_pts[:, 0], te_reinf_pts[:, 1], 'go', markersize=10)

    ix = 1
    for label, pt in zip(["TE_SS", "start_nd_arc"], te_reinf_pts):
        ax.annotate(
            label, 
            xy=pt,                     # point to annotate
            xytext=(pt[0], pt[1]+0.05 * ix),  # text position offset
            arrowprops=dict(arrowstyle='->', color='black'),
            fontsize=15,
            fontfamily='monospace',
            color='black'
        )
        ix += 1

    # plot the width
    arrow = FancyArrowPatch(
        (te_reinf_pts[0][0], te_reinf_pts[0][1]-0.015), (te_reinf_pts[1][0], te_reinf_pts[1][1]-0.015),
        connectionstyle="arc3,rad=0.01",
        arrowstyle="<->",
        mutation_scale=10,
        linewidth=2, color='blue'
    )
    ax.add_patch(arrow)
    ax.text(0.75, -0.0, 'offset', color='black', fontsize=12)


    plt.axis('off')
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig("airfoil_anchor+offset.svg")


# plane_intersection
if True:
    fig, ax = plt.subplots(figsize=(10, 4))

    ax.plot(-0.5, -0.3, 'ko')  # origin
    
    ax.arrow(-0.5, -0.3, 0.3, 0., head_width=0.01, head_length=0.02, fc='k', ec='k')
    ax.arrow(-0.5, -0.3, -0., 0.3, head_width=0.01, head_length=0.02, fc='k', ec='k')
    ax.arrow(-0.5, -0.3, 0.1, 0.05, head_width=0.01, head_length=0.02, fc='k', ec='k')
    ax.text(-0.5, 0.02, 'x', fontsize=12)
    ax.text(-0.18, -0.3, 'y', fontsize=12)
    ax.text(-0.39, -0.24, 'z', fontsize=12)
    
    sys = ax.annotate('Reference system',
                xy=(-0.5, -0.25),
                xytext=(-0.85, -0.2),
                arrowprops=dict(arrowstyle='->',
                                color="black",
                                linewidth=1))
    ref_axis = [0., 0.]
    ax.plot(*ref_axis, 'ko')  # origin
    ax.annotate('Reference axis (x, y, z)', xy=ref_axis, xytext=(0.3, -0.2), arrowprops=dict(arrowstyle='->', color="black", linewidth=1))
    #ax.arrow(0.3, 0.2, 0.3, 0, head_width=0.01, head_length=0.02, fc='k', ec='k')
    #ax.arrow(0, 0, 0, 0.3, head_width=0.01, head_length=0.02, fc='k', ec='k')
    #ax.arrow(0, 0, 0.1, 0.1, head_width=0.01, head_length=0.02, fc='k', ec='k')
    #ax.text(0, 0.32, 'x', fontsize=12)
    #ax.text(0.32, 0, 'y', fontsize=12)
    rot_angle = -8.
    af_rot = af.copy()
    af_rot[:, 0] -= 0.3
    af_rot = np.hstack((af_rot, np.zeros((af_rot.shape[0], 1))))
    chord_rot = np.array([np.linspace(-0.3, 0.7, 10),
                    np.zeros(10), np.zeros(10)]).T
    rot = R.from_euler('z', rot_angle, degrees=True)
    af_rot = rot.apply(af_rot)
    chord_rot = rot.apply(chord_rot)

    s = compute_curve_length(af_rot[1:-1, 0], af_rot[1:-1, 1])
    s /= s[-1]
    interpx = InterpX(af_rot[1:-1, 0], af_rot[1:-1, 1], side="suction")
    cap = interpx(np.linspace(-0.25, 0.05, 30))
    cap_pts = interpx(np.linspace(-0.25, 0.05, 3))

    ax.plot(af_rot[:, 0], af_rot[:, 1])
    ax.plot(chord_rot[:, 0], chord_rot[:, 1], "k--", linewidth=1)
    ax.plot(cap[:, 0], cap[:, 1], "r", linewidth=4)
    ax.plot(cap_pts[:, 0], cap_pts[:, 1], "go", markersize=5)

    # plot the width
    arrow = FancyArrowPatch(
        (cap_pts[0][0], cap_pts[0][1]-0.02), (cap_pts[2][0], cap_pts[2][1]-0.02),
        connectionstyle="arc3,rad=-0.175",
        arrowstyle="<->",
        mutation_scale=10,
        linewidth=2, color='blue'
    )
    ax.add_patch(arrow)
    ax.text(cap_pts[0][0], cap_pts[0][1]-0.05, 'width', color='black', fontfamily='monospace', fontsize=12)



    ix = 1
    for label, pt in zip(["end_nd_arc", "midpoint_nd_arc", "start_nd_arc"], cap_pts):
        ax.annotate(
            label, 
            xy=pt[:2],                     # point to annotate
            xytext=(pt[0]+0.3*(ix-3), pt[1] + 0.05*ix),  # text position offset
            arrowprops=dict(arrowstyle='->', color='black'),
            fontsize=15,
            fontfamily='monospace',
            color='black'
        )
        ix += 1

    arrow = FancyArrowPatch(
        (-0.1, 0.1), (0., 0.1),
        arrowstyle="<->",
        mutation_scale=10,
        linewidth=2, color='blue'
    )
    ax.add_patch(arrow)
    ax.annotate(
            "offset", 
            xy=(-0.05, 0.1),                     # point to annotate
            xytext=(0.07, 0.4),  # text position offset
            arrowprops=dict(arrowstyle='->', color='black'),
            fontsize=15,
            fontfamily='monospace',
            color='black'
        )
    ax.plot(-0.0*np.ones(5), np.linspace(-0.2, 0.5, 5), 'k--', linewidth=1)
    ax.plot(-0.1*np.ones(5), np.linspace(-0.2, 0.5, 5), 'k--', linewidth=1)
    ax.annotate(
            "intersection plane", 
            xy=(-0.1, 0.3),                     # point to annotate
            xytext=(-0.6, 0.4),  # text position offset
            arrowprops=dict(arrowstyle='->', color='black'),
            fontsize=15,
            fontfamily='monospace',
            color='black'
        )
    
    arrow = FancyArrowPatch(
    (0.45*np.cos(np.deg2rad(rot_angle-1)), 0.45*np.sin(np.deg2rad(rot_angle-1))), (0.45, 0.01),
    connectionstyle="arc3,rad=0.1",
    arrowstyle="<-",
    mutation_scale=10,
    linewidth=2, color='blue'
    )
    ax.add_patch(arrow)

    ax.annotate(
            "rotation", 
            xy=(0.45, -0.025),                     # point to annotate
            xytext=(0.6, -0.02),  # text position offset
            arrowprops=dict(arrowstyle='->', color='black'),
            fontsize=15,
            fontfamily='monospace',
            color='black'
        )
    
    ax.plot(np.linspace(-.4, 0.5, 5), np.zeros(5), 'k--', linewidth=1)
    plt.axis('off')
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig("airfoil_cap_intersection.svg")

# plane_intersection
if True:
    fig, ax = plt.subplots(figsize=(10, 4))

    ax.plot(-0.5, -0.3, 'ko')  # origin
    
    ax.arrow(-0.5, -0.3, 0.3, 0., head_width=0.01, head_length=0.02, fc='k', ec='k')
    ax.arrow(-0.5, -0.3, -0., 0.3, head_width=0.01, head_length=0.02, fc='k', ec='k')
    ax.arrow(-0.5, -0.3, 0.1, 0.05, head_width=0.01, head_length=0.02, fc='k', ec='k')
    ax.text(-0.5, 0.02, 'x', fontsize=12)
    ax.text(-0.18, -0.3, 'y', fontsize=12)
    ax.text(-0.39, -0.24, 'z', fontsize=12)
    
    sys = ax.annotate('Reference system',
                xy=(-0.5, -0.25),
                xytext=(-0.85, -0.2),
                arrowprops=dict(arrowstyle='->',
                                color="black",
                                linewidth=1))
    ref_axis = [0., 0.]
    ax.plot(*ref_axis, 'ko')  # origin
    ax.annotate('Reference axis (x, y, z)', xy=ref_axis, xytext=(0.3, 0.5), arrowprops=dict(arrowstyle='->', color="black", linewidth=1))
    #ax.arrow(0.3, 0.2, 0.3, 0, head_width=0.01, head_length=0.02, fc='k', ec='k')
    #ax.arrow(0, 0, 0, 0.3, head_width=0.01, head_length=0.02, fc='k', ec='k')
    #ax.arrow(0, 0, 0.1, 0.1, head_width=0.01, head_length=0.02, fc='k', ec='k')
    #ax.text(0, 0.32, 'x', fontsize=12)
    #ax.text(0.32, 0, 'y', fontsize=12)
    rot_angle = -8.
    af_rot = af.copy()
    af_rot[:, 0] -= 0.3
    af_rot = np.hstack((af_rot, np.zeros((af_rot.shape[0], 1))))
    chord_rot = np.array([np.linspace(-0.3, 0.7, 10),
                    np.zeros(10), np.zeros(10)]).T
    rot = R.from_euler('z', rot_angle, degrees=True)
    af_rot = rot.apply(af_rot)
    chord_rot = rot.apply(chord_rot)


    interpx = InterpX(af_rot[1:-1, 0], af_rot[1:-1, 1])
    web_pts = interpx(0.1)
    web = np.array([np.linspace(web_pts[0, 0], web_pts[1, 0]),
                    np.linspace(web_pts[0, 1], web_pts[1, 1])]).T
    ax.plot(af_rot[:, 0], af_rot[:, 1])
    ax.plot(chord_rot[:, 0], chord_rot[:, 1], "k--", linewidth=1)
    ax.plot(web[:, 0], web[:, 1], linewidth=4)
    ax.plot(web_pts[:, 0], web_pts[:, 1], "go", markersize=5)

    ix = 1
    for label, pt in zip(["start_nd_arc", "end_nd_arc"], web_pts):
        ax.annotate(
            label, 
            xy=pt,                     # point to annotate
            xytext=(pt[0]+0.1, pt[1] * ix),  # text position offset
            arrowprops=dict(arrowstyle='->', color='black'),
            fontsize=15,
            fontfamily='monospace',
            color='black'
        )
        ix += 1

    arrow = FancyArrowPatch(
        (-0.01, 0.1), (0.11, 0.1),
        arrowstyle="<->",
        mutation_scale=10,
        linewidth=2, color='blue'
    )
    ax.add_patch(arrow)
    ax.annotate(
            "offset", 
            xy=(0.05, 0.1),                     # point to annotate
            xytext=(0.07, 0.4),  # text position offset
            arrowprops=dict(arrowstyle='->', color='black'),
            fontsize=15,
            fontfamily='monospace',
            color='black'
        )
    ax.plot(np.ones(5)*0., np.linspace(-0.2, 0.5, 5), 'k--', linewidth=1)
    ax.plot(np.ones(5)*0.1, np.linspace(-0.2, 0.5, 5), 'k--', linewidth=1)
    ax.annotate(
            "intersection plane", 
            xy=(0.1, 0.3),                     # point to annotate
            xytext=(-0.6, 0.35),  # text position offset
            arrowprops=dict(arrowstyle='->', color='black'),
            fontsize=15,
            fontfamily='monospace',
            color='black'
        )
    
    arrow = FancyArrowPatch(
    (0.45*np.cos(np.deg2rad(rot_angle-1)), 0.45*np.sin(np.deg2rad(rot_angle-1))), (0.45, 0.01),
    connectionstyle="arc3,rad=0.1",
    arrowstyle="<-",
    mutation_scale=10,
    linewidth=2, color='blue'
    )
    ax.add_patch(arrow)

    ax.annotate(
            "rotation", 
            xy=(0.45, -0.025),                     # point to annotate
            xytext=(0.6, -0.02),  # text position offset
            arrowprops=dict(arrowstyle='->', color='black'),
            fontsize=15,
            fontfamily='monospace',
            color='black'
        )
    
    ax.plot(np.linspace(-.4, 0.5, 5), np.zeros(5), 'k--', linewidth=1)
    plt.axis('off')
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig("airfoil_web_intersection.svg")