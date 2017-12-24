#!/usr/bin/env python3


def combine(num, data=b''):
    #   Combine header and data
    bytes_num = num.to_bytes(4, byteorder='little', signed=True)
    return bytes_num + data


def separate(packet):
    #   Separate header and data from packet
    num = int.from_bytes(packet[0:4], byteorder='little', signed=True)
    return num, packet[4:]
