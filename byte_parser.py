import bitstring


def parse_dns_query(byte_data):
    headers = parse_headers(byte_data[:12])
    q, a, auth_a, add_a = parse_body(byte_data, headers)
    return headers, q, a, auth_a, add_a


def get_dns_response(headers, q, a, auth_a, add_a):
    headers['Total Questions'] = len(q)
    headers['Total Answer RRs'] = len(a)
    headers['Total Authority RRs'] = len(auth_a)
    headers['Total Additional RRs'] = len(add_a)
    result = bitstring.BitArray().bytes
    result += headers_to_bytes(headers)
    for question in q:
        result += question_to_bytes(question)
    for group in [a, auth_a, add_a]:
        for answer in group:
            result += answer_to_bytes(answer)
    return result


def headers_to_bytes(headers):
    header_format = 'uint:16, uint:1, uint:4, uint:1, uint:1, uint:1, ' \
                    'uint:4, uint:4, uint:16, uint:16, uint:16, uint:16'
    return bitstring.pack(header_format, headers['Identification'], 1,
                          headers['Opcode'], headers['AA'], headers['TC'],
                          headers['RD'], 0, 0, headers['Total Questions'],
                          headers['Total Answer RRs'],
                          headers['Total Authority RRs'],
                          headers['Total Additional RRs']).bytes


def answer_to_bytes(answer):
    result = bitstring.BitArray()
    result += name_to_bytes(answer['Name'])
    addr_format = 'uint:16, uint:16, uint:32, uint:16'
    result += bitstring.pack(addr_format, answer['Type'], answer['Class'],
                             answer['Ttl'], answer['Length'])
    if answer['Type'] == 1:
        result += ip_to_bytes(answer['Address'])
    else:
        result += name_to_bytes(answer['Address'])
    return result.bytes


def ip_to_bytes(address):
    result = bitstring.BitArray()
    for part in address.split('.'):
        result += bitstring.pack('uint:8', int(part))
    return result.bytes


def question_to_bytes(question):
    result = bitstring.BitArray()
    result += name_to_bytes(question['Name'])
    result += bitstring.pack('uint:16, uint:16', question['Type'],
                             question['Class'])
    return result.bytes


def name_to_bytes(name):
    result = bitstring.BitArray()
    for sub_name in name.split('.'):
        result += bitstring.pack('uint:8', len(sub_name))
        for c in sub_name:
            result += bitstring.pack('hex:8', c.encode('ASCII').hex())
    result += bitstring.pack('uint:8', 0)
    return result.bytes


def get_bits(byte_data):
    return ''.join([bin(b)[2:].rjust(8, '0') for b in byte_data])


def parse_headers(header_bytes):
    header_bits = get_bits(header_bytes)
    result = {'Identification': int(header_bits[:16], 2),
              'QR': int(header_bits[16:17], 2),
              'Opcode': int(header_bits[17:21], 2),
              'AA': int(header_bits[21], 2), 'TC': int(header_bits[22], 2),
              'RD': int(header_bits[23], 2), 'RA': int(header_bits[24], 2),
              'Z': int(header_bits[25], 2), 'AD': int(header_bits[26], 2),
              'CD': int(header_bits[27], 2),
              'Rcode': int(header_bits[28:32], 2),
              'Total Questions': int(header_bits[32:48], 2),
              'Total Answer RRs': int(header_bits[48:64], 2),
              'Total Authority RRs': int(header_bits[64:80], 2),
              'Total Additional RRs': int(header_bits[80:], 2)}
    return result


def parse_body(byte_data, headers):
    q = []
    a = []
    auth_a = []
    add_a = []

    pointer = 12
    for i in range(headers['Total Questions']):
        question, read_bytes = parse_question(byte_data, pointer)
        q.append(question)
        pointer += read_bytes
    for i in range(headers['Total Answer RRs']):
        answer, read_bytes = parse_answer(byte_data, pointer)
        a.append(answer)
        pointer += read_bytes
    for i in range(headers['Total Authority RRs']):
        answer, read_bytes = parse_answer(byte_data, pointer)
        auth_a.append(answer)
        pointer += read_bytes
    for i in range(headers['Total Additional RRs']):
        answer, read_bytes = parse_answer(byte_data, pointer)
        add_a.append(answer)
        pointer += read_bytes
    return q, a, auth_a, add_a


def parse_question(byte_data, offset):
    name, amount = parse_name(byte_data, offset)
    new_offset = offset + amount
    q_type = int.from_bytes(byte_data[new_offset:new_offset + 2], 'big')
    q_class = int.from_bytes(byte_data[new_offset + 2:new_offset + 4], 'big')
    result = {'Name': name,
              'Type': q_type,
              'Class': q_class}
    return result, amount + 4


def parse_answer(byte_data, offset):
    name, amount = parse_name(byte_data, offset)
    new_offset = offset + amount
    a_type = int.from_bytes(byte_data[new_offset:new_offset + 2], 'big')
    a_class = int.from_bytes(byte_data[new_offset + 2:new_offset + 4], 'big')
    a_ttl = int.from_bytes(byte_data[new_offset + 4:new_offset + 8], 'big')
    a_rd_len = int.from_bytes(byte_data[new_offset + 8:new_offset + 10], 'big')
    a_rd_data, rd_amount = parse_address(byte_data, new_offset + 10,
                                         a_rd_len, a_type)
    result = {'Name': name,
              'Type': a_type,
              'Class': a_class,
              'Ttl': a_ttl,
              'Length': a_rd_len,
              'Address': a_rd_data}
    return result, amount + rd_amount + 10


def parse_address(byte_data, offset, length, a_type):
    if a_type == 1:
        addr = '.'.join(['{}'.format(byte_data[offset + i])
                         for i in range(length)])
        return addr, length

    elif a_type == 2:
        name = parse_name(byte_data, offset)[0]
        return name, length
    else:
        return '', length


def parse_name(byte_data, offset):
    position = offset
    amount = 1
    length = byte_data[position]
    position += 1
    name = ''
    if length != 0:
        if length < 192:
            name += byte_data[position:position + length].decode('ASCII') + '.'
            amount += length
            position += length
            rec_name, rec_amount = parse_name(byte_data, position)
            return (name + rec_name).rstrip('.'), amount + rec_amount
        else:
            pointer = (length - 192) * 256 + byte_data[position]
            name += parse_name(byte_data, pointer)[0]
            return name, 2
    else:
        return name, amount


def bytes_from_bin_string(bin_string):
    return int(bin_string, 2).to_bytes((len(bin_string) + 7) // 8, 'big')
