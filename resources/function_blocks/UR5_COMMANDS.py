
"""
this file allows to parse the data received and send commands via Secondary client communications interface (port 30002)
data described in Excel document "Client_Interface_V3.5" in the "DataStreamFromURController" tab
commands described in pdf scriptManual - URScript Programming Language
"""

import struct
import socket
import time


joint_names = ['base_joint', 'shoulder_joint', 'elbow_joint',
               'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']
joint_offsets = {}

class PackageType():
    # This class translates received number into package types
    ROBOT_MODE_DATA = 0
    JOINT_DATA = 1
    TOOL_DATA = 2
    MASTERBOARD_DATA = 3
    CARTESIAN_INFO = 4
    KINEMATICS_INFO = 5
    CONFIGURATION_DATA = 6
    FORCE_MODE_DATA = 7
    ADDITIONAL_INFO = 8
    CALIBRATION_DATA = 9

class RobotMode(object):
    # This class translates received values into Robot Modes
    DISCONNECTED = 0
    CONFIRM_SAFETY = 1
    BOOTING = 2
    POWER_OFF = 3
    POWER_ON = 4
    IDLE = 5
    BACKDRIVE = 6
    RUNNING = 7
    UPDATING_FIRMWARE = 8

class ControlMode(object):
    # This class translates received values into Control Modes
    POSITION = 0
    TEACH = 1
    FORCE = 2
    TORQUE = 3

class JointMode(object):
    # This class translates received values into Joint Modes
    SHUTTING_DOWN = 236
    PART_D_CALIBRATION = 237
    BACKDRIVE = 238
    POWER_OFF = 239
    # EMERGENCY_STOPPED = 240
    # CALVAL_INITIALIZATION = 241
    # ERROR = 242
    # FREEDRIVE = 243
    # SIMULATED = 244
    NOT_RESPONDING = 245
    MOTOR_INITIALISATION = 246
    BOOTING = 247
    PART_D_CALIBRATION_ERROR = 248
    BOOTLOADER = 249
    CALIBRATION = 250
    # STOPPED = 251
    FAULT = 252
    RUNNING = 253
    IDLE = 255

class ToolMode(object):
    # This class translates received values into Tool Modes
    BOOTLOADER = 249
    RUNNING = 253
    IDLE = 255

class SafetyMode(object):
    # This class translates received values into Safety Modes
    NORMAL = 1
    REDUCED = 2
    PROTECTIVE_STOP = 3
    RECOVERY = 4
    SAFEGUARD_STOP = 5
    SYSTEM_EMERGENCY_STOP = 6
    ROBOT_EMERGENCY_STOP = 7
    VIOLATION = 8
    FAULT = 9

# ----------------------------- RobotState Package types Parsers-----------------------------------
class RobotModeData:
    # represents Robot Mode Data
    __slots__ = ['timestamp', 'robot_connected', 'real_robot_enabled',
                 'power_on_robot', 'emergency_stopped',
                 'security_stopped', 'program_running', 'program_paused',
                 'robot_mode', 'control_mode', 'target_speed_fraction',
                 'speed_scaling', 'target_speed_fraction_limit']

    def unpack(self, buf):
        # parses Robot Mode Data
        rmd = RobotModeData()
        (_, _,
         rmd.timestamp, rmd.robot_connected, rmd.real_robot_enabled,
         rmd.power_on_robot, rmd.emergency_stopped, rmd.security_stopped,
         rmd.program_running, rmd.program_paused, rmd.robot_mode, rmd.control_mode,
         rmd.target_speed_fraction, rmd.speed_scaling, rmd.target_speed_fraction_limit) = struct.unpack_from(
            "!IBQ???????BBddd", buf)
        return rmd

class JointData:
    # represents Joint Data
    __slots__ = ['q_actual', 'q_target', 'qd_actual',
                 'I_actual', 'V_actual', 'T_motor', 'T_micro', 'joint_mode']

    def unpack(self, buf):
        # parses Joint Data
        all_joints = []
        offset = 5
        for i in range(6):
            jd = JointData()
            (jd.q_actual, jd.q_target, jd.qd_actual, jd.I_actual, jd.V_actual,
             jd.T_motor, jd.T_micro,
             jd.joint_mode) = struct.unpack_from("!dddffffB", buf, offset)
            offset += 41
            all_joints.append(jd)
        return all_joints

