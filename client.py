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


def main(filePath, ipAddress, windowSize, timeout, errorProbability):

	seqNum = 0
	currentFrame = 0

	file = open(filePath, "r") 
	for line in file:
		currentPackage = generatePackage(seqNum, line)
		
		print('\n************** Package **************\n')
		print(currentPackage)

		if(currentFrame < windowSize):
			print('Should send')
			currentFrame += 1

		else:
			print('Should wait the ack')
			print('After wait')
			currentFrame = 0


	# 	print line, 

	# try
	# 	socket.setdefaulttimeout(10)
	# 	tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# 	tcp.connect((ipAddress, portNumber))

	# 	tcp.send(struct.pack('!1i', len(stringContent)))
	# 	tcp.send (rotated_word(stringContent, cesarFactor).encode('latin1'))
	# 	tcp.send(struct.pack('!1i', cesarFactor))

	# 	msg = tcp.recv(len(stringContent)).decode('latin1')

	# 	print(msg)
	# 	tcp.close()
		
	# except (ValueError, socket.error, socket.gaierror, socket.herror):
	# 	print("Atenção: Erro de conexão com o servidor.")
	# 	pass
	# except (socket.timeout):
	# 	print("Atenção: Tempo limite com o servidor excedido. Tente novamente mais tarde.")
	# 	pass

if __name__ == "__main__":
	main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]))