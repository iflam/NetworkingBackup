from construct import Struct, Bytes

Ethernet = Struct(
        'mac_src' / Bytes(6),
        'mac_dest' / Bytes(6)
        )
