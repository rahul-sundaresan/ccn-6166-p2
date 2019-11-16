import socket
import pickle
import hashlib
import sys


def gbn_receiver(receiver_host_name, receiver_listening_port):
    receiver_socket = socket.socket(socket.AF_INET6,socket.SOCK_DGRAM)
    receiver_socket.bind((receiver_host_name,receiver_listening_port))
    print("Listening on:", receiver_host_name, str(receiver_listening_port))
    expected_seq_num = 1
    while True:
        #  get the raw packet and src ip and port of packet
        received_raw_packet, client_info = receiver_socket.recvfrom(4096)
        received_packet = pickle.loads(received_raw_packet)
        received_seq_number, received_checksum, payload, mss, seq_bits = received_packet
        computed_checksum = hashlib.sha256()
        computed_checksum.update(pickle.dumps(received_seq_number))
        computed_checksum.update(payload)
        computed_checksum.update(pickle.dumps(mss))
        computed_checksum.update(pickle.dumps(seq_bits))
        #  Check if the packet is corrupt
        if received_checksum == computed_checksum.digest():
            if received_seq_number == expected_seq_num:
                print("Received Segment", received_seq_number)
                expected_seq_num = (expected_seq_num + mss) % (2 ** seq_bits - 1)
                # successfully received mss bytes so expect next mss bytes
                ack_checksum = hashlib.sha256()
                ack_checksum.update(pickle.dumps(expected_seq_num))
                ack_packet = (expected_seq_num, ack_checksum.digest())
                receiver_socket.sendto(pickle.dumps(ack_packet), client_info)
                print("ACK Sent:", expected_seq_num)

            else:
                #  received out of order packet
                print("Received out of order segment:", received_seq_number)
                #  send ACK with previous sequence number
                ack_checksum = hashlib.sha256()
                ack_checksum.update(pickle.dumps(expected_seq_num))
                ack_packet = (expected_seq_num, ack_checksum.digest())
                receiver_socket.sendto(pickle.dumps(ack_packet), client_info)
                print("ACK Sent:", expected_seq_num)
        else:
            #  received corrupted packet
            print("Received Corrupted segment:", received_seq_number)
            #  send ACK with previous sequence number
            ack_checksum = hashlib.sha256()
            ack_checksum.update(pickle.dumps(expected_seq_num))
            ack_packet = (expected_seq_num, ack_checksum.digest())
            receiver_socket.sendto(pickle.dumps(ack_packet), client_info)
            print("ACK Sent:", expected_seq_num)


if __name__ == '__main__':
    receiver_host = "localhost"
    listening_port = int(sys.argv[1])
    gbn_receiver(receiver_host, listening_port)
