#Abraham Soclof 
#674098915
#Lab 8
#SYNFlood.py

from scapy.all import rdpcap, IP, TCP
from collections import defaultdict, Counter
import ipaddress

THRESHOLD = 5

def compare_files(file1, file2):
    """Returns a set of IP addresses that are in file2 but not in file1."""
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        set1 = set(line.strip() for line in f1)
        set2 = set(line.strip() for line in f2)
    return set2 - set1

def read_pcap_file(pcap_file):
    """Reads a pcap file and returns a list of packets."""
    return rdpcap(pcap_file)

def analyze_packets(packets):
    """
    Analyzes packets to count SYN and ACK flags, and calculate packet sending rate.
    
    Parameters:
    packets: A list of packets to be analyzed.
    """
    
    # Initialize a dictionary to store counts of SYN and ACK flags, last packet time, and packet sending rate for each source IP
    ip_counts = defaultdict(lambda: {'syn': 0, 'ack': 0, 'last_time': None, 'rate': 0})
    
    # Initialize a Counter to count packets per destination IP
    dst_ip_counter = Counter()

    # Loop through the packets
    for pkt in packets:
        # Check if the packet has an IP layer and a TCP layer
        if pkt.haslayer(IP) and pkt.haslayer(TCP):
            # Get the IP and TCP layers
            ip_layer = pkt[IP]
            tcp_layer = pkt[TCP]
            
            # Get the packet's timestamp
            current_time = float(pkt.time)

            # Increment the count for the destination IP
            dst_ip_counter[ip_layer.dst] += 1

            # If the SYN flag is set, increment the SYN count for the source IP
            if tcp_layer.flags & 2:  # SYN flag
                ip_counts[ip_layer.src]['syn'] += 1
                
            # If the ACK flag is set, increment the ACK count for the source IP
            if tcp_layer.flags & 16:  # ACK flag
                ip_counts[ip_layer.src]['ack'] += 1

            # Calculate the packet sending rate for the source IP
            # Check if a 'last_time' value exists for the source IP in the ip_counts dictionary.
            # 'last_time' represents the timestamp of the last packet that was sent by this source IP.
            if ip_counts[ip_layer.src]['last_time']:
                # If 'last_time' exists, calculate the time difference between the current packet's timestamp and the 'last_time'.
                # This gives us the time interval between the current packet and the last packet from the same source IP.
                time_diff = current_time - ip_counts[ip_layer.src]['last_time']
                
                # Check if the time difference is greater than 0.
                # If it's 0, it means the current packet and the last packet from the same source IP have the same timestamp.
                if time_diff > 0:
                    # If the time difference is greater than 0, calculate the packet sending rate as 1 / time_diff.
                    # This gives us the number of packets sent per second (packet rate) for the current time interval.
                    # Then, update the 'rate' value for the source IP in the ip_counts dictionary to be the maximum of the current 'rate' and the newly calculated rate.
                    # This way, the 'rate' value always represents the highest packet sending rate observed for each source IP.
                    ip_counts[ip_layer.src]['rate'] = max(ip_counts[ip_layer.src]['rate'], 1 / time_diff)
            
            # Update the last packet time for the source IP
            ip_counts[ip_layer.src]['last_time'] = current_time

    # Return the counts and the packet sending rates
    return ip_counts, dst_ip_counter

def identify_attacked_network(dst_ip_counter):
    """Identifies the most common destination IP and assumes its subnet as the attacked network."""
    most_common_dst = dst_ip_counter.most_common(1)[0][0]
    ip_parts = most_common_dst.split('.')
    attacked_network = f"{'.'.join(ip_parts[:2])}.0.0/16"
    return attacked_network

def identify_potential_attackers(ip_counts, threshold):
    """
    Identifies potential attackers based on SYN count, packet rate, and SYN to ACK ratio.
    
    The thresholds for SYN count, packet rate, and SYN/ACK ratio are chosen based on the 
    characteristics of a SYN flood attack:
    - SYN count > threshold: In a SYN flood attack, the attacker sends a large number of SYN packets.
      This threshold filters out IP addresses that have sent a large number of SYN packets.
    - Packet rate > 0.5: In a SYN flood attack, the attacker often sends packets at a high 
    rate to overwhelm the target system. This threshold filters out IP addresses that have 
    a high packet sending rate.
    - SYN/ACK ratio > 3: In a normal TCP connection, the number of SYN packets should be 
    roughly equal to the number of ACK packets. However, in a SYN flood attack, 
    the attacker sends a large number of SYN packets without corresponding ACK packets, 
    leading to a high SYN/ACK ratio. This threshold filters out IP addresses with a high SYN/ACK ratio.
    """
    potential_attackers = []
    for ip, data in ip_counts.items():
        syn_ack_ratio = data['syn'] / (data['ack'] + 1)  # Avoid division by zero
        if (data['syn'] > threshold and data['rate'] > 0.5 and syn_ack_ratio > 3):
            potential_attackers.append((ip, data['syn']))
    return potential_attackers

def filter_and_select_attackers(potential_attackers, attacked_network, num_attackers=100):
    """Filters and selects the top attackers, ensuring no IPs from the attacked network are included."""
    potential_attackers.sort(key=lambda x: x[1], reverse=True)
    attackers = []
    for ip, _ in potential_attackers:
        if len(attackers) >= num_attackers:
            break
        if ipaddress.ip_address(ip) not in ipaddress.ip_network(attacked_network):
            attackers.append(ip)
    if len(attackers) < num_attackers:
        additional_attackers = [ip for ip, _ in potential_attackers if ip not in attackers]
        attackers.extend(additional_attackers[:num_attackers - len(attackers)])
    return attackers

def create_attacker_file(attackers, output_file="attackers.txt"):
    """Writes the attacking IP addresses to a file."""
    with open(output_file, "w") as f:
        for attacker in attackers:
            f.write(f"{attacker}\n")
    print(f"Identified {len(attackers)} attacking IP addresses. Saved to {output_file}.")
    return output_file

def check_false_alarms(attackers, attacked_network):
    """Checks for false alarms by ensuring no IPs from the attacked network are identified as attackers."""
    false_alarms = [ip for ip in attackers if ipaddress.ip_address(ip) in ipaddress.ip_network(attacked_network)]
    if false_alarms:
        print("Warning: Some IPs from the assumed attacked network were identified as attackers:")
        for ip in false_alarms:
            print(ip)
    else:
        print("No IPs from the assumed attacked network were identified as attackers.")

def main():
    pcap_file = "SYNflood.pcapng"
    packets = read_pcap_file(pcap_file)
    ip_counts, dst_ip_counter = analyze_packets(packets)
    attacked_network = identify_attacked_network(dst_ip_counter)
    print(f"Assumed attacked network: {attacked_network}")
    potential_attackers = identify_potential_attackers(ip_counts, THRESHOLD)
    attackers = filter_and_select_attackers(potential_attackers, attacked_network)
    create_attacker_file(attackers)
    check_false_alarms(attackers, attacked_network)
    missing_ips = compare_files('attackers.txt', 'attackersListFiltered.txt')
    if missing_ips:
        print("The following IP addresses are in attackersListFiltered.txt but not in attackers.txt:")
        for ip in missing_ips:
            print(ip)
    else:
        print("All IP addresses in attackersListFiltered.txt are in attackers.txt")

if __name__ == "__main__":
    main()
