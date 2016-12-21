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

# Status code to string mapping
status_string = {
    100: "Successfully executed, no error",
    101: "Command loaded into TMCL program EEPROM",
    1:   "Wrong checksum",
    2:   "Invalid command",
    3:   "Wrong type",
    4:   "Invalid value",
    5:   "Configuration EEPROM locked",
    6:   "Command not available"
}

class TMCLError(Exception):
    pass

def _calculate_checksum(data):
    """ Calculate checksum.
    Input:  Bytes object, string or array
    Output: Integer
    """
    return (sum(ord(b) for b in data))%256

def send_command(handle, address, command, type, motor, value):
    """ Send a command to a Trinamic controller.
    handle is a file or stream object, basically anything that
    implements write and read methods.
    """
    data=struct.pack('>BBBBiB', address, command, type, motor, value)
    data+=struct.pack('>B',_calculate_checksum(data))
    handle.write(data)

def get_result(handle):
    """ Read a result from a Trinamic controller.
    handle is a file or stream object, basically anything that
    implements write and read methods.
    Returns a tuple with controller address, status code and
    value.
    Raises TMCLError with appropriate error message on error.
    """
    data=handle.read()

    address,status,value,checksum=struct.unpack('>BxBxiB', data)

    if not checksum==_calculate_checksum(data[:-2]):
        # Checksum error
        raise TMCLError(status_string[1])

    if not status==100:
        # Error from motor controller
        raise TMCLError(status_string[status])

    return address, status, value
