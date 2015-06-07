# -*- coding: utf-8 -*-
# -*- mode: python -*-
from . import *
from .wzbase import WZBase

class WZAuth(WZBase):
    def __init__(self, child):
        self.req_auth_map = BijectiveSetSetMap()
        self.req_auth_excluded_set = set()
        self.sig_auth_map = BijectiveSetSetMap()
        self.child = child

    def add_req_auth_exclusion(self, interface, method):
        self.req_auth_excluded_set.add((interface, method))

    def del_req_auth_exclusion(self, interface, method):
        self.req_auth_excluded_set.discard((interface, method))

    def add_req_auth_record(self, interface, method, iden):
        self.req_auth_map.add_value((interface, method), iden)
    
    def del_req_auth_record(self, interface, method, iden):
        self.req_auth_map.del_value((interface, method), iden)
        
    def set_req_auth_records(self, interface, method, idens):
        self.req_auth_map.set_values((interface, method), idens)

    def get_req_auth_records(self, interface, method, iden):
        self.req_auth_map.get_values((interface, method))
    
    def clear_req_auth_records(self, interface, method):
        self.req_auth_map.clear_values((interface, method))
    
    def check_req_auth_record(self, interface, method, iden):
        try:
            return iden in self.req_auth_map.get_values((interface, method))
        except KeyError:
            return False
    
    def add_sig_auth_record(self, interface, method, iden):
        self.sig_auth_map.add_value((interface, method), iden)
    
    def del_sig_auth_record(self, interface, method, iden):
        self.sig_auth_map.del_value((interface, method), iden)

    def set_sig_auth_records(self, interface, method, idens):
        self.sig_auth_map.set_values((interface, method), idens)

    def clear_sig_auth_records(self, interface, method):
        self.sig_auth_map.clear_values((interface, method))

    def check_sig_auth_record(self, interface, method, iden):
        try:
            return iden in self.sig_auth_map.get_values((interface, method))
        except KeyError:
            return False

    def clear_all_auth_records_for_iden(self, iden):
        try:
            self.req_auth_map.clear_keys(iden)
        except KeyError:
            pass
        try:
            self.sig_auth_map.clear_keys(iden)
        except KeyError:
            pass
    
    def _parse_req(self, iden, msg, reqid, interface, method):
        success = False
        try:
            if tuple(iden) in self.req_auth_map[(interface, method)]:
                success = True
        except KeyError:
            if (interface, method) in self.req_auth_excluded_set:
                success = True
        if not success:
            try:
                if tuple(iden) in self.req_auth_map[(interface, b'')]:
                    success = True
            except KeyError:
                pass
        if not success:
            raise WZEReqDenied(iden, reqid,
                               'No auth record for %s,%s'%(interface, method))
        return self.child._parse_req(iden, msg, reqid, interface, method)
    
    def _parse_rep(self, iden, msg, reqid, seqnum, status):
        return self.child._parse_rep(iden, msg, reqid, seqnum, status)
    
    def _parse_sig(self, iden, msg, interface, method):
        success = False
        try:
            if tuple(iden) in self.sig_auth_map[(interface, method)]:
                success = True
        except KeyError:
            pass
        if not success:
            try:
                if tuple(iden) in self.sig_auth_map[(interface, b'')]:
                    success = True
            except KeyError:
                pass
        if not success:
            raise WZESigDenied(iden, 'No auth record for %s,%s'%(interface, method))
        return self.child._parse_sig(iden, msg, interface, method)
    
    def _parse_err(self, iden, msg, status):
        self.child._parse_err(iden, msg, status)
