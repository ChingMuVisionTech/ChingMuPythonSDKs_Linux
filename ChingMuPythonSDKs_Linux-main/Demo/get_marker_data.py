import os
import sys
import time
from ctypes import *

# Load dynamic Library
def LoadDll(dllPath):
    if(os.path.exists(dllPath)):
        return CDLL(dllPath)
    else:
        print("Chingmu's dynamic Library  does not exist \n")
        sys.exit()

def CMMarkerExtern(host, frameCount):
    markerPos = (c_double *(2000 * 3))()
    markerNum = cmVrpn.CMMarkerExtern(host, frameCount, markerPos)
    if(markerNum > 0):
        index = 0
        while index < markerNum:
            print("marker pose %d: X:%f Y:%f Z:%f" % (index, markerPos[index * 3], markerPos[index * 3 +1], markerPos[index * 3 + 2]))
            index = index + 1

    return markerNum

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

    frameCount = 0
    getfailed = 0

    loopState = True
    while(loopState):
        if(frameCount > 10000):
            loopState = False

        # Control acquisition frequency.parameters can be customized.
        time.sleep(0.2)

        # Enable functions as required
        markerNum = CMMarkerExtern(host, frameCount)

        if(markerNum > 0):
            getfailed = 0
        else:
            getfailed += 1

        if(getfailed > 10):
            print("Continuous acquisition failed, exit the program.")
            loopState = False

        frameCount += 1

    # quit vrpn thread
    cmVrpn.CMVrpnQuitExtern()
