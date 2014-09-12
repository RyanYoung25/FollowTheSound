#!/usr/bin/env python

from Maestor import maestor
import alsaaudio
import audioop
import sys
import time
import math

robot = maestor()
audioInput = 0
maxPos = 1.5
minPos = -1.5

def initAudio():
    global audioInput
    #Initialize and set the properties of PCM object
    card = 'default'
    audioInput = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, card)
    audioInput.setchannels(2)
    audioInput.setrate(44100)
    audioInput.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    audioInput.setperiodsize(160)


def localize():
    #Returns an error between -1 and 1 that specifies which direction to move the head to
    try:
        #Start an infite loop that gets and analyzes audio data
        alpha = .05 #The width of the sigmoid. Gotta tweak it a little.
        
        #Average difference
        avgDiff = 0
        
        for i in range(0, 100):
            l, data = audioInput.read()
            if l > 0:
                lchan = audioop.tomono(data, 2, 1, 0)
                rchan = audioop.tomono(data, 2, 0, 1)
                lmax = audioop.max(lchan, 2)
                rmax = audioop.max(rchan, 2)
                
                #lowpass filter
                if lmax < 70 and rmax < 70:
                    continue

                #calculage the difference in intensity. Positive difference means the source
                #is further to the left 
                
                diff = lmax - rmax
                avgDiff = avgDiff + diff
                time.sleep(.001) #audio refresh rate

        avgDiff = avgDiff / 1000
        print avgDiff
        #Logistic Sigmoid function! 
        
        z = math.exp(-1 * alpha * avgDiff)
        error = (1 / (1 + z)) - 0.5
        return error
        
    except Exception, e:
        print e 
        
    

def adjust(error):
    #adjusts hubo's neck yaw to position himself closer to the source of the sound
    pos = float(robot.getProperties("NKY", "position"))
    pos = pos + error

    if pos > maxPos:
        pos = maxPos
    elif pos < minPos: 
        pos = minPos

    robot.setProperty("NKY", "position",  pos) #will work on it. But for now. 
    print pos + error

def main():
    #The main part of the program
    initAudio()
    while True:
        err = localize()
        adjust(err)
        time.sleep(.25)


if __name__ == '__main__':
    main()
