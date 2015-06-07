# -*- coding: utf-8 -*-
# -*- mode: python -*-
import struct, hashlib, random
from sup.zmq import split_frames
from pybimaps import BijectiveSetMap, BijectiveSetSetMap, BijectiveListSetMap

wzstart = b'WZ'
wzversion = 4
header_struct = struct.Struct('!2sHB') # WZ, version, request type
req_struct = struct.Struct('!Q16s32s') # Reqid, interface, method
rep_struct = struct.Struct('!QQH') # Reqid, seqid, status
sig_struct = struct.Struct('!16s32s') # Interface, Method
error_struct = struct.Struct('!H') # Status

class msgtype:
    nil = 0
    req = 1
    rep = 2
    sig = 3
    err = 4
    ping = 6
    pong = 9

class status:
    success = 0
    error = 1
    e_wrong_version = 2
    e_unknown_type = 3
    e_no_handler = 4
    e_no_route = 5
    e_reqid_conflict = 6
    e_seqid_conflict = 7
    e_req_denied = 8 # merge with e_sig_denied?
    e_sig_denied = 9
    e_auth_wrong_hash = 10
    e_timeout = 255

status_names = {
    0: 'success',
    1: 'error',
    2: 'e_wrong_version',
    3: 'e_unknown_type',
    4: 'e_no_handler',
    5: 'e_no_route',
    6: 'e_reqid_conflict',
    7: 'e_seqid_conflict',
    8: 'e_req_denied',
    9: 'e_sig_denied',
    10: 'e_auth_wrong_hash',
    255: 'e_timeout',
}
route_type_names = {
    0: 'null',
    1: 'exclusive',
    2: 'random',
    3: 'roundrobin',
}
def name_status(val):
    return str(val)+': '+status_names.get(val, 'unknown')

def name_route_type(val):
    return str(val)+': '+route_type_names.get(val, 'unknown')

class routetype:
    max_type = 3
    null = 0
    exclusive = 1
    random = 2
    roundrobin = 3
    
class RequestState:
    def __init__(self, fun):
        self.finished = False
        self.retry = False
        self.fun = fun
            
    def accept(self, reqid, seqnum, status, data):
        if seqnum == 0:
            self.finished = True
        self.fun(self, reqid, seqnum, status, data)

class WZError(Exception): pass
class WZENoWZ(WZError): pass
class WZErrorRep(WZError): pass

class WZCommonErrorRep(WZErrorRep):
    status = status.error
    def __init__(self, iden, *args, **kvargs):
        self.rep_msg = make_common_error_msg(iden, self.status)
        super().__init__(*args, **kvargs)

class WZEWrongVersion(WZCommonErrorRep):
    status = status.e_wrong_version
class WZEUnknownType(WZCommonErrorRep):
    status = status.e_unknown_type
class WZENoHandler(WZCommonErrorRep):
    status = status.e_no_handler
class WZENoRoute(WZCommonErrorRep):
    status = status.e_no_route
class WZESeqidConflict(WZCommonErrorRep):
    status = status.e_seqid_conflict
class WZESigDenied(WZCommonErrorRep):
    status = status.e_sig_denied

class WZReqErrorRep(WZErrorRep):
    status = status.error
    def __init__(self, iden, reqid, *args, **kvargs):
        self.rep_msg = make_req_error_msg(iden, reqid, self.status)
        super().__init__(*args, **kvargs)

class WZENoReqHandler(WZReqErrorRep):
    status = status.e_no_handler
class WZENoReqRoute(WZReqErrorRep):
    status = status.e_no_route
class WZEReqidConflict(WZReqErrorRep):
    status = status.e_seqid_conflict
class WZEReqDenied(WZReqErrorRep):
    status = status.e_req_denied
class WZEAuthWrongHash(WZReqErrorRep):
    status = status.e_auth_wrong_hash

def make_auth_hash(interface, method, reqid, key):
    h = hashlib.new('sha256')
    h.update(interface)
    h.update(method)
    h.update(struct.pack('!Q', reqid))
    h.update(key)
    return h.digest()

def make_common_error_msg(iden, status):
    msg = []
    if iden:
        msg.extend(iden)
        msg.append(b'')
    header = header_struct.pack(wzstart, wzversion, msgtype.err)
    header += error_struct.pack(status)
    msg.append(header)
    return msg

def make_req_error_msg(iden, reqid, status):
    msg = []
    if iden:
        msg.extend(iden)
        msg.append(b'')
    header = header_struct.pack(wzstart, wzversion, msgtype.rep)
    header += rep_struct.pack(reqid, 0, status)
    msg.append(header)
    return msg

def make_nil_msg():
    header = header_struct.pack(wzstart, wzversion, msgtype.nil)
    msg = [header]
    return msg
    
def make_req_msg(interface, method, args, reqid):
    header = header_struct.pack(wzstart, wzversion, msgtype.req)
    header += req_struct.pack(reqid, interface, method)
    msg = [header]
    msg.extend(args)
    return msg
    
def make_rep_msg(reqid, seqnum, status, answer):
    header = header_struct.pack(wzstart, wzversion, msgtype.rep)
    header += rep_struct.pack(reqid, seqnum, status)
    msg = [header]
    msg.extend(answer)
    return msg
    
def make_sig_msg(interface, method, args):
    header = header_struct.pack(wzstart, wzversion, msgtype.sig)
    header += sig_struct.pack(interface, method)
    msg = [header]
    msg.extend(args)
    return msg