class ToolData:
    # represents Tool Data
    __slots__ = ['analog_input_range2', 'analog_input_range3',
                 'analog_input2', 'analog_input3',
                 'tool_voltage_48V', 'tool_output_voltage', 'tool_current',
                 'tool_temperature', 'tool_mode']

    def unpack(self, buf):
        # parses tool data
        td = ToolData()
        (_, _,
         td.analog_input_range2, td.analog_input_range3,
         td.analog_input2, td.analog_input3,
         td.tool_voltage_48V, td.tool_output_voltage, td.tool_current,
         td.tool_temperature, td.tool_mode) = struct.unpack_from("!IBbbddfBffB", buf)
        return td

class MasterboardData:
    # represents Masterboard Data
    __slots__ = ['digital_input_bits', 'digital_output_bits',
                 'analog_input_range0', 'analog_input_range1',
                 'analog_input0', 'analog_input1',
                 'analog_output_domain0', 'analog_output_domain1',
                 'analog_output0', 'analog_output1',
                 'masterboard_temperature',
                 'robot_voltage_48V', 'robot_current',
                 'master_io_current', 'safety_mode',
                 'in_reduced_mode'] #slots related to 'euromap' ignored

    def unpack(self, buf):
        # parses Masterboard Data
        md = MasterboardData()
        (_, _,
         md.digital_input_bits, md.digital_output_bits,
         md.analog_input_range0, md.analog_input_range1,
         md.analog_input0, md.analog_input1,
         md.analog_output_domain0, md.analog_output_domain1,
         md.analog_output0, md.analog_output1,
         md.masterboard_temperature,
         md.robot_voltage_48V, md.robot_current,
         md.master_io_current, md.safety_mode,
         md.in_reduced_mode) = struct.unpack_from("!IBiibbddbbddffffBB", buf)
        return md

class CartesianInfo:
    # represents Cartesian Info data
    __slots__ = ['x', 'y', 'z', 'rx', 'ry', 'rz', 'tcp_offset_x', 'tcp_offset_y', 'tcp_offset_z', 'tcp_offset_rx', 'tcp_offset_ry', 'tcp_offset_rz']

    def unpack(self, buf):
        # parses Cartesian Info data
        ci = CartesianInfo()
        (_, _,
         ci.x, ci.y, ci.z, ci.rx, ci.ry, ci.rz, ci.tcp_offset_x, ci.tcp_offset_y, ci.tcp_offset_z, ci.tcp_offset_rx, ci.tcp_offset_ry, ci.tcp_offset_rz) = struct.unpack_from("!IB12d", buf)
        return ci

class KinematicsInfo:
    # represents Kinematic Info data
    def unpack(self, buf):
        # parses Kinematic Info data
        return KinematicsInfo()

class JointLimitData:
    # helper class for ConfigurationData
    __slots__ = ['min_limit', 'max_limit', 'max_speed', 'max_acceleration']

class ConfigurationData:
    # represents Configuration data
    __slots__ = ['joint_limit_data',
                 'v_joint_default', 'a_joint_default',
                 'v_tool_default', 'a_tool_default', 'eq_radius',
                 'dh_a', 'dh_d', 'dh_alpha', 'dh_theta',
                 'masterboard_version', 'controller_box_type',
                 'robot_type', 'robot_subtype']

    def unpack(self, buf):
        # parses Configuration data.
        cd = ConfigurationData()
        cd.joint_limit_data = []
        for i in range(6):
            jld = JointLimitData()
            (jld.min_limit, jld.max_limit) = struct.unpack_from("!dd", buf, 5+16*i)
            (jld.max_speed, jld.max_acceleration) = struct.unpack_from("!dd", buf, 5+16*6+16*i)
            cd.joint_limit_data.append(jld)
        (cd.v_joint_default, cd.a_joint_default, cd.v_tool_default, cd.a_tool_default,
         cd.eq_radius) = struct.unpack_from("!ddddd", buf, 5+32*6)
        (cd.masterboard_version, cd.controller_box_type, cd.robot_type,
         cd.robot_subtype) = struct.unpack_from("!iiii", buf, 5+32*6+5*8+6*32)
        return cd

