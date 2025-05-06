import sys
from scapy.all import IP, UDP, DNS, DNSQR, sr1

DNS_PORT = 53
DNS_SERVER_IP = "8.8.8.8"
WORDLIST_FILE = 'WordList_TLAs.txt'

def read_file_content(filename):
    """Read and return the content of a file, stripped of whitespace."""
    with open(filename, 'r') as file:
        return [line.strip() for line in file]

def send_dns_query(dest, domain, query_type):
    """
    Send a DNS query and return the response.

    Args:
        dest: Destination IP address for the DNS query.
        domain: Domain name to resolve.
        query_type: Type of DNS query (e.g., 'A', 'AAAA', 'SOA').

        
    Returns:
        DNS response or None if no response received.
    """
    dns_packet = IP(dst=dest) / UDP(dport=DNS_PORT) / DNS(qd=DNSQR(qname=domain, qtype=query_type))
    response = sr1(dns_packet, timeout=2, verbose=False)
    return response.getlayer(DNS) if response and response.haslayer(DNS) else None

def get_soa_record(domain):
    """Get the SOA record for a domain and return the primary DNS server."""
    dns_response = send_dns_query(DNS_SERVER_IP, domain, 'SOA')
    if dns_response and dns_response.an:
        return dns_response.an.mname.decode('utf-8')
    print(f"SOA record for {domain} does not exist.")
    return None

def get_a_records(dns_server, subdomain):
    """Get A records for a subdomain."""
    dns_response = send_dns_query(dns_server, subdomain, 'A')
    if dns_response and dns_response.an:
        return [answer.rdata for answer in dns_response.an if answer.type == 1]
    return []

def main():
    if len(sys.argv) != 2:
        print("Usage: python dns_query.py <DOMAIN_NAME>")
        sys.exit(1)

    domain_name = sys.argv[1]
    main_dns_server = get_soa_record(domain_name)
    if not main_dns_server:
        return

    print(f"SOA record for {domain_name}:")
    print(f"Primary DNS server: {main_dns_server}")

    subdomains = read_file_content(WORDLIST_FILE)
    try:
        for subdomain in subdomains:
            full_domain = f"{subdomain}.{domain_name}"
            try:
                addresses = get_a_records(main_dns_server, full_domain)
                if addresses:
                    print(f"{full_domain}: {addresses}")
            except Exception as e:
                print(f"Error querying {full_domain}: {str(e)}")
    except KeyboardInterrupt:
        print("\nExiting program...")
        sys.exit(0)

if __name__ == "__main__":
    main()