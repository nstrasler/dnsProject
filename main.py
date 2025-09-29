from dnslib import DNSRecord, DNSHeader, DNSBuffer, DNSQuestion, RR, QTYPE, RCODE, A
from socket import socket, SOCK_DGRAM, AF_INET
import formatInput
from QueryObj import get_dns_record
import resolution

ROOT_SERVER = "199.7.83.42"  # ICANN Root Server

if __name__ == '__main__':

    cacheDict = {}
    sock = socket(AF_INET, SOCK_DGRAM)

    while True:
        command = "ROOT"

        url = input("type your url please: ")
        if url == "exit":
            quit(0)
        print(url)

        while command == "CNAME" or "ROOT":

            urlArray = formatInput.formatInput(url)

            for var in (reversed(urlArray)): #TODO Fix to just check if whole string cached
                if var in cacheDict:
                    cacheResult = cacheDict[var]
                    break

            if not urlArray[0] in cacheDict:
                try:
                    record = get_dns_record(sock, urlArray[0],ROOT_SERVER,"NS")
                    #cacheDict[urlArray[0]] = record

                    print(record.auth[0].rdata)
                except:
                    print("Error in getting dns record")
            else:
                record = cacheDict[url] #TODO fix cache logic
            counter = 0 #for timeout error to increment server
            while True:
                if not str(record.auth[counter].rdata) in cacheDict:
                    try:
                        record = get_dns_record(sock, urlArray[1], str(record.auth[counter].rdata), "NS")
                        print(record.auth[0].rdata)
                    except:
                        print("Error in getting TLD record trying next record")
                        counter = counter + 1
                        continue
                else:
                    record = cacheDict[str(record.auth[counter].rdata)]

                counter = 0
                while True:
                    if not str(record.auth[counter].rdata) in cacheDict:
                        try:
                            record = get_dns_record(sock, url, str(record.auth[counter].rdata), "A")

                        except:
                            print("Error in getting IP from TLD server trying next server")
                            counter = counter + 1
                            continue
                    else:
                        record = cacheDict[str(record.auth[counter].rdata)]

                    if record.auth[0].rtype == 2: #TODO work on logic for command looping
                        command = "NS"
                    elif record.rr[0].rtype == 1: #A TYPE or AAAA TYPE #TODO rr not always present if auth NS reponse
                        print(record.rr[0].rdata)
                        command = "A"
                        break
                    elif record.rr[0].rtype == 5: #CNAME
                        command = "CNAME"
                        url = str(record.rr[0].rdata)
                        print(url)
                        break
                    else:
                        command = "ROOT"


                break







                        #cache if successful







                #for rr in record.rr:
                   # if rr.rtype == QTYPE.A:
                   #     print(str(rr.rdata))
                  #      break

                #if record.auth:
                #    print(record.auth[0].rdata)


    sock.close()