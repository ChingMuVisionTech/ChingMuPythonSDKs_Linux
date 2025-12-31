import os
import sys
import time
from ctypes import *

class timeval(Structure):
    _fields_ = [("tv_sec",c_long),
                ("tv_usec",c_long)]

class VrpnHierarchy(Structure):
    _fields_ = [("msg_time", timeval),
            ("sensor", c_int),
            ("parent", c_int),
            ("name", c_char*127)]

class VrpnEndHierarchyMsg(Structure):
    _fields_ = [("msg_time",timeval),
                ("retarget_flag",c_int)] # 0 - source, 1 - retarget

# Load dynamic Library
def LoadDll(dllPath):
    if(os.path.exists(dllPath)):
        return CDLL(dllPath)
    else:

        print("Chingmu's dynamic Library  does not exist \n")
        sys.exit()

# get hierarchy info
def CallbackUpdateHierarchy(voidPtr,hierarchy):
    print("segment name:%s segment parent id:%d segment id:%d"%(hierarchy.name.decode(),hierarchy.parent, hierarchy.sensor))

def CallbackResetHierarchy(voidPtr,msg):
    print("sec:%d,usec%d"%(msg.tv_sec,msg.tv_usec))
    print("reset hierarchy\n")

def CallbackVrpnEndHierarchy(voidPtr, endMsg):
    print("sec:%d,usec%d"%(endMsg.msg_time.tv_sec,endMsg.msg_time.tv_usec))
    print("0 - source, 1 - retarget:%d"%(endMsg.retarget_flag))

if __name__ == '__main__':
    cur_path = os.path.dirname(os.path.abspath(__file__))
    dllPath = cur_path + "/../ChingmuDLL/libCMVrpn.so"
    print(dllPath)
    # Load dynamic Library
    cmVrpn = LoadDll(dllPath)

    # set server address
    host = bytes("MCAvatar@192.168.3.35", "gbk")

    # start vrpn thread
    cmVrpn.CMVrpnStartExtern()

    # enable write trace_log.txt
    cmVrpn.CMVrpnEnableLog(True)

    userData = VrpnHierarchy(timeval(c_long(0),c_long(0)), c_int(0),c_int(0),b"0"*127)

    callbackUpdata = CFUNCTYPE(None,c_char_p,VrpnHierarchy)(CallbackUpdateHierarchy)
    callbackReset = CFUNCTYPE(None,c_char_p,timeval)(CallbackResetHierarchy)
    callbackFinishe = CFUNCTYPE(None, c_char_p, VrpnEndHierarchyMsg)(CallbackVrpnEndHierarchy)

    # Register the callback function of the received model's hierarchy
    ret = cmVrpn.CMPluginRegisterUpdateHierarchy(host, byref(userData), callbackUpdata)
    while(ret !=1):
        time.sleep(0.2)
        ret = cmVrpn.CMPluginRegisterUpdateHierarchy(host, byref(userData), callbackUpdata)

    print("Register UpdateHierarchy 1:{}".format(ret))


    # Register callback function for reset model
    ret = cmVrpn.CMPluginRegisterResetHierarchy(host, byref(userData), callbackReset)
    while(ret !=1):
        time.sleep(0.2)
        ret = cmVrpn.CMPluginRegisterResetHierarchy(host, byref(userData), callbackReset)
    print("Register UpdateHierarchy 2:{}".format(ret))

    # Register the callback function of sending completion signal
    ret = cmVrpn.CMPluginRegisterEndHierarchy(host, byref(userData), callbackFinishe)
    while(ret !=1):
        time.sleep(0.2)
        ret = cmVrpn.CMPluginRegisterEndHierarchy(host, byref(userData), callbackFinishe)
    print("Register UpdateHierarchy 3:{}".format(ret))

    loopState = True
    while(loopState):
        time.sleep(0.2)

    cmVrpn.CMPluginUnRegisterUpdateHierarchy(host, byref(userData), CallbackUpdateHierarchy)
    cmVrpn.CMPluginUnRegisterResetHierarchy(host, byref(userData), CallbackResetHierarchy)
    cmVrpn.CMPLuginUnRegisterEndHierarchy(host, byref(userData), callbackFinishe)
    # quit vrpn thread
    cmVrpn.CMVrpnQuitExtern()
