import cryptomite
from random import randint
import hashlib

def int_to_bool_list(i, length):
    return [bool(int(b)) for b in bin(i)[2:].zfill(length)]

def hash_data(data):
    # Convert the floats to integers
    data = [(int(x*1e9), int(y*1e9)) for x, y in data]

    # Convert the integers to binary and remove the '0b' prefix
    data = [(bin(x)[2:][2:], bin(y)[2:][2:]) for x, y in data]

    # Unpack the data
    A, B, C, D = [int(x, 2) for x, y in data for x in (x, y)]

    # Unpack the data
    A, B, C, D = [int(x, 2) for x, y in data for x in (x, y)]

    # Perform the operations
    E = A ^ B ^ C ^ D
    F = A & B & C & D
    G = A | B | C | D
    constant = 0x5A827999
    H = (A + B + C + D) % constant
    Output = E ^ F ^ G ^ H

    A = bin(A)[2:]
    E = bin(E)[2:]
    F = bin(F)[2:]
    G = bin(G)[2:]
    H = bin(H)[2:]
    Output = bin(Output)[2:]

    EFGHOutput = E + Output + G + F + H
    seed = A + H + F + G + E

    #Logic for Circulant Randomness Extractor: 
    # 1) n is the input length
    # 2) m is the output length
    # 3) EFGHOutput is the input1, seed is input2
    # 4) Assertion_1: len(EFGHOutput) = len(seed) - 1 = n
    # 5) Assertion_2: n + 1 also has to be prime
    
    # Pad the binary string with leading zeros to ensure a constant number of bits
    padded_output = EFGHOutput.zfill(130)
    seed = seed.zfill(131)
    EFGHOutput = int_to_bool_list(int(EFGHOutput, 2), 128)
    n = 130
    m = 128
    EFGHOutput = [int(bit) for bit in padded_output]
    seed = [int(bit) for bit in seed]
  
    EFGHOutput = EFGHOutput[:n]
    seed = seed[:n+1]
    
    circulant = cryptomite.Circulant(n, m)

    extracted_value = circulant.extract(EFGHOutput, seed)
    extracted_value_str = ''.join(map(str, extracted_value))

    #MD5
    import hashlib

    # Compute the MD5 hash of the extracted value
    md5_hash = hashlib.md5(extracted_value_str.encode()).hexdigest()
    
    # Convert the MD5 hash to binary
    md5_hash_binary = bin(int(md5_hash, 16))[2:].zfill(130)

    md5_hash_bool_list = int_to_bool_list(int(md5_hash_binary, 2), 130)
    final_extracted_value = circulant.extract(md5_hash_bool_list, seed)
    final_extracted_value_str = ''.join(map(str, final_extracted_value))

    return final_extracted_value_str