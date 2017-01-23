import struct, socket


def unpack_address(u):
    addrtype = u.unpack_uint()

    if addrtype == 1:
        address = u.unpack_fopaque(4)

    if addrtype == 2:
        address = u.unpack_fopaque(16)
    
    return address

class IPv4Address(object):
    def __init__(self, addr_int):
        self.addr_int = addr_int
        self.na = struct.pack(b'!L', addr_int)
    
    def __str__(self):
        return socket.inet_ntoa(self.na)

    def asString(self):
        return str(self)

    def __repr__(self):
        return "<IPv4Address ip=\"%s\">" % str(self)
