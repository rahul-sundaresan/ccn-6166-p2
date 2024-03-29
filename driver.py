import sys
import gbn_sender
import sr_sender


def read_file_and_return_params(file_name):
    with open(file_name, mode='r') as tcp_deets:
        tcp_type = tcp_deets.readline().rstrip() #  GBN or SR
        seq_bits, window_size = tcp_deets.readline().rstrip().split(' ') #  Seq bits and window size
        seq_bits = int(seq_bits)
        window_size = int(window_size)
        timeout = int(tcp_deets.readline().rstrip())
        mss = int(tcp_deets.readline().rstrip())
        return tcp_type, seq_bits, window_size, timeout, mss


if __name__ == '__main__':
    input_file = sys.argv[1]
    dst_port = int(sys.argv[2])
    packet_count = int(sys.argv[3])
    tcp_type: str
    tcp_type, seq_bits, window_size, timeout, mss = read_file_and_return_params(input_file)
    if tcp_type == "GBN":
        gbn_sender.gbn_send(dst_port, packet_count, seq_bits, window_size, timeout, mss)
    else:
        sr_sender.sr_send(dst_port, packet_count, seq_bits, window_size, timeout, mss)


