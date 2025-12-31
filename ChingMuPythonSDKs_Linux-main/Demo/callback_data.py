import os
import sys
import time
from ctypes import *


class timeval(Structure):
    _fields_ = [("tv_sec",c_long),
                ("tv_usec",c_long)]

class Vrpn_TRACKER(Structure):
    _fields_ = [
        ("msg_time", timeval),
        ("sensor", c_int),
        ("frameCounter", c_int),
        ("pos", c_double * 3),
        ("quat", c_double * 4)
    ]

class Vrpn_TRACKERVEL(Structure):
    _fields_ = [
        ("msg_time", timeval),
        ("sensor", c_int),
        ("vel", c_double * 3),
        ("vel_quat", c_double * 4),
        ("reserved", c_double)
    ]

class Vrpn_TRACKERACC(Structure):
    _fields_ = [
        ("msg_time", timeval),
        ("sensor", c_int),
        ("acc", c_double * 3),
        ("acc_quat", c_double * 4),
        ("reserved", c_double)
    ]

class Vrpn_ESKin(Structure):
    _fields_ = [
        ("sensor", c_int),
        ("name", c_char * 8),
        ("row", c_int),
        ("col", c_int),
        ("data", c_short * 4096)
    ]

# Load dynamic Library
def LoadDll(dllPath):
    if(os.path.exists(dllPath)):
        return CDLL(dllPath)
    else:
        print("Chingmu's dynamic Library  does not exist \n")
        sys.exit()

def CallbackVrpnTrackerData(voidPtr, b):
    print("timeval: %d %d frameCounter: %d id: %d pos: X:%f Y:%f Z:%f quaternion: rx:%f ry:%f rz:%f rw:%f"
        %(b.msg_time.tv_sec, b.msg_time.tv_usec, b.frameCounter, b.sensor, b.pos[0], b.pos[1], b.pos[2], b.quat[0], b.quat[1], b.quat[2], b.quat[3]))

def CallbackVrpnVelData(voidPtr, vel):
    print("timeval: %d %d id: %d vel: X:%f Y:%f Z:%f vel_quaternion: rx:%f ry:%f rz:%f"
        %(vel.msg_time.tv_sec, vel.msg_time.tv_usec, vel.sensor, vel.vel[0], vel.vel[1], vel.vel[2], vel.vel_quat[0] / 3.14 * 180, vel.vel_quat[1] / 3.14 * 180, vel.vel_quat[2] / 3.14 * 180))


def CallbackVrpnAccData(voidPtr, acc):
    print("timeval: %d %d id: %d acc: X:%f Y:%f Z:%f acc_quaternion: rx:%f ry:%f rz:%f"
        % (acc.msg_time.tv_sec, acc.msg_time.tv_usec, acc.sensor, acc.acc[0], acc.acc[1], acc.acc[2], acc.acc_quat[0] / 3.14 * 180, acc.acc_quat[1] / 3.14 * 180, acc.acc_quat[2] / 3.14 * 180))


def CallbackCamCoveredData(voidPtr, camNameList):
    s = camNameList.decode('utf-8', errors='replace')
    cam_names = s.split(',')
    print("receive cam covered data:")
    print(cam_names)

if __name__ == '__main__':
    # Set dynamic Library path
    dllPath = os.path.dirname(os.path.dirname(__file__)) + "/ChingmuDLL/libCMVrpn.so"

    # Load dynamic Library
    cmVrpn = LoadDll(dllPath)

    # set server address
    host = bytes("MCAvatar@192.168.3.35", "gbk")

    # start vrpn thread
    cmVrpn.CMVrpnStartExtern()

    # enable write trace_log.txt
    cmVrpn.CMVrpnEnableLog(True)

    callbackTrackerData = CFUNCTYPE(None, c_char_p, Vrpn_TRACKER)(CallbackVrpnTrackerData)
    result = cmVrpn.CMPluginConnectServer(host)
    print(result)

    result = cmVrpn.CMPluginRegisterTrackerData(host, None, callbackTrackerData)
    print(result)

    #callbackVelocityData = CFUNCTYPE(None, c_char_p, Vrpn_TRACKERVEL)(CallbackVrpnVelData)
    #cmVrpn.CMPluginRegisterVelocityData(host, None, callbackVelocityData)

    #callbackAccelerationData = CFUNCTYPE(None, c_char_p, Vrpn_TRACKERACC)(CallbackVrpnAccData)
    #cmVrpn.CMPluginRegisterAccelerationData(host, None, callbackAccelerationData)
    loopState = True
    while(loopState):
        time.sleep(0.0002)

    cmVrpn.CMPluginUnRegisterTrackerData(host, None, callbackTrackerData)
    #cmVrpn.CMPluginUnRegisterVelocityData(host, None, callbackVelocityData)
    #cmVrpn.CMPluginUnRegisterAccelerationData(host, None, callbackAccelerationData)
    #cmVrpn.CMPluginUnRegisterESkinData(host, None, callbackESkinData)

    # quit vrpn thread
    cmVrpn.CMVrpnQuitExtern()
