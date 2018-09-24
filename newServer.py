# coding=utf-8
import socket, os, sys, struct, time, hashlib, random
import 	threading

lock = threading.Lock()

def generateCheckSum(package):
	checksum = hashlib.md5()
	checksum.update(package)
	return checksum.digest()

def needsRetransmission(seqnum, clientsWindows, address):
  return (seqnum <= clientsWindows[address][1])

def isInsideWindow(seqnum, clientsWindows, address):
  return (clientsWindows[address][0] <= seqnum) and (seqnum <= clientsWindows[address][0]+clientsWindows[address][1])

def addMsgToLog(seqnum,message,address,messagesLog):
  print("Adicionando ao log")
  messagesLog.append((seqnum, message, address))

def moveWindow(clientsWindows, address):
  print('clientWindows', clientsWindows)
  clientsWindows[address][0] += 1
  clientsWindows[address][1] += 1

def validMessage(seqnum, sec, nsec, clientsWindows, messagesLog, address, udp, windowSize):
  if address in clientsWindows:
    if needsRetransmission(seqnum, clientsWindows, address):
      checksumAck = generateCheckSum(seqnum + sec + nsec)
      udp.sendto(seqnum + sec + nsec + checksumAck, address[0])

    if isInsideWindow(seqnum, clientsWindows, address):
      return True
    else:
      return False
  else:
      clientsWindows[address] = [1,1 + windowSize]
      return True

def receiveMessages(address, data, clientsWindows, messagesLog, udp, windowSize):
  
  seqnum = data[0:8]
  sec = data[8:16]
  nsec = data[16:20]

  sz = data[20:22]
  msgSize = struct.unpack('!h', sz)[0]

  message = data[22:22+msgSize]
  receivedChecksum = data[22+msgSize:22+msgSize+16]
  
  # Checksum #
  checksum = generateCheckSum(seqnum + sec + nsec + sz + message)

  # Valid message #
  if(checksum == receivedChecksum):
    sz = struct.unpack('!h', sz)[0]
    message = message.decode('latin1')

    print('seqnum', seqnum)
    print('seq', sec)
    print('nseq', nsec)
    print('sz', msgSize)
    print('message', message)

    if(validMessage(seqnum, sec, nsec, clientsWindows, messagesLog, address, udp, windowSize)): 
      lock.acquire()
      seq = struct.unpack('!q', seqnum)[0]
      print('new seqnum', seq)
      if (seq == clientsWindows[address][0]):addMsgToLog(seq,message,address,messagesLog)
      moveWindow(clientsWindows, address)
      
      lock.release()

    else:
        print('Message outside the window. Message will be discarded')

  else: 
    print('Wrong checksum. Message will be discarded')

  udp.close()


def main(file, port, windowSize, pError):
  udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  udp.bind(('', port))
  print('Receiving ~')

  clientsWindows = {}
  clients = []
  messagesLog = []

  while True:
    data,address = udp.recvfrom(16422)
    newThread = threading.Thread(target=receiveMessages, args=(address, data, clientsWindows, messagesLog, udp, windowSize))
    clients.append(newThread)
    newThread.start()

  recordLog(messagesLog)


if __name__ == "__main__":
	main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]))

# Run command: python newServer.py server.txt 5000 10 0


# Receiving ~
# ('seqnum', '\x00\x00\x00\x00\x00\x00\x00\x01')
# ('seq', ('seqnum', '\x00\x00\x00\x00[\xa88\x14'('seqnum''\x00\x00\x00\x00\x00\x00\x00, \x02''))\x00\x00\x00\x00\x00\x00\x00\x03'
# )
# ('nseq', '\x19\xaba\x1c')
# ('sz', 3(
# (''seq'seq', , '\x00'\x00\x00\x00\x00[\x00\x00\x00\xa8[8\x14'\xa88\x14'))

# ('ns(eq''nseq'), , '\x19\xb2\x95!'
# )'\x19\xb5\xa6<')

# ((('mes's'sage'szz'', 8, , 7))

# (u'oi\n'()'message', 
# 'message'u'batata\n'('new seqnum'), 1, u'funciona'))


# Message outside the window. Message will be discarded
# Adicionando ao log
# Message outside the window. Message will be discarded
# ('clientWindows', {('127.0.0.1', 46228): [1, 11]})
# ('seqnum', Traceback (most recent call last):
#   File "newServer.py", line 104, in <module>
#     main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]))
#   File "newServer.py", line 95, in main
#     data,address = udp.recvfrom(16422)
# '\x00\x00\x00\x00\x00\x00\x00\x03')
#   File "/usr/lib/python2.7/socket.py", line 174, in _dummy
#     raise error(EBADF, 'Bad file descriptor')
# ('seq', '\x00\x00\x00\x00[\xa88\x19')
# socket.error: [Errno 9] Bad file descriptor('nseq', '\x1a\x02\xa5\xad')

# ('sz', 8)
# ('message', u'funciona')
# Message outside the window. Message will be discarded



