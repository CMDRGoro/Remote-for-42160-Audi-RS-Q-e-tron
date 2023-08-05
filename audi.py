# Ports A and B: 2x Lego 22169 L Motors (for driving)
# Port D: Lego 22169 L Motor (servo mode for steering)

# Import
from pybricks.pupdevices import Motor, Remote, Light
from pybricks.parameters import Port, Direction, Stop, Button, Color
from pybricks.hubs import TechnicHub
from pybricks.tools import wait
from micropython import mem_info

# Initialize
hub = TechnicHub()
steer = Motor(Port.D)
motor1 = Motor(Port.A, Direction.CLOCKWISE)
motor2 = Motor(Port.B, Direction.CLOCKWISE)

# Connect to the remote.
hub.light.on(Color.ORANGE)
print('Waiting for remote')
remote = Remote()
hub.light.on(Color.VIOLET)

# Read the current settings
old_kp, old_ki, old_kd, _, _ = steer.control.pid()

# Set new values
steer.control.pid(kp=old_kp*4, kd=old_kd*0.4)
lightstatus = 0
steertarget = 0
steermode = 1
drive_speed = 0
remote.light.on(Color.GREEN)
print('PRECISION MODE')

# Find the steering endpoint on the left and right.
left_end = steer.run_until_stalled(-200, then=Stop.HOLD)
right_end = steer.run_until_stalled(200, then=Stop.HOLD)

# Reset this angle to be half the difference.
# Zero is in the middle.
steer.reset_angle((right_end - left_end)/2)
steer.run_target(speed=400, target_angle=0, wait=False)

# Set steering angle
steer_angle = (((right_end - left_end)/2)-5)
print('steer angle:',steer_angle)

# Redy to Drive
print('REDY')
while True:
    # Check which buttons are pressed.
    pressed = remote.buttons.pressed()

    # Mode Change
    if (Button.LEFT in pressed) and (steermode == 0):
        steermode = 1
        print('PRECISION MODE')
        remote.light.on(Color.GREEN)
        drive_speed = 0
        wait(500)
    elif (Button.LEFT in pressed) and (steermode == 1):
        steermode = 0
        print('AGRESSIVE MODE')
        remote.light.on(Color.RED)
        steertarget = 0
        wait(500)

    # Agressive steering
    if (Button.LEFT_MINUS in pressed) and (steermode == 0):
        steer.track_target(-steer_angle)
    elif (Button.LEFT_PLUS in pressed) and (steermode == 0):
        steer.track_target(steer_angle)
    # Reeturn To center
    else:
        if (steermode == 0):
            steer.track_target(0)

    # Precision steering
    if (Button.LEFT_MINUS in pressed) and (steermode == 1) and (steertarget>(-steer_angle)):
        steertarget = (steertarget - 1)
        print('target angle' ,(steertarget))
        steer.run_target(1400, steertarget, Stop.HOLD, False)
    elif (Button.LEFT_PLUS in pressed) and (steermode == 1) and (steertarget<(steer_angle)):
        steertarget = (steertarget + 1)
        print('target angle' ,(steertarget))
        steer.run_target(1400, steertarget, Stop.HOLD, False)

    # Show Battery, Memory Usage then Stop the Program.
    if Button.CENTER in pressed:
        print('Battery voltage:',((hub.battery.voltage())/1000)/6,"V")
        mem_info()
        wait(500)
        hub.system.shutdown()

    # Brake
    if (Button.RIGHT in pressed):
        drive_speed = 0

    # Set Drive Speed Agressive Mode
    if steermode == 0:
        drive_speed = 0
    if (Button.RIGHT_PLUS in pressed) and (steermode == 0 ):
        drive_speed += 100
    elif (Button.RIGHT_MINUS in pressed) and (steermode == 0):
        drive_speed -= 100

    # Set Drive Speed Precision Mode
    if (Button.RIGHT_PLUS in pressed) and (steermode == 1) and (drive_speed < 100):
        drive_speed = (drive_speed + 1)
        print('Drive Speed:',(drive_speed))
    elif (Button.RIGHT_MINUS in pressed) and (steermode == 1) and (drive_speed > -100):
        drive_speed = (drive_speed - 1)
        print('Drive Speed:', (drive_speed))

    # Apply Drive Speed
    motor1.dc(drive_speed)
    motor2.dc(drive_speed)

    # Battery Indicator on Hub
    if hub.battery.voltage()/600 > 12:
        hub.light.on(Color.BLUE)
    else:
        if hub.battery.voltage()/600 > 10:
            hub.light.on(Color.GREEN)
        else:
            if hub.battery.voltage()/600 > 9:
                hub.light.on(Color.ORANGE)
            else:
                if hub.battery.voltage()/600 > 8:
                    hub.light.on(Color.RED)

    # Wait
    wait(10)
