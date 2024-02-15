

import serial

from time import sleep

port = serial.Serial("/dev/cu.usbserial-1420", 115200)

port.write(b"\r\n\r\n") # Hit enter a few times to wake the Printrbot
sleep(2)   # Wait for Printrbot to initialize
port.flushInput()

# for l in port.readlines():
#     print("$", l)

with open("/Users/mik/test/test.gcode") as f:
    for line in f:
        print(">", line)
        while(1):
            port.write(line.encode() + b"\n")
            port.flush()
            print("sending", line)

            port.flushInput()
            grbl_out = port.readline()
            print("$", grbl_out)
            if b"ok" in grbl_out:
                break
            if b"error" in grbl_out:
                sleep(0.1)
                print("retrying")


        # sleep(0.1)
        # for l in port.readlines():
        #     print("$", l)


