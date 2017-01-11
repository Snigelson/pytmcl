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
        raise TMCLError(
            'Error {}: {}'.format(
                status, status_string.get(status,'Unknown error')
            ))

    return address, status, value
