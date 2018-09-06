# coding=utf-8
import socket, os, sys, threading, struct, time, md5

#agora sei usar git
def generatePackage(seqNum, line):
	timestamp = time.time()
	seconds = struct.pack('!q', int(timestamp))
	nanoseconds = struct.pack('!l', int((timestamp-int(timestamp))*pow(10,9)))
	msgSize = struct.pack("!h", len(line))
	
	checksum = md5.new()

	# print(seconds)

	# print(struct.pack('q', seconds) + " " + str(len(struct.pack('q', seconds))))

	# print(str(seconds) + str(nanoseconds) + str(msgSize) + str(line))
	# checksum.update(timestamp + seconds + nanoseconds + msgSize + msg)

	partialPackage = struct.pack("q", seqNum) + seconds + nanoseconds + line
	print(len(struct.pack("q", seqNum)))
	print(len(seconds))
	print(len(nanoseconds))
	print(len(line))
	print(len(partialPackage))

	return [timestamp, seconds, nanoseconds, msgSize, checksum]


def main(filePath, ipAddress, portNumber, windowSize, timeout, errorProbability):

	seqNum = 0

	file = open(filePath, "r") 
	for line in file:
		currentPackage = generatePackage(seqNum, line)
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
	main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]))