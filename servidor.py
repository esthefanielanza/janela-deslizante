# coding=utf-8
import socket, os, sys, struct, time, hashlib, random
import threading

lock = threading.Lock()

def generateCheckSum(package):
	checksum = hashlib.md5()
	checksum.update(package)
	return checksum.digest()

def needsRetransmission(seqnum, clientsWindows, address):
  return (seqnum <= clientsWindows[address][1])

def isInsideWindow(seqnum, clientsWindows, address):
  return (clientsWindows[address][0] <= seqnum) and (seqnum <= clientsWindows[address][0]+clientsWindows[address][1])

def addMsgToLog(seqnum, message, file):
  print("Saved message %d" % seqnum)
  with open(file,'a') as f:
    f.write(message)

def removeFromArray(clientsWindows, address, indexToRemove):
  clientsWindows[address][2] = [i for i in clientsWindows[address][2] if i[0] != indexToRemove]

def indexInArray(clientsWindows, address, indexToFind):
  for i in clientsWindows[address][2]:
    if i[0] == indexToFind:
      return True
  return False

def generateErrorChecksum(seq, pError):
  seqNum = struct.unpack('!q', seq)[0]

  if(random.random() < pError):
    return struct.pack("!q", seqNum + 1)
  return seq

def firstElementMessage(window, seqnum):
  for package in window:
    if(package[0] == seqnum):
      return package[1]

def moveWindow(clientsWindows, address, seq, file):
  firstElement = clientsWindows[address][0]

  while(indexInArray(clientsWindows, address, firstElement)): 
    clientsWindows[address][0] += 1
    clientsWindows[address][1] += 1
    addMsgToLog(firstElement, firstElementMessage(clientsWindows[address][2], firstElement), file)        
    removeFromArray(clientsWindows,address,firstElement)
    firstElement += 1

def validMessage(seqnum, sec, nsec, clientsWindows, address, udp, windowSize, message):
  seq = struct.unpack('!q', seqnum)[0]
  isValid = False
  if address in clientsWindows:
    if isInsideWindow(seq, clientsWindows, address):
      # Mensagem está dentro da janela
      clientsWindows[address][2].append([seq,message])
      isValid = True
    else:
      isValid = False
  else:
      clientsWindows[address] = [1,windowSize,[]]
      clientsWindows[address][2].append([seq,message])
      isValid = True

  if needsRetransmission(seq, clientsWindows, address):
    checksumAck = generateCheckSum(seqnum + sec + nsec)
    udp.sendto(seqnum + sec + nsec + checksumAck, address)

  return isValid

def receiveMessages(address, data, clientsWindows, udp, windowSize, file, pError):
  seqnum = data[0:8]
  sec = data[8:16]
  nsec = data[16:20]

  sz = data[20:22]
  msgSize = struct.unpack('!h', sz)[0]

  message = data[22:22+msgSize]
  receivedChecksum = data[22+msgSize:22+msgSize+16]

  # Checksum #
  checksum = generateCheckSum(generateErrorChecksum(seqnum, pError) + sec + nsec + sz + message)

  seq = struct.unpack('!q', seqnum)[0]

  # Valid message #
  if(checksum == receivedChecksum):
    sz = struct.unpack('!h', sz)[0]
    message = message.decode('latin1')
    
    lock.acquire()
    if(validMessage(seqnum, sec, nsec, clientsWindows, address, udp, windowSize, message)): 
      if (seq == clientsWindows[address][0]):
        moveWindow(clientsWindows, address, seq, file)

    else:
      print('Message outside the window. Message %d will be discarded' % seq)
    
    lock.release()

  else: 
    print('Wrong checksum. Message %d will be discarded' % seq)

def main(file, port, windowSize, pError):
  udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  udp.bind(('', port))

  clientsWindows = {}
  clients = []

  while True:
    data,address = udp.recvfrom(16422)
    newThread = threading.Thread(target=receiveMessages, args=(address, data, clientsWindows, udp, windowSize, file, pError))
    clients.append(newThread)
    newThread.start()

  udp.close()

if __name__ == "__main__":
	main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]))

