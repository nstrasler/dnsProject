from dnslib import DNSRecord, DNSHeader, DNSBuffer, DNSQuestion, RR, QTYPE, RCODE
from socket import socket, SOCK_DGRAM, AF_INET

ROOT_SERVER = "199.7.83.42"  # ICANN Root Server
DNS_PORT = 53

def get_dns_record(udp_socket, domain: str, parent_server: str, record_type):

    q = DNSRecord.question(domain, qtype=record_type)
    q.header.rd = 0  # Recursion Desired?  NO
    #print("DNS query", repr(q))
    udp_socket.sendto(q.pack(), (parent_server, DNS_PORT))
    pkt, _ = udp_socket.recvfrom(8192)
    buff = DNSRecord.parse(pkt)
    """
    The top level format of DNS message is divided into five sections:
    1. Header
    2. Question
    3. Answer
    4. Authority
    5. Additional
    """
    return buff

if __name__ == '__main__':
    sock = socket(AF_INET, SOCK_DGRAM)
    temp = get_dns_record(sock, "gvsu.edu", ROOT_SERVER, "A")
    print(temp.auth)
    sock.close()