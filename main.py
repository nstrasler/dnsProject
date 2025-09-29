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
        for var in (reversed(urlArray)):
            if var in cacheDict:
                cacheResult = cacheDict[var]
                break


        #or var for unresponsive name servers
        #initialRecord = get_dns_record(sock, "gvsu.edu", ROOT_SERVER, "A")

        while True:
            rootReturn = ""
            if not cacheResult or cacheResult[1] != "ROOT":
                record = get_dns_record(sock, urlArray[0],ROOT_SERVER,"NS")             #TODO errorno check
                cacheDict.setdefault(urlArray[0], [record.auth[0].rdata]).append("ROOT") #cache as ROOT if succesful
                rootReturn = record.auth[0].rdata
            else:
                rootReturn = cacheResult[0]

            counter = 0
            while True:
                if not cacheResult or cacheResult[1] != "TLD":
                    record = get_dns_record(sock, urlArray[1], rootReturn, "NS")






                        #cache if successful







                #for rr in record.rr:
                   # if rr.rtype == QTYPE.A:
                   #     print(str(rr.rdata))
                  #      break

                #if record.auth:
                #    print(record.auth[0].rdata)


    sock.close()