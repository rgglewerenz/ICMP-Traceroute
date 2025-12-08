#Ross Lewerenz, Tyler Dudley
#ICMP Traceroute Final project
from socket import *
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 2

# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise

def checksum(string):
    
    #HELLO THERE, I'm finally commenting now: the skeleton code refers to another lab,
    # the ping lab for this section of the code
    #naturally i went to that portion and ripped it right out for us to use
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = ord(string[count+1]) * 256 + ord(string[count])
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2

    if countTo < len(string):
        csum = csum + ord(string[len(string) - 1])
        csum = csum & 0xffffffff
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    
    answer = ~csum
    answer = answer & 0xffff

    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer
#wow how easy

def build_packet(mySocket,destAddr, ID):
   #this section of the skeleton code also refers to the previous ping lab
   #so I've based this def off of that lab's sendOnePing
    myChecksum = 0

    #foundation for assembling the packet
    header = struct.pack("bbHHh",ICMP_ECHO_REQUEST,0,myChecksum,ID,1)
    data = struct.pack("d",time.time())
    #calc the checksum for the fake header and data
    myChecksum= checksum(str(header+data))

    if sys.platform == 'darwin': ##I'll look this up at some point
        
        myChecksum = htons(myChecksum) & 0xffff

    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh",ICMP_ECHO_REQUEST,0,myChecksum,ID,1)

    packet = header + data
    return packet
    #pretty sure i don't have to modify the code from the ping lab
    #but if i do it'll be updated accordingly

def get_route(hostname):
    timeLeft = TIMEOUT
    for ttl in range(1, MAX_HOPS):
        for tries in range(TRIES):
            destAddr = gethostbyname(hostname)

            #Fill in start - first red section
            try:
                    mySocket = socket(AF_INET,SOCK_RAW,IPPROTO_ICMP)#yes i looked up the specifics
            except PermissionError:
                    print("Error, run as admin") #and also looked up error handling
                    return
            # Make a raw socket named mySocket
            #Fill in end

            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)

            try:
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))
                t = time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)

                if whatReady[0] == []:  # Timeout
                    print(" * * * Request timed out.")

                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect

                if timeLeft <= 0:
                    print(" * * * Request timed out.")

            except timeout:
                continue

            else:
                #Fill in start - second red section
                # Fetch the icmp type from the IP packet
                #Fill in end

                if types == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print(" %d rtt=%.0f ms %s" % (ttl,
                          (timeReceived - t) * 1000, addr[0]))

                elif types == 3:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print(" %d rtt=%.0f ms %s" % (ttl,
                          (timeReceived - t) * 1000, addr[0]))

                elif types == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print(" %d rtt=%.0f ms %s" % (ttl,
                          (timeReceived - timeSent) * 1000, addr[0]))
                    return

                else:
                    print("error")
                    break

            finally:
                mySocket.close()

get_route("google.com")
