# — coding: utf-8 —
import random
length = 44
bits=[1,2,4,8,16,32]

def text_to_bin(string):
    bins=""
    for code in string.encode('utf-8'):
        bins+=str(bin(code)[2:]).zfill(12)
    ends=len(bins)%length
    add=""
    add=add.zfill(length-ends)
    return bins+add

def into_blocks(text_bin, block_size=length):
    for i in range(len(text_bin)):
        if not i % block_size:
            yield text_bin[i:i + block_size]

def get_check_bits_data(value_bin):
    check_bits_count_map = {k: 0 for k in bits}
    for index, value in enumerate(value_bin, 1):
        if int(value):
            bin_char_list = list(bin(index)[2:].zfill(12))
            bin_char_list.reverse()
            for degree in [2 ** int(i) for i, value in enumerate(bin_char_list) if int(value)]:
                check_bits_count_map[degree] += 1
    check_bits_value_map = {}
    for check_bit, count in check_bits_count_map.items():
        check_bits_value_map[check_bit] = 0 if not count % 2 else 1
    return check_bits_value_map

def set_empty_check_bits(value_bin):
    for bit in bits:
        value_bin = value_bin[:bit - 1] + '0' + value_bin[bit - 1:]
    return value_bin

def set_check_bits(value_bin):
    value_bin = set_empty_check_bits(value_bin)
    check_bits_data = get_check_bits_data(value_bin)
    for check_bit, bit_value in check_bits_data.items():
        value_bin = '{0}{1}{2}'.format(
            value_bin[:check_bit - 1], bit_value, value_bin[check_bit:])
    return value_bin

def get_check_bits(value_bin):
    check_bits = {}
    for index, value in enumerate(value_bin, 1):
        if index in bits:
            check_bits[index] = int(value)
    return check_bits

def exclude_check_bits(value_bin):
    clean_value_bin = ''
    for index, char_bin in enumerate(list(value_bin), 1):
        if index not in bits:
            clean_value_bin += char_bin
    return clean_value_bin

def set_errors(encoded):
    result = ''
    for chunk in into_blocks(encoded, length + len(bits)):
        num_bit = random.randint(1, len(chunk))
        chunk = '{0}{1}{2}'.format(chunk[:num_bit - 1], int(chunk[num_bit - 1]) ^ 1, chunk[num_bit:])
        result += (chunk)
    return result

def set_2_errors(encoded):
    result = ''
    for chunk in into_blocks(encoded, length + len(bits)):
        num_bit = random.sample(list(range(0,47)),2)
        num_bit=[31,32]
        chunk = '{0}{1}{2}'.format(chunk[:num_bit[0] - 1], int(chunk[num_bit[0] - 1]) ^ 1, chunk[num_bit[0]:])
        chunk = '{0}{1}{2}'.format(chunk[:num_bit[1] - 1], int(chunk[num_bit[1] - 1]) ^ 1, chunk[num_bit[1]:])
        result += (chunk)
    return result

def check_and_fix_error(encoded_chunk):
    check_bits_encoded = get_check_bits(encoded_chunk)
    check_item = exclude_check_bits(encoded_chunk)
    check_item = set_check_bits(check_item)
    check_bits_e = get_check_bits(check_item)
    check_bits = get_check_bits(check_item)
    if check_bits_encoded != check_bits:
        invalid_bits = []
        for check_bit_encoded, value in check_bits_encoded.items():
            if check_bits[check_bit_encoded] != value:
                invalid_bits.append(check_bit_encoded)
        num_bit = sum(invalid_bits)
        encoded_chunk = '{0}{1}{2}'.format(encoded_chunk[:num_bit - 1],int(encoded_chunk[num_bit - 1]) ^ 1,encoded_chunk[num_bit:])
    return encoded_chunk

def get_diff_index_list(value_bin1, value_bin2):
    diff_index_list = []
    for index, char_bin_items in enumerate(zip(list(value_bin1), list(value_bin2)), 1):
        if char_bin_items[0] != char_bin_items[1]:
            diff_index_list.append(index)
    return diff_index_list

def encode(source):
    text_bin = text_to_bin(source)
    result = ''
    for chunk_bin in into_blocks(text_bin):
        chunk_bin = set_check_bits(chunk_bin)
        result += chunk_bin
    return result

def decode(encoded, fix_errors=True):
    decoded_value = ''
    try:
        fixed_encoded_list = []
        for encoded_chunk in into_blocks(encoded, length + len(bits)):
            if fix_errors:
                encoded_chunk = check_and_fix_error(encoded_chunk)
                if check_and_fix_error(encoded_chunk)=="More than 1 mistake":
                    return "More than 1 mistake"
            fixed_encoded_list.append(encoded_chunk)
        clean_chunk_list = ""
        for encoded_chunk in fixed_encoded_list:
            encoded_chunk = exclude_check_bits(encoded_chunk)
            clean_chunk_list+=encoded_chunk
        d=len(clean_chunk_list)%12
        clean_chunk_list=clean_chunk_list[:-d]
        for clean_char in [clean_chunk_list[i:i + 12] for i in range(len(clean_chunk_list)) if not i % 12]:
            decoded_value += chr(int(clean_char, 2))
    except Exception:
        return("More than 1 mistake")
    return decoded_value

source = input('Enter text:')
print('Encoding block length: {0}'.format(length))
print('control bits: {0}'.format(bits))
encoded = encode(source)
print('Translation into a binary string code: {0}'.format(encoded))
decoded = decode(encoded)
print('Decoding result: {0}'.format(decoded))
encoded_with_error = set_errors(encoded)
print('Assume 1 error in the encoded data: {0}'.format(encoded_with_error))
diff_index_list = get_diff_index_list(encoded, encoded_with_error)
print('Bit errors are allowed: {0}'.format(diff_index_list))
decoded = decode(encoded_with_error, fix_errors=False)
print('The result of decoding erroneous data without error correction: {0}'.format(decoded))
decoded = decode(encoded_with_error)
print('The result of decoding erroneous data with error correction: {0}'.format(decoded))
encoded_with_error = set_2_errors(encoded)
print('Allow 2 errors in the encoded data: {0}'.format(encoded_with_error))
diff_index_list = get_diff_index_list(encoded, encoded_with_error)
print('Bit errors are allowed: {0}'.format(diff_index_list))
decoded = decode(encoded_with_error, fix_errors=False)
print('The result of decoding erroneous data without error correction: {0}'.format(decoded))
decoded = decode(encoded_with_error)
print('The result of decoding erroneous data with error correction: {0}'.format(decoded))