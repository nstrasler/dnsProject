import re
from dnslib import DNSRecord, DNSHeader, DNSBuffer, DNSQuestion, RR, QTYPE, RCODE, A
from socket import socket, SOCK_DGRAM, AF_INET

cacheDict = {}
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

def formatInput(input):
    temp = input.removesuffix(".")
    parts = temp.split('.')
    result = []
    for i in range(1, len(parts) + 1):
        current_part = ".".join(parts[-i:])
        result.append(current_part)
    return result

def listCache():
    count = 1
    print("-----CACHE CONTENTS-----")

    for key in cacheDict.keys():
        if cacheDict[key].header.a and cacheDict[key].rr[0].rtype == 1:
            print(str(count) + ". <A TYPE> "+ key + " <" + str(cacheDict[key].rr[0].rdata) + ">")
            count += 1
        elif cacheDict[key].header.a and cacheDict[key].rr[0].rtype == 5:
            print(str(count) + ". <CNAME> "+ key + " <" + str(cacheDict[key].rr[0].rdata) + ">")
            count += 1
        #elif cacheDict[key].header.auth and cacheDict[key].auth[0].rtype == 2:
        #    print(str(count) + ". <NS> " + key + " <"+str(cacheDict[key].auth[0].rdata) + ">") #TODO fix access for IP format
        #    count += 1
        else:
            print(str(count) + ". <NS> " + key)
            count += 1

def deleteCacheEntry(input):
    keys = list(cacheDict.keys())
    if 0 <= input < len(keys):
        target = keys[input-1]
        del cacheDict[target]

if __name__ == '__main__':
    sock = socket(AF_INET, SOCK_DGRAM)
    command = ""

    while True:
        command = "ROOT"
        url = input("type your url please: ")

        match = re.search(r"remove (\d+)$", url)
        if url == ".exit":
            sock.close()
            quit(0)
        elif url == ".list":
            listCache()
            continue
        elif url == ".clear":
            cacheDict.clear()
            continue
        elif match:
            num = int(match.group(1))
            if num and len(cacheDict) >= num > 0:
                    deleteCacheEntry(num)
            continue


        while command == "CNAME" or command == "ROOT":
            urlArray = formatInput(url)
            if urlArray[-1] in cacheDict and len(urlArray) > 2 and cacheDict[urlArray[-1]].header.a and cacheDict[urlArray[-1]].rr[0].rtype != 5:
                record = cacheDict[urlArray[-1]]
                print("Cache hit off full url")
                for x in record.rr:
                    print(x.rdata)
                break

            #ROOT SERVER NS QUERY
            if urlArray[0] in cacheDict:
                record = cacheDict[urlArray[0]]
                print("Got TLD server from cache : " + str(record.auth[0].rdata))
            else:
                try:
                    record = get_dns_record(sock, urlArray[0],ROOT_SERVER,"NS")
                    if record.header.rcode != 0:
                        print("Error in getting TLD server")
                        break
                    else:
                        print("Got TLD server from Root DNS server : "+ str(record.auth[0].rdata))
                        cacheDict[urlArray[0]] = record
                except:
                    print("Error in getting TLD server")
                    break
            counter = 0 #for timeout/error to increment server
            #TLD NS QUERY
            while True:
                if record.header.auth and record.header.auth > counter:
                    if str(record.auth[counter].rdata) in cacheDict:
                        print("Got Authoritative server from cache : " + str(cacheDict[str(record.auth[counter].rdata)]))
                        record = cacheDict[str(record.auth[counter].rdata)]
                    else:
                        print("Trying an Authoritative server from TLD : " + str(record.auth[counter].rdata))
                        try:
                            record = get_dns_record(sock, urlArray[1], str(record.auth[counter].rdata), "NS")
                            if record.header.rcode != 0:
                                counter = counter + 1
                                print("Error returned in getting Authoritative server trying next record")
                                continue
                            else:
                                cacheDict[urlArray[1]] = record
                        except:
                            print("Failed message in getting Authoritative record from TLD trying next record")
                            counter = counter + 1
                            continue
                else:
                    print("No more Authoritative servers to check query failed")
                    command = "EXIT"
                    break
                counter = 0
                #Authoritative A QUERY
                while command != "EXIT":
                    if record.header.auth and record.header.auth > counter:
                        tempstr = str(record.auth[counter].rdata)
                        if tempstr in cacheDict and cacheDict[tempstr].header.a and cacheDict[tempstr].rr[0].rtype != 5:
                            print("Got NS server from cache : " + tempstr)
                            record = cacheDict[str(record.auth[counter].rdata)]
                        else:
                            print("Trying an NS server from Authoritative server : " + tempstr)
                            try:
                                record = get_dns_record(sock, urlArray[-1], str(record.auth[counter].rdata), "A")
                                if record.header.rcode != 0:
                                    counter = counter + 1
                                    print("Error returned in getting response from NS server trying next record")
                                    continue
                                else:
                                    cacheDict[urlArray[-1]] = record
                            except:
                                print("Failed message in getting A from Authoritative server trying next server")
                                counter = counter + 1
                                continue
                        if record.header.a and (record.rr[0].rtype == 1 or record.rr[0].rtype == 28): #A TYPE or AAAA Type
                            for x in record.rr:
                                print(x.rdata)
                            command = "A"
                            break
                        elif record.header.a and record.rr[counter].rtype == 5: #CNAME
                            command = "CNAME"
                            url = str(record.rr[counter].rdata)
                            print("CNAME Found: "+url)
                            break
                        elif record.header.auth and record.auth[counter].rtype == 2:
                            command = "NS"
                        else:
                            command = "EXIT"
                    else:
                        print("No more NS servers to check")
                        command = "EXIT"
                        break
                break