class ForceModeData:
    # represents Force Mode data
    __slots__ = ['x', 'y', 'z', 'rx', 'ry', 'rz', 'robot_dexterity']

    def unpack(self, buf):
        # parses Force Mode data
        fmd = ForceModeData()
        (_, _, fmd.x, fmd.y, fmd.z, fmd.rx, fmd.ry, fmd.rz,
         fmd.robot_dexterity) = struct.unpack_from("!IBddddddd", buf)
        return fmd

class AdditionalInfo:
    # represents additional info data
    __slots__ = ['freedrive_button_pressed', 'freedrive_button_enabled', 'io_enabled_freedrive']

    def unpack(self, buf):
        # parses additional info data
        ai = AdditionalInfo()
        (_,_,ai.freedrive_button_pressed, ai.freedrive_button_enabled, ai.io_enabled_freedrive) = struct.unpack_from("!IBBBB", buf)
        return ai

# --------------------------- Robot MessageType General Parser-----------------------------
class RobotState(object):
    # represents all possible types of data received
    __slots__ = ['robot_mode_data', 'joint_data', 'tool_data',
                 'masterboard_data', 'cartesian_info',
                 'kinematics_info', 'configuration_data',
                 'force_mode_data', 'additional_info',
                 'unknown_ptypes']

    def __init__(self):
        self.unknown_ptypes = []

    def unpack_main(self):
        host = "192.168.0.20"
        port = 30002
        test_socket = socket.create_connection((host, port))
        while True:    # create socket connection
            buf = test_socket.recv(4096)
            packet_length = struct.unpack_from("!i", buf)[0]
            if (len(buf) >= packet_length) and (packet_length != 24) and (
                    packet_length != 56):
                length, mtype = struct.unpack_from("!IB", buf)
                if length != len(buf):
                    raise Exception("Could not unpack packet: length field is incorrect")
                if mtype != 16:
                    if mtype == 20:
                        print ("Likely a syntax error:")
                        print (buf[:2048])
                    raise Exception("Fatal error when unpacking RobotState packet")

                rs = RobotState()
                offset = 5
                while offset < len(buf):
                    length, ptype = struct.unpack_from("!IB", buf, offset)
                    assert offset + length <= len(buf)
                    # print ('Length:' + str(length) + ' Offset:' + str(offset))
                    # package_buf = buffer(buf, offset, length)
                    package_buf = bytes(memoryview(buf))[offset:]
                    offset += length
                    rmd = RobotModeData()
                    jd = JointData()
                    td = ToolData()
                    mbd = MasterboardData()
                    ci = CartesianInfo()
                    ki = KinematicsInfo()
                    cd = ConfigurationData()
                    fmd = ForceModeData()
                    ai = AdditionalInfo()
                    if ptype == PackageType.ROBOT_MODE_DATA:
                        rs.robot_mode_data = rmd.unpack(package_buf)
                    elif ptype == PackageType.JOINT_DATA:
                        rs.joint_data = jd.unpack(package_buf)
                    elif ptype == PackageType.TOOL_DATA:
                        rs.tool_data = td.unpack(package_buf)
                    elif ptype == PackageType.MASTERBOARD_DATA:
                        rs.masterboard_data = mbd.unpack(package_buf)
                    elif ptype == PackageType.CARTESIAN_INFO:
                        rs.cartesian_info = ci.unpack(package_buf)
                    elif ptype == PackageType.KINEMATICS_INFO:
                        rs.kinematics_info = ki.unpack(package_buf)
                    elif ptype == PackageType.CONFIGURATION_DATA:
                        rs.configuration_data = cd.unpack(package_buf)
                    elif ptype == PackageType.FORCE_MODE_DATA:
                        rs.force_mode_data = fmd.unpack(package_buf)
                    elif ptype == PackageType.ADDITIONAL_INFO:
                        rs.additional_info = ai.unpack(package_buf)
                    elif ptype == PackageType.CALIBRATION_DATA:
                        pass  # internal data, should be skipped
                    else:
                        rs.unknown_ptypes.append(ptype)
                return rs

