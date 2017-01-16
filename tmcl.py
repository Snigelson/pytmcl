import struct

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
    Input:  Bytes object
    Output: Integer
    """
    return (sum(b for b in data))%256

def send_command(handle, address, command, type, motor, value):
    """ Send a command to a Trinamic controller.
    handle is a file or stream object, basically anything that
    implements write and read methods.
    """
    data=struct.pack('>BBBBi', address, command, type, motor, value)
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
    data=handle.read(9)

    address,module,status,command,value,checksum=struct.unpack('>BBBBiB', data)

    if not checksum==_calculate_checksum(data[:-1]):
        # Checksum error
        raise TMCLError(status_string[1])

    if not status==100:
        # Error from motor controller
        raise TMCLError(
            'Error {}: {}'.format(
                status, status_string.get(status,'Unknown error')
            ))

    return address, value


if __name__=='__main__':
    import sys
    import serial

    def print_usage():
	    print('Usage: {} <instruction> <type> <motor> <value> <port>'.format(sys.argv[0]))

    if not len(sys.argv) == 6:
        print_usage()
        sys.exit(-1)

    port=serial.Serial(sys.argv[5], 9600)

    try:
        port.open()
    except OSError as e:
        print('Error opening serial port: '+str(e))
        sys.exit(-1)

    address=1
    instruction=int(sys.argv[1])
    type=int(sys.argv[2])
    motor=int(sys.argv[3])
    value=int(sys.argv[4])

    send_command(port, address, instruction, type, motor, value)
    result=get_result(port)

    print('Result: '+str(result))
