# coding=utf-8
import socket, os, sys, struct, time, hashlib, random
import 	threading

lock = threading.Lock()

def generateErrorChecksum(seq, seqNum, pError):
	if(random.random() < pError):
		return struct.pack("!q", seqNum + 1)
	return seq

def generateCheckSum(package):
	checksum = hashlib.md5()
	checksum.update(package)
	return checksum.digest()

def generatePackage(seqNum, line, pError):
	timestamp = time.time()

	# Packing Message #
	seq = struct.pack("!q", seqNum)
	seconds = struct.pack('!q', int(timestamp))
	nanoseconds = struct.pack('!l', int((timestamp-int(timestamp))*pow(10,9)))
	msgSize = struct.pack("!h", len(line))
	msg = line.encode('latin1')

	# Simulating error on checksum changing the seq number #
	checksum = generateCheckSum(generateErrorChecksum(seq, seqNum, pError) + seconds + nanoseconds + msgSize + msg)
	
	return seq + seconds + nanoseconds + msgSize + msg + checksum

def readFile(filePath, pError):
	seqNum = 0
	messages = []
    
	file = open(filePath, "r") 
        
	for line in file: 
		seqNum += 1
		messages.append(generatePackage(seqNum,line,pError))

	return messages

def firstUnconfirmedItem(confirmations):
	for i in range(len(confirmations)):
		if confirmations[i] == 0: return i
	return -1

def sendMessage(packages, confirmations, i, udp, dest):
	try:
		print('====== Package ======')
		print('i', i)
		print('package', packages[i])

		udp.sendto(packages[i], dest)
		print(confirmations[i])
		while(not confirmations[i]):

			ackPackage = udp.recvfrom(36)[0]		

			# Reading Ack
			seq = ackPackage[0:8]
			sec = ackPackage[8:16]
			nsec = ackPackage[16:20]
			receivedChecksum = ackPackage[20:36]
			checksum = generateCheckSum(seq + sec + nsec)
			
			receivedMessageNum = struct.unpack('!q', seq)[0] - 1
			
			if(checksum == receivedChecksum):
				lock.acquire()
				confirmations[receivedMessageNum] = 1
				print('RECEIVED ========= ', receivedMessageNum)
				print(confirmations)
				lock.release()
			else:
				# timeout
				udp.sendto(packages[receivedMessageNum], 1)
	except:
		print("Extrapolou o tempo do servidor")
		if(not confirmations[i]):
			sendMessage(packages, confirmations, i, udp, dest)

	#morre thread
	print('==== Ended thread', i)

def main(filePath, address, windowSize, timeout, pError):

	[HOST, PORT] = address.split(':')
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	udp.settimeout(timeout)
	dest = (HOST, int(PORT))

	packages = readFile(filePath, pError)
	threads = [None] * len(packages)
	confirmations = [0] * len(packages)

	item = firstUnconfirmedItem(confirmations)
	
	for i in range(len(threads)):
		threads[i] = threading.Thread(target=sendMessage, args=(packages,confirmations,i, udp, dest))
		print(threads)
		# Should wait the ack for first message
		if(threading.active_count() > windowSize):
			while(not confirmations[item]):
				pass
			item = firstUnconfirmedItem(confirmations)
		
		threads[i] = threads[i].start()

	print('here')
	while(firstUnconfirmedItem(confirmations) != -1):
		pass
		
	print('Ending ~')
	udp.close()

	print('Ending 2')

if __name__ == "__main__":
	main(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]))
