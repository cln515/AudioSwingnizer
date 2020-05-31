import numpy as np
import wave
import math
import sys

def mixRate(v,b,w):
    if v < b-w :
        return 1
    if v < b+w :
        T = 2*w
        ret = 1 - (0.5 * math.sin(math.pi * (v-(b-w))/T - math.pi/2) + 0.5)
        return ret 
    return 0

if len(sys.argv)<6:
    print("usage: swingnizer.py fast.wav slow.wav tempo length(sec) output")

# input wav files
wavl = sys.argv[1] #fast
wavs = sys.argv[2] #slow

# input tempo
tempo = int(sys.argv[3])

# input length (second)
length_sec = int(sys.argv[4])

# output file
output = sys.argv[5]

# rate speed
rate_fast = 1.5
rate_fast_length = 1/rate_fast #2/3
rate_slow = rate_fast/(2*rate_fast-1) #0.75
rate_slow_length = 1/rate_slow #4/3

#read wav data
wr = wave.open(wavl, 'r')
ch = wr.getnchannels()
width = wr.getsampwidth()
fr = wr.getframerate()
fn = wr.getnframes()

data = wr.readframes(wr.getnframes())
wr.close()
Xf = np.frombuffer(data, dtype=np.int16)

if ch == 2:
    l_channell =  Xf[::ch]
    r_channell =  Xf[1::ch]
elif ch == 1:
    l_channell =  Xf[::ch]
    

print(l_channell)
print("Channel: ", ch)
print("Sample width: ", width)
print("Frame Rate: ", fr)
print("Frame num: ", fn)
print("Params: ", wr.getparams())
print("Total time: ", 1.0 * fn / fr)

wr = wave.open(wavs, 'r')
ch = wr.getnchannels()
width = wr.getsampwidth()
fr = wr.getframerate()
fn = wr.getnframes()

data = wr.readframes(wr.getnframes())
wr.close()
Xs = np.frombuffer(data, dtype=np.int16)

if ch == 2:
    l_channels =  Xs[0::ch]
    r_channels =  Xs[1::ch]
elif ch == 1:
    l_channels =  Xs[0::ch]
    

print(l_channels)
print("Channel: ", ch)
print("Sample width: ", width)
print("Frame Rate: ", fr)
print("Frame num: ", fn)
print("Params: ", wr.getparams())
print("Total time: ", 1.0 * fn / fr)

#mix
X_out = np.zeros(fr*ch*length_sec, dtype=np.int16)
cnt = 0
buf_st = 0
while True:
    #bpm = n, 60/(n*2) sec * framerate 
    buf_en =  int(60.0*(cnt+1)/(tempo) * fr)
    if buf_en>=len(X_out)/ch:
        break
    sep = int((buf_st*rate_fast_length +buf_en*rate_slow_length)/2)
    diff_front = sep -buf_st
    diff_back = buf_en - sep
    buf_slow_st = int(buf_st * rate_slow_length)
    buf_slow_nextst = int(buf_en * rate_slow_length)
    buf_fast_st = int(buf_en * rate_fast_length - (buf_en-buf_st))
    if buf_slow_nextst >= len(Xs[0::ch]):
        break
    if buf_fast_st + (buf_en-buf_st) >= len(Xf[0::ch]):
        break
    sep_b = (sep - buf_st)/(buf_en-buf_st)
    for ch_c in range(ch):
        cpcnt=0
        #mixing border of files
        for j in range(buf_st,buf_en):
            v = (j-buf_st)/(buf_en-buf_st)
            if v>0.98:
                mixrate_fast = mixRate(v,0.99,0.01)
                mixrate_slow = 1-mixrate_fast
                X_out[ch_c::ch][j] = int(mixrate_slow * Xs[ch_c::ch][buf_slow_nextst-(buf_en-buf_st-cpcnt)] + mixrate_fast * Xf[ch_c::ch][buf_fast_st + cpcnt])
            else:    
                mixrate_slow = mixRate(v,sep_b,0.02)
                mixrate_fast = 1-mixrate_slow
                if mixrate_slow==1:
                    X_out[ch_c::ch][j] = Xs[ch_c::ch][buf_slow_st+cpcnt]
                elif mixrate_fast==1:
                    X_out[ch_c::ch][j] = Xf[ch_c::ch][buf_fast_st + cpcnt]
                else:
                    X_out[ch_c::ch][j] = int(mixrate_slow * Xs[ch_c::ch][buf_slow_st+cpcnt] + mixrate_fast * Xf[ch_c::ch][buf_fast_st + cpcnt])
            cpcnt+=1        
    buf_st=buf_en
    cnt += 1
w = wave.Wave_write(output)
p = (ch,2,fr,len(X_out),'NONE','not compressed')
w.setparams(p)
w.writeframes(X_out)
w.close()