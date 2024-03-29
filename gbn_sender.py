import socket
import hashlib
import os
import time
import pickle
import random


def gbn_send(dst_port, packet_count, seq_bits, window_size, timeout, mss):
    #  create client side socket
    recv_host = "localhost"
    recv_port = dst_port
    #  IPv6 is the future and the future is now
    client_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    next_seq_num = 1
    tcp_window = []
    latest_ack_time = time.time()
    sent_packet_count = 0
    random.seed()

    while sent_packet_count <= packet_count:
        for _ in range(window_size):
            payload = os.getrandom(mss)
            random_number = random.random()  # number for roulette wheel seeletion mechanism
            #  create packet tuple (sequence_no, checksum, payload, mss, bits for sequence number)
            checksum = hashlib.sha256()
            checksum.update(pickle.dumps(next_seq_num))
            checksum.update(payload)
            checksum.update(pickle.dumps(mss))
            checksum.update(pickle.dumps(seq_bits))
            if random_number < 0.1:  # roulette wheel selection mechanism
                print("Intentionally meddling with payload hue hue hue")
                payload = payload = os.getrandom(mss)
            packet_in_send_queue = (next_seq_num, checksum.digest(), payload, mss, seq_bits)
            # send our "TCP" segment via UDP
            client_socket.sendto(pickle.dumps(packet_in_send_queue), (recv_host, recv_port))
            print("Sending sequence no: " + str(next_seq_num) + "; Timer started")
            next_seq_num = (next_seq_num + mss) % (2**seq_bits - 1)
            tcp_window.append(packet_in_send_queue)

        #  process ACK with probability
        if 0.1 <= random_number < 0.15:
            print("Dropped the ACK")
        else:
            recv_packet = pickle.loads(client_socket.recv(4096))
            print("Received ACK: ", recv_packet[0])

            latest_ack_time = time.time()
            sent_packet_count += 1
            if recv_packet[0] == tcp_window[0][0]:
                del tcp_window[0]
        if time.time() - latest_ack_time > float(timeout/1000):
            for packet in tcp_window:
                print("Timer expired. Retransmitting packet with with seq No: ", str(packet[0]))
                client_socket.sendto(pickle.dumps(packet), (recv_host, recv_port))
