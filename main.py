from dnslib import DNSRecord, DNSHeader, DNSBuffer, DNSQuestion, RR, QTYPE, RCODE, A
from socket import socket, SOCK_DGRAM, AF_INET
import formatInput
from QueryObj import get_dns_record
import resolution

ROOT_SERVER = "199.7.83.42"  # ICANN Root Server

if __name__ == '__main__':

    cacheDict = {}
    sock = socket(AF_INET, SOCK_DGRAM)
    cont = True

    while True:
        url = input("type your url please: ")
        if url == "exit":
            quit(0)
        print(url)
        urlArray = formatInput.formatInput(url)     #splits into array of edu, gvsu.edu, www.gvsu.edu
        #record = get_dns_record(sock, "gvsu.edu", 'joselyn.ns.cloudflare.com.', "A")
        cacheResult = []
        for var in (reversed(urlArray)): #TODO Fix to just check if whole string cached
            if var in cacheDict:
                cacheResult = cacheDict[var]
                break


        #or var for unresponsive name servers
        #initialRecord = get_dns_record(sock, "gvsu.edu", ROOT_SERVER, "A")

        while True:
            if not url in cacheDict:
                try:
                    record = get_dns_record(sock, urlArray[0],ROOT_SERVER,"NS")
                    cacheDict[url] = record

                    print(record.auth[0].rdata)
                except:
                    print("Error in getting dns record")
            else:
                record = cacheDict[url]
            counter = 0 #for timeout error to increment server
            while True:
                if not urlArray[1] in cacheDict: #TODO fix double check cache logic
                    try:
                        record = get_dns_record(sock, urlArray[1], str(record.auth[counter].rdata), "NS")
                        print(record.auth[0].rdata)
                    except:
                        print("Error in getting TLD record")
                        counter = counter + 1
                else:
                    record = cacheDict[urlArray[1]]









                        #cache if successful







                #for rr in record.rr:
                   # if rr.rtype == QTYPE.A:
                   #     print(str(rr.rdata))
                  #      break

                #if record.auth:
                #    print(record.auth[0].rdata)


    sock.close()