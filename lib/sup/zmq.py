# -*- coding: utf-8 -*-

def split_frames(frames) -> tuple:
    '''Splits zmq ROUTER frames to base and message.'''
    base = []
    nfn = 0
    for frame in frames:
        nfn += 1
        base.append(frame)
        if frame == b'':
            break
    msg = frames[nfn:]
    return base, msg
