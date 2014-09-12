#!/usr/bin/env python

from Maestor import maestor
import alsaaudio
import audioop
import sys
import time

robot = maestor()
audioInput = 0

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
        
        for i in range(0, 1000):
            l, data = audioInput.read()
            if l > 0:
                lchan = audioop.tomono(data, 2, 1, 0)
                rchan = audioop.tomono(data, 2, 0, 1)
                lmax = audioop.max(lchan, 2)
                rmax = audioop.max(rchan, 2)
                #calculage the difference in intensity. Positive difference means the source
                #is further to the left 
                
                diff = lmax - rmax
                avgDiff = avgDiff + diff
                time.sleep(.001) #audio refresh rate

        avgDiff = avgDiff / 1000
        print avgDiff
        #Logistic Sigmoid function! 
        
        z = Math.exp(-1 * alpha * avgDiff)
        error = (1 / (1 + z)) - 0.5
        return error
        
    except Exception:
        sys.exit(0)
    

def adjust(error):
    #adjusts hubo's neck yaw to position himself closer to the source of the sound
    #robot.setProperty("NKY", "position", error) #will work on it. But for now. 
    pass
    

def main():
    #The main part of the program
    while True:
        err = localize()
        adjust(err)
        time.sleep(1)


if __name__ == '__main__':
    main()