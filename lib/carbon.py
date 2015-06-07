import socket, time, pickle, struct

'''see http://graphite.readthedocs.org/en/1.0/feeding-carbon.html'''

def udp_packet(addr, data):
    '''Wrapper function over socket api'''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.sendto(data, addr)
    finally:
        s.close()

def send_data(addr, name, value, timestamp=None):
    '''Send plaintext data.'''
    msg = ' '.join((name, str(value), str(timestamp or int(time.time()))))
    return udp_packet(addr, msg)

def send_data_piclke(addr, listOfMetricTuples, pickle_p=pickle.HIGHEST_PROTOCOL):
    '''Send pickled data.'''
    pld = pickle.dumps(listOfMetricTuples, pickle_p)
    msg = ''.join((struct.pack("!L", len(pld)), pld))
    return udp_packet(addr, msg)
