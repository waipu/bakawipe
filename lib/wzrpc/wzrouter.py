# -*- coding: utf-8 -*-
# -*- mode: python -*-
from . import *
from .wzbase import WZBase

class WZRouter(WZBase):
    def __init__(self):
        self.req_routes = BijectiveListSetMap()
        self.req_route_types = {}
        self.sig_routes = BijectiveSetSetMap()
        self.iden_reqid_map = BijectiveSetMap()
    
    def add_req_route(self, interface, method, iden):
        self.req_routes.append_value((interface, method), iden)

    def set_req_routes(self, interface, method, idens):
        self.req_routes.set_values((interface, method), idens)

    def get_req_routes(self, interface, method):
        return self.req_routes.get_values((interface, method))
        
    def del_req_route(self, interface, method, iden):
        self.req_routes.del_value((interface, method), iden)
    
    def clear_req_routes_for_iden(self, iden):
        return self.req_routes.clear_keys(iden)

    def get_req_routes_for_iden(self, iden):
        return self.req_routes.get_keys(iden)

    def check_req_route(self, interface, method, iden):
        try:
            return iden in self.req_routes.get_values((interface, method))
        except KeyError:
            return False
    
    def set_req_route_type(self, interface, method, type_):
        self.req_route_types[interface, method] = type_

    def get_req_route_type(self, interface, method):
        return self.req_route_types.get((interface, method), None) # or random instead
    
    def add_sig_route(self, interface, method, iden):
        self.sig_routes.add_value((interface, method), iden)

    def set_sig_routes(self, interface, method, idens):
        self.sig_routes.set_values((interface, method), idens)
    
    def del_sig_route(self, interface, method, iden):
        self.sig_routes.del_value((interface, method), iden)

    def clear_sig_routes_for_iden(self, iden):
        return self.sig_routes.clear_keys(iden)

    def clear_all_routes_for_iden(self, iden):
        try:
            self.clear_req_routes_for_iden(iden)
        except KeyError:
            pass
        try:
            self.clear_sig_routes_for_iden(iden)
        except KeyError:
            pass

    def _parse_req(self, iden, msg, reqid, interface, method):
        try:
            routes = self.req_routes[(interface, method)]
        except KeyError:
            try:
                routes = self.req_routes[(interface, None)]
            except KeyError:
                raise WZENoReqRoute(iden, reqid,
                                    'No req route for %s,%s'%(interface, method))
        if len(routes) == 0:
            raise WZENoReqRoute(iden, reqid,
                                'No req route for %s,%s'%(interface, method))
        type_ = self.req_route_types.get((interface, method),
                                             routetype.random)
        if type_ == routetype.null:
            yield
        elif type_ == routetype.exclusive:
            route = routes[0]
        elif type_ == routetype.random:
            route = routes[random.randint(0, len(routes)-1)]
        elif type_ == routetype.roundrobin: # Yeah, roundrobin. Later.
            route = routes[random.randint(0, len(routes)-1)]
        else:
            yield
        self.iden_reqid_map.add_value(tuple(iden), reqid)
        newmsg = list(route)
        newmsg.extend(iden)
        newmsg.append(b'')
        newmsg.extend(msg)
        yield newmsg
        
    def _parse_rep(self, iden, msg, reqid, seqnum, status):
        # try:
        #     route = self.iden_reqid_map.get_key(reqid)
        #     if seqnum == 0:
        #         self.iden_reqid_map.del_value(route, reqid)
        # except KeyError:
        #     raise WZENoRoute(iden, 'No rep route for reqid')
        newmsg = list(iden)
        newmsg.pop(0)
        newmsg.append(b'')
        newmsg.extend(msg)
        yield newmsg

    def _parse_sig(self, iden, msg, interface, method):
        try:
            routes = self.sig_routes[(interface, method)]
        except (KeyError, IndexError):
            try:
                routes = self.sig_routes[(interface, None)]
            except (KeyError, IndexError):
                raise WZENoRoute(iden, 'No sig route for %s,%s'%(interface, method))
        msgs = []
        for route in routes:
            newmsg = list(route)
            newmsg.append(b'')
            newmsg.extend(msg)
            yield newmsg

    def _parse_err(self, iden, msg, status):
        pass

    def _handle_nil(self, iden, msg):
        pass
