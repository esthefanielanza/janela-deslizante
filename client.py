# coding=utf-8
import socket, os, sys, threading, struct, time, hashlib

def generateCheckSum(seq, seconds, nanoseconds, msgSize, msg):
	checksum = hashlib.md5()
	checksum.update(seq + seconds + nanoseconds + msgSize + msg)
	return checksum.digest()

def generatePackage(seqNum, line):
	timestamp = time.time()
	
	# Packing Message #
	seq = struct.pack("!q", seqNum)
	seconds = struct.pack('!q', int(timestamp))
	nanoseconds = struct.pack('!l', int((timestamp-int(timestamp))*pow(10,9)))
	msgSize = struct.pack("!h", len(line))
	msg = line.encode('latin1')

	checksum = generateCheckSum(seq, seconds, nanoseconds, msgSize, msg)

	print('\n************** Sizes *************\n')
	print(len(seq))
	print(len(seconds))
	print(len(nanoseconds))
	print(len(msgSize))
	print(len(msg))

	print('\n************** MD5 **************\n')
	print(checksum)

	return [seq, seconds, nanoseconds, msgSize, msg, checksum]


def main(filePath, address, windowSize, timeout, errorProbability):

	[HOST, PORT] = address.split(':')
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	dest = (HOST, int(PORT))

	seqNum = 0
	currentFrame = 0

	file = open(filePath, "r") 
	for line in file:
		currentPackage = generatePackage(seqNum, line)
		
		print('\n************** Package **************\n')
		print(currentPackage)

		if(currentFrame < windowSize):
			for item in currentPackage:
				print('Sending item:', item)
				udp.sendto(item, dest)
			currentFrame += 1

		else:
			print('Should wait the ack')
			print('After wait')
			msg = udp.recvfrom(1024).decode('latin1')
			currentFrame -= 1
			udp.sendto(item, dest)


		print('Ending ~')

	udp.close()

if __name__ == "__main__":
	main(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]))

# Run command: python client.py teste.txt 127.0.0.1:5000 1 1 1
