import socket
import struct


def converter(hostname: str) -> bytes:

    if not hostname:
        raise ValueError("Hostname cannot be empty")

    if hostname.endswith("."):
        hostname = hostname[:-1]

    converted = b""

    for label in hostname.split("."):

        label_bytes = label.encode("utf-8")

        if len(label_bytes) > 63:
            raise ValueError("Label is longer than 63 bytes")

        converted += bytes([len(label_bytes)])
        converted += label_bytes

    converted += b"\x00"

    return converted


def build_header(transaction_id: int) -> bytes:

    flags = 0x0100
    qd_count = 1
    an_count = 0
    ns_count = 0
    ar_count = 0

    return struct.pack(
        "!HHHHHH",
        transaction_id,
        flags,
        qd_count,
        an_count,
        ns_count,
        ar_count
    )


def skip_name(data: bytes, offset: int) -> int:

    while True:

        length = data[offset]

        if length & 0xC0 == 0xC0:
            return offset + 2

        if length == 0:
            return offset + 1

        offset += 1 + length


def resolve(hostname: str) -> str:

    transaction_id = 0x1234

    dns_header = build_header(transaction_id)

    qname = converter(hostname)

    qtype = struct.pack("!H", 1)
    qclass = struct.pack("!H", 1)

    query = dns_header + qname + qtype + qclass

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    ) as sock:

        sock.settimeout(5)

        sock.sendto(
            query,
            ("8.8.8.8", 53)
        )

        response, address = sock.recvfrom(4096)

    (
        response_id,
        flags,
        qd_count,
        an_count,
        ns_count,
        ar_count
    ) = struct.unpack(
        "!HHHHHH",
        response[:12]
    )

    if response_id != transaction_id:
        raise ValueError("Transaction ID mismatch")

    rcode = flags & 0x000F

    if rcode == 3:
        raise ValueError("Domain does not exist")

    if rcode != 0:
        raise ValueError(f"DNS error: RCODE {rcode}")

    offset = 12

    offset = skip_name(response, offset)

    offset += 4

    for _ in range(an_count):

        offset = skip_name(response, offset)

        record_type = struct.unpack(
            "!H",
            response[offset:offset + 2]
        )[0]

        offset += 2

        record_class = struct.unpack(
            "!H",
            response[offset:offset + 2]
        )[0]

        offset += 2

        ttl = struct.unpack(
            "!I",
            response[offset:offset + 4]
        )[0]

        offset += 4

        data_length = struct.unpack(
            "!H",
            response[offset:offset + 2]
        )[0]

        offset += 2

        data = response[
            offset:offset + data_length
        ]

        offset += data_length

        if record_type == 1 and data_length == 4:

            ip = ".".join(
                str(byte)
                for byte in data
            )

            return ip

    raise ValueError("No A record found")


hostname = "google.com"

ip = resolve(hostname)

print(f"{hostname} → {ip}")
