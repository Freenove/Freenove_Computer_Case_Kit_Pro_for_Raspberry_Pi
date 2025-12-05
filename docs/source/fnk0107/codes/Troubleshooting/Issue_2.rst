##############################################################################
Issue 2: Misaligned Mouse Mapping Coordinates
##############################################################################

At the time of this writing, compatibility issues associated with the latest Raspberry Pi OS release ("Trixie") have been observed. Once an official update addressing these issues is available, we will promptly update our resources and discontinue the relevant troubleshooting notes here

Description
**********************************************************

When the HDMI display resolution is changed, the mouse click position in the VNC interface will be misaligned. This issue arises because the VNC virtual display area is now composed of a combined "HDMI + DSI dual-display" region, rather than the previous "HDMI-only" display area. The mouse coordinate mapping, however, is not updated in real time, resulting in a discrepancy between the actual and expected click positions. 

Solution
**********************************************************

Restart the VNC interface. The mouse coordinate mapping will be reset and function correctly thereafter.