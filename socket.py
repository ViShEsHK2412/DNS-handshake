import socket

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


print(converter("ww.google.com."))