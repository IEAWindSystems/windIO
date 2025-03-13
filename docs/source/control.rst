
****************************************
Actuators and Controllers
****************************************

**NOTE windIO has moved!** The windIO source code repository and documentation have moved to the following locations:

- Documentation is hosted at https://ieawindsystems.github.io/windio
- Source code repository is now https://github.com/ieawindsystems/windio

----

Actuators
************


.. literalinclude:: ../../test/turbine_example.yaml
    :start-after: # Actuators
    :end-before: # Control


pitch
########################################

:code:`fine_pitch` : Float, rad
    Optimal pitch angle of the wind turbine. As default, it is
    maintained constant in region II.

    *Minimum* = -10    *Maximum* = 10


:code:`max_pitch_rate` : Float, rad/s
    Maximum pitch rate of the rotor blades.

    *Minimum* = 0    *Maximum* = 0.2


:code:`pitch_act_bw` : Float, rad/s
    Bandwidth of 2nd order LPF representing pitch actuators

    *Minimum* = 0    *Maximum* = 100


:code:`max_pitch` : Float, rad
    Maximum pitch angle, where the default is 90 degrees. It is used
    by the ROSCO controller (https://github.com/NREL/ROSCO)

    *Minimum* = 0    *Maximum* = 2.0


:code:`min_pitch` : Float, rad
    Minimum pitch angle, where the default is 0 degrees. It is used by
    the ROSCO controller (https://github.com/NREL/ROSCO)

    *Minimum* = -0.5    *Maximum* = 1.0




generator
########################################

:code:`rated_power` : Float, W
    Nameplate power of the turbine, i.e. the rated electrical output
    of the generator.

    *Minimum* = 0

:code:`max_gen_speed` : Float, rad/s
    Maximum generator speed of the wind turbine.

    *Minimum* = 0    *Maximum* = 10


:code:`max_torque_rate` : Float, Nm/s
    Maximum torque rate of the wind turbine generator.

    *Minimum* = 1000    *Maximum* = 100000000




hss_brake
########################################

:code:`start_time` : Float, seconds
    Time in simulation that brake is activated, THSSBrDp in OpenFAST

    *Minimum* = 0

:code:`duration` : Float, seconds
    Time for HSS-brake to reach full deployment once initiated (sec),
    HSSBrDT in OpenFAST

    *Minimum* = 0

:code:`torque` : Float, N-m
    Fully deployed HSS-brake torque, HSSBrTqF in OpenFAST

    *Minimum* = 0



Control
***********


.. literalinclude:: ../../test/turbine_example.yaml
    :start-after: # Control
    :end-before: # Environment


supervisory
########################################

:code:`Vin` : Float, m/s
    Cut-in wind speed of the wind turbine.

    *Minimum* = 0    *Maximum* = 10


:code:`Vout` : Float, m/s
    Cut-out wind speed of the wind turbine.

    *Minimum* = 0    *Maximum* = 50


:code:`maxTS` : Float, m/s
    Maximum allowable blade tip speed.

    *Minimum* = 60    *Maximum* = 120




pitch
########################################

:code:`PC_omega` : Float, rad/s
    Pitch controller desired natural frequency. It is used by the
    ROSCO controller (https://github.com/NREL/ROSCO)

    *Minimum* = 0    *Maximum* = 5


:code:`PC_zeta` : Float
    Pitch controller desired damping ratio. It is used by the ROSCO
    controller (https://github.com/NREL/ROSCO)

    *Minimum* = 0    *Maximum* = 5


:code:`ps_percent` : Float
    Percent peak shaving. It is used by the ROSCO controller
    (https://github.com/NREL/ROSCO)

    *Minimum* = 0    *Maximum* = 1




fl_feedback
========================================

Platform velocity feedback using nacelle IMU

:code:`gain` : Float, seconds
    Platform velocity feedback gain used by the ROSCO controller
    (https://github.com/NREL/ROSCO)



twr_feedback
========================================

Tower velocity feedback using nacelle IMU

:code:`gain` : Float, seconds
    Tower velocity feedback gain used by the ROSCO controller
    (https://github.com/NREL/ROSCO)



IPC
========================================

Individual pitch control (IPC) using the mulitblade coordinate (MBC) transform

:code:`IPC_gain_1P` : Float, rad/Nm
    Integral gain of 1P feedback

    *Minimum* = 0

:code:`IPC_gain_2P` : Float, rad/Nm
    Integral gain of 2P feedback

    *Minimum* = 0

:code:`IPC_phase_1P` : Float, rad
    Phase lag of 1P IPC feedback

    *Minimum* = -3.14    *Maximum* = 3.14


:code:`IPC_phase_2P` : Float, rad
    Phase lag of 2P IPC feedback

    *Minimum* = -3.14    *Maximum* = 3.14




torque
########################################

:code:`control_type` : String from, ['tsr_tracking', 'legacy', 'pi_transitions']
    Type of torque control used.

:code:`tsr` : Float
    Rated tip speed ratio of the wind turbine. As default, it is
    maintained constant in region II.

    *Minimum* = 0    *Maximum* = 15


:code:`VS_zeta` : Float
    Torque controller desired damping ratio. It is used by the ROSCO
    controller (https://github.com/NREL/ROSCO)

    *Minimum* = 0    *Maximum* = 5


:code:`VS_omega` : Float, rad/s
    Torque controller desired natural frequency. It is used by the
    ROSCO controller (https://github.com/NREL/ROSCO)

    *Minimum* = 0    *Maximum* = 5


:code:`VS_minspd` : Float, rad/s
    Minimum rotor speed. It is used by the ROSCO controller
    (https://github.com/NREL/ROSCO)

    *Minimum* = 0    *Maximum* = 5




setpoint_smooth
########################################

:code:`ss_vsgain` : Float
    Torque controller setpoint smoother gain bias percentage. It is
    used by the ROSCO controller (https://github.com/NREL/ROSCO)

    *Minimum* = 0    *Maximum* = 1


:code:`ss_pcgain` : Float
    Pitch controller setpoint smoother gain bias percentage. It is
    used by the ROSCO controller (https://github.com/NREL/ROSCO)

    *Minimum* = 0    *Maximum* = 1




shutdown
########################################

Turbine shutdown control, when a certain limit is reached

:code:`limit_type` : String from, ['time', 'pitch', 'yaw', 'gen_speed', 'wind_speed', 'plt_pitch', 'nac_IMU']
    What value is used to trigger shutdown procedure

:code:`limit_value` : Float
    When limit_type > limit_value, shutdown is initiated

:code:`pitch_rate` : Float, rad/s
    Rate of pitch manuever to max_pitch. Default is 2 deg./s ?

    *Minimum* = 0    *Maximum* = 0.2




open_loop_pitch
========================================



wind_speed_estimator
########################################

Extended Kalman filter implementation of wind speed estimator

:code:`gen_process_noise` : Float
    Process noise for EKF generator speed state, Default = 1e-5

    *Minimum* = 0    *Maximum* = 0.001


:code:`turb_intensity` : Float
    Turbulence intensity defined in usual way, parameterizes EKF
    process noise for wind, Default = 0.14

    *Minimum* = 0    *Maximum* = 0.5


:code:`turb_length_scale` : Float
    Turbulence length scale, parameterizes EKF process noise for wind,
    Defulat = 3 * TurbineDiameter

    *Minimum* = 0    *Maximum* = 1000




yaw
########################################

Yaw control for changing wind direction or steady offset as implemented by ROSCO

:code:`yaw_error_thresh` : Float, rad^2 s
    Yaw error threshold, Turbine begins to yaw when it passes this

    *Minimum* = 0

:code:`yaw_filt_fast` : Float, rad/s
    Corner frequency for fast low pass filter, Default = 1.0 Hz

    *Minimum* = 1e-06

:code:`yaw_filt_slow` : Float, rad/s
    Corner frequency for slow low pass filter, Default = 1/60 Hz

    *Minimum* = 1e-09

:code:`yaw_rate` : Float, rad/s
    Yaw rate when changing yaw

    *Minimum* = 0



power_control
########################################

:code:`method` : String from, ['gen_speed']
    Method used to control power output, generator speed only for now.



reference_control
========================================

Control power reference R

:code:`method` : String from, ['constrained_ref_control', 'open_loop_opt']
    Method of controlling power reference R

:code:`const_gen_lim` : Float, rad/s
    Generator speed limit to start de-rating

    *Minimum* = 0

:code:`const_gen_gain` : Float, (rad/s)^-1
    Gain for de-rating when gen speed > lim

    *Minimum* = 0

:code:`const_gen_est` : Float, (rad/m)
    Generator speed transient estimation gain

    *Minimum* = 0

:code:`const_plt_lim` : Float, rad
    Platform pitch limit to start de-rating

    *Minimum* = 0

:code:`const_plt_gain` : Float, (rad)^-1
    Gain for de-rating when plt pitch > lim

    *Minimum* = 0

:code:`const_plt_est` : Float, (rad)/(m/s)
    Platform pitch transient estimation gain

    *Minimum* = 0



freq_avoidance
########################################

Changes generator speed setpoint to avoid turbine natural frequencies

:code:`list_of_freqs` : Array of Floats, rad/s
    List of frequencies to avoid

:code:`avoidance_param` : Array of Floats, rad/s
    Buffer speed around frequencies to avoid



soft_cut_out
########################################

Upper limit of power reference at high wind speeds (lookup table)

:code:`wind_speeds` : Array of Floats, m/s
    List of wind speeds

:code:`power_reference` : Array of Floats, (-)
    List of power reference at wind_speeds, number of elements should
    be same



user_defined_SS_1
########################################

User defined state-space linear controllers within ROSCO, only 1 for now


user_defined_SS_2
########################################

User defined state-space linear controllers within ROSCO, only 1 for now


user_defined_SS_3
########################################

User defined state-space linear controllers within ROSCO, only 1 for now


user_defined_SS_4
########################################

User defined state-space linear controllers within ROSCO, only 1 for now


user_defined_SS_5
########################################

User defined state-space linear controllers within ROSCO, only 1 for now


user_defined_TF_1
########################################

User defined transfer function linear controllers within ROSCO, only 1 for now


user_defined_TF_2
########################################

User defined transfer function linear controllers within ROSCO, only 1 for now


user_defined_TF_3
########################################

User defined transfer function linear controllers within ROSCO, only 1 for now


user_defined_TF_4
########################################

User defined transfer function linear controllers within ROSCO, only 1 for now


user_defined_TF_5
########################################

User defined transfer function linear controllers within ROSCO, only 1 for now


user_defined_OL_1
########################################



user_defined_OL_2
########################################



user_defined_OL_3
########################################



user_defined_OL_4
########################################



user_defined_OL_5
########################################



user_dylib
########################################

User defined dynamic library.

:code:`dylib` : String
    Dynamic library file path & name

:code:`dylib_input` : String
    Dynamic library file input



user_simulink
########################################

User defined simulink model

:code:`simulink_model` : String
    Path to simulink model

:code:`matlab_path` : String
    Path to matlab executable

:code:`sim_param_file` : String
    Path to matlab script with simulation parameters


