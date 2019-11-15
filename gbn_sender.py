import socket
import hashlib
import os
import time
import pickle


def gbn_send(dst_port, packet_count, seq_bits, window_size, timeout, mss):

    #  create client side socket
    recv_host = "localhost"
    recv_port = dst_port
    client_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    window_base = 1
    next_seq_num = 1
    tcp_window = []
    latest_ack_time = time.time()
    sent_packet_count = 0

    while sent_packet_count <= packet_count:
        payload = os.getrandom(mss)
        if next_seq_num < window_base + window_size:
            #  create packet tuple (sequence_no, checksum, payload)
            checksum = hashlib.sha256()
            checksum.update(next_seq_num)
            checksum.update(payload)
            packet_in_send_queue = (next_seq_num,checksum.digest(),payload)
             # send our "TCP" segment via UDP
            client_socket.sendto(pickle.dumps(packet_in_send_queue), (recv_host, recv_port))
            print("Sending sequence no: " + str(next_seq_num) + "; Timer started")
            next_seq_num = (next_seq_num + mss)%(2**seq_bits - 1)
            tcp_window.append(packet_in_send_queue)
            sent_packet_count += 1
            recv_packet = pickle.loads(client_socket.recv(4096))
            print("Received ACK: ", recv_packet[0])
            while recv_packet[0] > window_base and window_size:
                latest_ack_time = time.time()
                del tcp_window[0]
                window_base = window_base + 1
            if time.time() - latest_ack_time > timeout:
                for packet in tcp_window:
                    print("Timer expired. Retransmitting packet with with seq No: ", str(packet[0]))
                    client_socket.sendto(pickle.dumps(packet), (recv_host, recv_port))
