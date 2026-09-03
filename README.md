# DNS-handshake

A minimal DNS resolver written in pure Python — no `dnspython`, no `socket.gethostbyname`.
It builds a DNS query packet byte by byte, sends it over UDP to a public resolver, and
parses the raw binary response to extract the IPv4 address.

Built to understand what actually happens on the wire when a hostname is resolved.

## How it works

1. **Build the header** — a 12-byte struct: transaction ID, flags (`0x0100`, recursion
   desired), and the four section counts.
2. **Encode the question** — the hostname is converted to DNS label format, where each
   label is prefixed with its length and the name is terminated by a null byte
   (`google.com` → `\x06google\x03com\x00`), followed by QTYPE `A` and QCLASS `IN`.
3. **Send over UDP** — the query is sent to `8.8.8.8:53` with a 5-second timeout.
4. **Parse the response** — the header is unpacked and validated (transaction ID match,
   RCODE check), the question section is skipped, and each answer record is walked to
   find an `A` record whose 4-byte RDATA is formatted as a dotted-quad IP.

Message compression pointers (the `0xC0` prefix) are handled when skipping names.

## Usage

Requires Python 3.6+ and no external dependencies.

```bash
python dns_client.py
```

```
google.com → 142.250.183.174
```

To resolve a different host, use the `resolve` function directly:

```python
from dns_client import resolve

print(resolve("github.com"))
```

## API

| Function | Description |
| --- | --- |
| `converter(hostname)` | Encodes a hostname into DNS label format. |
| `build_header(transaction_id)` | Packs the 12-byte DNS header for a standard query. |
| `skip_name(data, offset)` | Advances past a name field, handling compression pointers. |
| `resolve(hostname)` | Performs the full query and returns the first `A` record as a string. |

## Errors

`resolve` raises `ValueError` on an empty hostname, a label longer than 63 bytes, a
transaction ID mismatch, a non-zero RCODE (including NXDOMAIN), or a response containing
no `A` record. A `socket.timeout` is raised if the resolver does not reply within 5 seconds.

## Limitations

- IPv4 (`A` records) only — no `AAAA`, `MX`, `CNAME`, or `TXT` support.
- UDP only, with no TCP fallback for truncated responses.
- The resolver address is hardcoded to Google Public DNS.
