import struct

# Opcodes of all TMCL commands that can be used in direct mode
ROR=1
ROL=2
MST=3
MVP=4
SAP=5
GAP=6
STAP=7
RSAP=8
SGP=9
GGP=10
STGP=11
RSGP=12
RFS=13
SIO=14
GIO=15
SCO=30
GCO=31
CCO=32

# Opcodes of TMCL control functions (to be used to run or abort a TMCL program in the module)
APPL_STOP=128
APPL_RUN=129
APPL_RESET=131

# Options for MVP commandds
MVP_ABS=0
MVP_REL=1
MVP_COORD=2

# Options for RFS command
RFS_START=0
RFS_STOP=1
RFS_STATUS=2

# handle is an object with read() and write() methods.

def send_command(handle, address, command, type, motor, value):
	data=struct.pack('>BBBBiB', address, command, type, motor, value, 0)
	handle.write(data)

def get_result(handle, address, status, value):
	data=handle.read()
	
	checksum_calc=sum(ord(b) for b in data)
	
	address,status,value,checksum=struct.unpack('>BxBxi', data)

	if not checksum_calc==checksum:
		# Checksum error
		...

	return address, status, value