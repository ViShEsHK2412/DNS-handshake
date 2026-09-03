import socket
import struct


def converter(hostname: str) -> bytes:

    if hostname == "":
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



def header(
    transId: int,
    flags: int,
    qdCount: int,
    ansCount: int,
    nsCount: int,
    arCount: int
) -> bytes:

    dns_header = struct.pack(
        "!HHHHHH",
        transId,
        flags,
        qdCount,
        ansCount,
        nsCount,
        arCount
    )

    return dns_header



hostname = "google.com"

trans_id = 0x1234
flags = 0x0100

qd_count = 1
ans_count = 0
ns_count = 0
ar_count = 0


# Build header
dns_header = header(
    trans_id,
    flags,
    qd_count,
    ans_count,
    ns_count,
    ar_count
)


# Build QNAME
qname = converter(hostname)


# QTYPE = 1 → A record
qtype = struct.pack("!H", 1)


# QCLASS = 1 → IN (Internet)
qclass = struct.pack("!H", 1)


# Assemble complete DNS query
query = dns_header + qname + qtype + qclass


print("DNS Query:")
print(query.hex())


# Send query
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:

    sock.settimeout(5)

    sock.sendto(
        query,
        ("8.8.8.8", 53)
    )

    response, address = sock.recvfrom(4096)


print("\nResponse received from:", address)
print("Response length:", len(response))
print("Response:")
print(response.hex())

# First 12 bytes are the DNS header
header_data = response[:12]


# Convert the 12 raw bytes back into 6 integers
header_fields = struct.unpack(
    "!HHHHHH",
    header_data
)


# Give each field a meaningful name
(
    response_trans_id,
    response_flags,
    response_qd_count,
    response_an_count,
    response_ns_count,
    response_ar_count
) = header_fields



print("\n--- DNS Header ---")

print(
    "Transaction ID:",
    hex(response_trans_id)
)

print(
    "Flags:",
    hex(response_flags)
)

print(
    "QDCOUNT:",
    response_qd_count
)

print(
    "ANCOUNT:",
    response_an_count
)

print(
    "NSCOUNT:",
    response_ns_count
)

print(
    "ARCOUNT:",
    response_ar_count
)


if response_trans_id != trans_id:
    raise ValueError("Transaction ID mismatch!")

print("Transaction ID matched!")



rcode = response_flags & 0x000F

print("RCODE:", rcode)


if rcode == 0:
    print("No error")

elif rcode == 2:
    print("Server failure")

elif rcode == 3:
    print("NXDOMAIN: domain does not exist")

elif rcode == 5:
    print("Query refused")

else:
    print("Other DNS response code:", rcode)



tc = bool(response_flags & 0x0200)

print("TC:", tc)

if tc:
    print("Response is truncated")
    print("A real DNS client should retry using TCP")


ra = bool(response_flags & 0x0080)

print("RA:", ra)

if ra:
    print("Server supports recursion")



if response_an_count == 0:

    print("No answer records")

else:

    print(
        "Number of answer records:",
        response_an_count
    )