# ------------------------------------- Send data --------------------------------------
class RobotException(Exception):
    pass

class Program(object):
    def __init__(self, prog):
        self.program = prog

    def __str__(self):
        return "Program({})".format(self.program)
    __repr__ = __str__

class send_UR:
    def __init__(self):
        self._dict = {}
        self.prog_queue = []
        self.running = False            # True when robot is on and listening
        self.host = "192.168.0.20"      # robot ip

    def is_program_running(self):
        """
        return True if robot is executing a program
        """
        rs = RobotState()
        return rs.unpack_main().robot_mode_data.program_running

    def is_robot_on(self):
        """
        Return True if robot is running (not in idle)
        """

        rs = RobotState()
        # robot mode = 7 - running
        if rs.unpack_main().robot_mode_data.robot_mode == 7 \
        and rs.unpack_main().robot_mode_data.real_robot_enabled is True \
            and rs.unpack_main().robot_mode_data.emergency_stopped is False \
            and rs.unpack_main().robot_mode_data.security_stopped is False \
            and rs.unpack_main().robot_mode_data.robot_connected is True \
                and rs.unpack_main().robot_mode_data.power_on_robot is True:
                    self.running = True
        else:
            self.running = False
        return self.running

    def initiate_robot(self):
        port = 29999
        s = socket.create_connection((self.host, port))
        s.send("power on \n")
        time.sleep(3)
        s.send("brake release \n")

    def is_point_possible(self, pose):
        # to conclude
        if pose[2] <= 0.181:
            return False
        else:
            return True

    def get_dist(self, target, joints=False):
        if joints:
            return self.get_joints_dist(target)
        else:
            return self.get_lin_dist(target)

    def get_lin_dist(self, target):
        pose = self.get_tcp_pos()
        dist = 0
        for i in range(3):
            dist += (target[i] - pose[i]) ** 2
        for i in range(3, 6):
            dist += ((target[i] - pose[i]) / 5) ** 2  # arbitrary length like
        return dist ** 0.5

    def get_joints_dist(self, target):
        joints = self.get_joint_pos()
        dist = 0
        for i in range(6):
            dist += (target[i] - joints[i]) ** 2
        return dist ** 0.5

    def wait_for_move(self, target, threshold=None, timeout=5, joints=False):
        """
        wait for a move to complete.
        for every received data calculate a dist equivalent and when it is lower than
        'threshold' we return.
        """
        if threshold is None:
            threshold = 0.001
            if threshold < 0.001:
                threshold = 0.001
        count = 0
        while True:
            if not self.is_robot_on():
                raise RobotException("Robot stopped")
            dist = self.get_dist(target, joints)
            if dist <= threshold:
                # print("Move ended")
                return
            count += 1
            if count > timeout * 10:
                raise RobotException("Goal not reached but no program has been running for {} seconds. dist is {}, threshold is {}, target is {}, current pose is {}".format(timeout, dist, threshold, target, send_UR.get_tcp_pos(self)))
            else:
                count = 0

    def get_joint_pos(self):
        """
        returns joint positions [base, shoulder, elbow, wrist1, wrist2, wrist3] in rad
        """
        i = 0
        rs = RobotState()
        jp = []
        while i < 6:
            ja = rs.unpack_main().joint_data[i].q_actual
            jp.append(ja)
            i = i+1
        return jp

    def get_tcp_pos(self):
        """
        returns tool center position [x, y, z, rx, ry, rz] - pose in meters and rad
        """
        rs = RobotState().unpack_main().cartesian_info
        tcp_pose = []
        for i in rs.__slots__:
            a = getattr(rs, i, None)
            tcp_pose.append(a)
        return tcp_pose[:6]

    def send_command(self, comm):
        """
        send program to robot in URscript format
        If program is sent while another is running the first program is aborted.
        """
        comm.strip()
        if not isinstance(comm, bytes):
            comm = comm.encode()

        port = 30002
        s = socket.create_connection((self.host, port))
        data = Program(comm + b"\n")
        self.prog_queue.append(data)

        if len(self.prog_queue) > 0:
            data = self.prog_queue.pop(0)   # removes first item in the list, and return it
            s.send(data.program)            # send program via socket
            # print ("program sent: {}".format(data.program))

    def set_digital_out(self, out, value):
        """
        set digital output. value is a bool
        """
        if value in (True, 1):
            value = "True"
        else:
            value = "False"
        self.send_command('digital_out[%s]=%s' % (out, value))

    def set_analog_out(self, out, value):
        """
        set analog output, value is a float
        """
        comm = "set_analog_out(%s, %s)" % (out, value)
        self.send_command(comm)

    def format_move(self, comm, tpose, acc, vel, radius=0, prefix=""):
        """
        formats pose given into value with 6 floats (maximum accepted by UR)
        """
        tpose = [round(i, 6) for i in tpose]
        tpose.append(acc)
        tpose.append(vel)
        tpose.append(radius)
        return "{}({}[{},{},{},{},{},{}], a={}, v={}, r={})".format(comm, prefix, *tpose)

    def send_move(self, comm, pose, acc=0.2, vel=0.5, wait=True, threshold=None):
        """
        Send a move command to the robot.
        comm  - "movel", "movep", "servoc"... "movej" ONLY if with pose
        pose - [_,_,_,_,_,_] - no need for p[] (inserts prefix automatically)
        """
        command = self.format_move(comm, pose, acc, vel, prefix="p")
        self.send_command(command)
        if wait:
            self.wait_for_move(pose[:6], threshold=threshold)
            return self.get_tcp_pos()

    def movej(self, joints, acc=0.2, vel=0.5, wait=False, threshold=None):
        """
        send movej command, joints in type list in pose(p[_,_,_,_,_,_])or joint positions([_,_,_,_,_,_])
        acc in rad/sec^2
        vel in rad/sec
        """
        command = self.format_move("movej", joints, acc, vel)
        self.send_command(command)
        if wait:
            self.wait_for_move(joints[:6], threshold=threshold, joints=True)
            return self.get_tcp_pos()

    def movec(self, pose_via, pose_to, acc=0.01, vel=0.01, wait=True, threshold=None):
        """
        Move Circular: Move to position via other position
        """
        pose_via = [round(i, 6) for i in pose_via]
        pose_to = [round(i, 6) for i in pose_to]
        prog = "movec(p%s, p%s, a=%s, v=%s, r=%s)" % (pose_via, pose_to, acc, vel, "0")
        self.send_command(prog)
        if wait:
            self.wait_for_move(pose_to, threshold=threshold)
            return self.get_tcp_pos()

    def servoc(self, pose, acc=0.01, vel=0.01):
        """
        Send a servoc
        """
        return self.send_move("servoc", pose, acc=acc, vel=vel)

    def send_move_blended(self, comm, list_poses, acc=0.4, vel=0.9, rad=0.1, wait=False, threshold=None):
        """
        joins several move commands and applies a blending radius
        pose_list is a list of poses
        command  - movej, movel...
        """
        top = "def program():\n"
        program = top
        for total_poses, pose in enumerate(list_poses):
            if total_poses == (len(list_poses) - 1):
                rad = 0
            program += self.format_move(comm, pose, acc, vel, rad, prefix="p") + "\n"
        program += "end\n"
        self.send_command(program)
        if wait:
            print (list_poses[-1])
            self.wait_for_move(target=list_poses[-1], threshold=threshold)
            return self.get_tcp_pos()

    def stopj(self, acc=1.5):
        self.send_command("stopj(%s)" % acc)




class UR5_COMMANDS:
    ss = send_UR()

    def schedule(self, event_name, event_value, X, Y, Z, RX, RY, RZ):
        if event_name == 'REQ':
            return self.request(event_value, X, Y, Z, RX, RY, RZ)

    def request(self, event_value, X, Y, Z, RX, RY, RZ):
        self.ss.send_move('movel', [X, Y, Z, RX, RY, RZ], wait=True)
        print('{0}:{1}:{2}:{3}:{4}:{5}'.format(X, Y, Z, RX, RY, RZ))
        return [event_value]
