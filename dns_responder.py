#dependency : pip install scapy 
from scapy.all import *
DNSServerIP="172.16.20.40"
filter="udp port 53 and ip dst "+DNSServerIP+" and not ip src "+DNSServerIP 

def DNS_Responder(localIP):

    def forwardDNS(orig_pkt):
        print "Forwarding :"+ orig_pkt[DNSQR].qname 
	response = sr1(IP(dst="8.8.8.8")/UDP(sport=orig_pkt[UDP].sport)/ \
		DNS(rd=1,id=orig_pkt[DNS].id,qd = DNSQR(qname=orig_pkt[DNSQR].qname)),verbose=0)
	respPkt = IP(dst=orig_pkt[IP].src)/UDP(dport=orig_pkt[UDP].sport)/DNS()
	respPkt[DNS]=response[DNS]
	send(respPkt,verbose=0)
	return "Responding: "+ respPkt.summary()

    def getResponse(pkt):
	if (DNS in pkt and pkt[DNS].opcode==0L and pkt[DNS].ancount==0 and pkt[IP].src!=localIP):
	    if "trailers.apple.com" in pkt['DNS Question Record'].qname:
		spfResp = IP(dst = pkt[IP].src)\
		    /UDP(dport=pkt[UDP].sport,sport=53)\
		    /DNS(id=pkt[DNS].id,ancount=1,an=DNSRR(rrname=pkt[DNSQR].qname,rdata=localIP)\
	            /DNSRR(rrname="trailers.apple.com",rdata=localIP))
		send(spfResp,verbose=0)
	        return "Spoofed DNS Response Sent"
	    else:
	        return forwardDNS(pkt)
	else:
	    return False
	return getResponse

sniff(filter=filter, prn=DNS_Responder(DNSServerIP))



