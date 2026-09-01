import socket , struct

with socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
) as server:

    server.sendto(
        b"hello",
        ("localhost", 8000)
    )



def converter(hostname: str) -> bytes:
    if(hostname == ""):
        print("Invalid")
        raise ValueError("Hostname cannot be empty")
    if hostname.endswith('.'):
        hostname = hostname.rstrip('.') 
    var = hostname.split(".")
    converted = b""
    for values in var:
        byteval = values.encode("utf-8")
        length = len(byteval)
        if length > 63:
            raise ValueError("Length Greater than 63")
        converted = converted + bytes([length]) + byteval

    converted = converted + b"\x00"

    return converted


def header(transId: int , flags : int , qdCount : int , ansCount : str , nsCount : int , arCount : int) -> bytes:
    header = struct.pack("!HHHHHH",transId,flags,qdCount,ansCount,nsCount,arCount)

    print(f" The length of the header is: {len(header)} , and the hex value is : {header.hex()}")

    round = struct.unpack("!HHHHHH" , header)

    print(f"The round trip final ans is : {round}")

header(0x1234,0x0100 , 1 , 0 , 0 , 0 )




