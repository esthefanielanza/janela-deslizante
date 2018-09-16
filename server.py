# coding=utf-8
import socket, os, sys, threading, struct, time, hashlib

def generateCheckSum(seq, seconds, nanoseconds, msgSize, msg):
	checksum = hashlib.md5()
	checksum.update(seq + seconds + nanoseconds + msgSize + msg)
	return checksum.digest()

def main(filePath, port, windowSize, errorProbability):
  host = ''
  udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  orig = (host, port)
  udp.bind(orig)


  print('Receiving ~')
  
  # Receiving data #
  # Sum of the max sizes #
  package = udp.recvfrom(131110)[0]
  print(package)
  
  seqnum = package[0:8]
  sec = package[8:16]
  nsec = package[16:20]

  sz = package[20:22]
  msgSize = struct.unpack('!h', sz)[0]

  message = package[22:22+msgSize]
  md5 = package[22+msgSize:22+msgSize+16]
  
  # Checksum #
  checksum = generateCheckSum(seqnum, sec, nsec, sz, message)

  # Valid message #
  if(checksum == md5):
    print('Valid message!')
  
    seqnum = struct.unpack('!q', seqnum)[0]
    sec = struct.unpack('!q', sec)[0]
    nsec = struct.unpack('!l', nsec)[0]
    sz = struct.unpack('!h', sz)[0]
    message = message.decode('latin1')

    print('seqnum', seqnum)
    print('seq', sec)
    print('nseq', nsec)
    print('sz', msgSize)
    print('message', message)

  udp.close()

if __name__ == "__main__":
	main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]))

# Run command: python client.py teste.txt 127.0.0.1:5000 1 1 1
