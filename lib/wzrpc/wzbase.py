# -*- coding: utf-8 -*-
# -*- mode: python -*-
from . import *

class WZBase(object):
    def make_error_msg(self, iden, status):
        msg = []
        if iden:
            msg.extend(iden)
            msg.append(b'')
        msg.append(header_struct.pack(wzstart, wzversion, msgtype.err))
        msg.append(error_struct.pack(status))
        return msg

    def parse_msg(self, iden, msg):
        if len(msg) == 0 or not msg[0].startswith(wzstart):
            raise WZENoWZ('Not a WZRPC message {0} from {1}'.format(msg, repr(iden)))
        try:
            hsize = header_struct.size # locals are faster
            wz, ver, type_ = header_struct.unpack(msg[0][:hsize])
        except Exception as e:
            raise
        if int(ver) != wzversion:
            raise WZEWrongVersion(iden, 'Wrong message version')
        if type_ == msgtype.req:
            unpacked = []
            for v in req_struct.unpack(msg[0][hsize:]):
                if type(v) == bytes:
                    v = v.partition(b'\0')[0]
                unpacked.append(v)
            return self._parse_req(iden, msg, *unpacked)
        elif type_ == msgtype.rep:
            unpacked = rep_struct.unpack(msg[0][hsize:])
            return self._parse_rep(iden, msg, *unpacked)
        elif type_ == msgtype.sig:
            unpacked = []
            for v in sig_struct.unpack(msg[0][hsize:]):
                if type(v) == bytes:
                    v = v.partition(b'\0')[0]
                unpacked.append(v)
            return self._parse_sig(iden, msg, *unpacked)
        elif type_ == msgtype.err:
            unpacked = error_struct.unpack(msg[0][hsize:])
            return self._parse_err(iden, msg, *unpacked)
        elif type_ == msgtype.nil:
            return self._handle_nil(iden, msg)
        else:
            raise WZEUnknownType(iden, 'Unknown message type')
        
    def parse_router_msg(self, frames):
        base, msg = split_frames(frames)
        return self.parse_msg(base[:-1], msg)
