# coding=utf-8
import socket, os, sys, struct, time, hashlib, random
import 	threading

lock = threading.Lock()
messagesSent = 0
incorrectChecksum = 0

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

def readFile(filePath):
	with open(filePath, "r") as f:
		return f.readlines() 

def firstUnconfirmedItem(confirmations):
	for i in range(len(confirmations)):
		if confirmations[i] == 0: return i
	return -1

def sendMessage(lines, pError, confirmations, i, udp, dest, timeout):
	try:
		global messagesSent, incorrectChecksum
		
		package = generatePackage(i + 1, lines[i], pError)
		udp.sendto(package, dest)

		lock.acquire()
		messagesSent += 1
		lock.release()

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
				lock.release()

			else:
				time.sleep(timeout)
				package = generatePackage(receivedMessageNum, lines[receivedMessageNum], pError)
				udp.sendto(package, dest)


				lock.acquire()
				messagesSent += 1
				incorrectChecksum += 1
				lock.release()
				

	except Exception as e:
		if(not confirmations[i]):
			sendMessage(lines, pError, confirmations, i, udp, dest, timeout)

def main(filePath, address, windowSize, timeout, pError):
	global messagesSent, incorrectChecksum

	start = time.time()
	
	# Setting the socket
	[HOST, PORT] = address.split(':')
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	udp.settimeout(timeout)
	dest = (HOST, int(PORT))
	
	lines = readFile(filePath)
	threads = [None] * len(lines)
	confirmations = [0] * len(lines)
	item = firstUnconfirmedItem(confirmations)

	# Starting threads
	for i in range(len(threads)):
		threads[i] = threading.Thread(target=sendMessage, args=(lines, pError, confirmations, i, udp, dest, timeout))

		# Window is defined with the number of running threads, this is the window lock
		if(threading.active_count() > windowSize):
			while(not confirmations[item]):
				pass
			item = firstUnconfirmedItem(confirmations)
		
		threads[i] = threads[i].start()

	# Client should end if all the packages were sent
	while(firstUnconfirmedItem(confirmations) != -1):
		pass
		
	udp.close()
	end = time.time()

	print('%d %d %d %.3fs' % (len(lines), messagesSent, incorrectChecksum, end - start))

if __name__ == "__main__":
	main(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]))
