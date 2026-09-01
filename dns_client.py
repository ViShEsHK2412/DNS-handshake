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



hostname = "google.com"
# 1. Build the DNS header
trans_id = 0x1234
flags = 0x0100       # Standard query + recursion desired
qd_count = 1
ans_count = 0
ns_count = 0
ar_count = 0

dns_header = struct.pack(
    "!HHHHHH",
    trans_id,
    flags,
    qd_count,
    ans_count,
    ns_count,
    ar_count
)

# 2. Build QNAME
qname = converter(hostname)

# 2. Build QNAME
qname = converter(hostname)

# 3. Build QTYPE and QCLASS
qtype = struct.pack("!H", 1)    # A record
qclass = struct.pack("!H", 1)   # IN (Internet)

# 4. Assemble the complete DNS query
query = dns_header + qname + qtype + qclass

print("DNS Query:")
print(query.hex())

# 5. Send query over UDP
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.settimeout(5)

    sock.sendto(
        query,
        ("8.8.8.8", 53)
    )

    # 6. Receive DNS response
    response, address = sock.recvfrom(4096)

print("\nResponse received from:", address)
print("Response length:", len(response))
print("Response:")
print(response.hex())

# 7. Check transaction ID
response_trans_id = struct.unpack("!H", response[:2])[0]

print("\nRequest Transaction ID:", hex(trans_id))
print("Response Transaction ID:", hex(response_trans_id))

if response_trans_id != trans_id:
    raise ValueError("Transaction ID mismatch!")

print("Transaction ID matched!")


