import copy

# ==========================================
# PART 1: GF(2^8) Arithmetic
# ==========================================

# The AES Irreducible Polynomial: x^8 + x^4 + x^3 + x + 1
AES_MODULUS = 0x11B

def gf_add(a, b):
    """
    Addition in GF(2^8) is simply XOR.
    """
    return a ^ b

def gf_mult(a, b):
    """
    Multiplication in GF(2^8) modulo the AES polynomial.
    """
    p = 0 
    for _ in range(8):
        if (b & 1) == 1:
            p = p ^ a
        
        hi_bit_set = (a & 0x80)
        a = (a << 1) & 0xFF 
        if hi_bit_set:
            a = a ^ 0x1B 
        b = b >> 1
    return p

# ==========================================
# PART 2: Compute Multiplicative Inverses
# ==========================================

def gf_inverse(a):
    """
    Finds the multiplicative inverse of 'a' in GF(2^8).
    """
    if a == 0:
        return 0
    
    # Using exponentiation method: a^(-1) = a^(254)
    result = 1
    for _ in range(254):
        result = gf_mult(result, a)
        
    return result

# ==========================================
# PART 3: Affine Transformation
# ==========================================

def affine_transform(byte_val):
    """
    Applies the AES Affine Transformation to a byte.
    """
    c = 0x63
    b = byte_val
    new_b = 0
    
    for i in range(8):
        # Calculate the ith bit based on the AES matrix
        bit = (b >> i) & 1
        bit ^= (b >> ((i + 4) % 8)) & 1
        bit ^= (b >> ((i + 5) % 8)) & 1
        bit ^= (b >> ((i + 6) % 8)) & 1
        bit ^= (b >> ((i + 7) % 8)) & 1
        
        # Add the constant bit
        c_bit = (c >> i) & 1
        bit ^= c_bit
        
        new_b |= (bit << i)
        
    return new_b

# ==========================================
# PART 4: Generate S-Box Table
# ==========================================

def generate_sbox():
    sbox = [0] * 256
    for i in range(256):
        inv = gf_inverse(i)
        s = affine_transform(inv)
        sbox[i] = s
    return sbox

def print_sbox(sbox):
    print("\n--- AES S-Box Generated from Scratch ---\n")
    print("     0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F")
    print("   -----------------------------------------------")
    for row in range(16):
        print(f"{row:X} |", end=" ")
        for col in range(16):
            val = sbox[row * 16 + col]
            print(f"{val:02X}", end=" ")
        print() 

# ==========================================
# PART 5: Minimum Experiment (Non-Linearity)
# ==========================================

def calculate_non_linearity(sbox):
    """
    Calculates the non-linearity of the S-Box.
    """
    print("\nCalculating Non-linearity... (This may take 10-20 seconds)")
    
    max_bias = 0
    
    # Pre-calculate parity for speed
    parity_table = [bin(x).count('1') % 2 for x in range(256)]

    # Loop through all Output Masks (v)
    for v in range(1, 256):
        # Loop through all Input Masks (u)
        for u in range(1, 256):
            matches = 0
            
            # Test Linear Approximation across all inputs (x)
            for x in range(256):
                input_masked = u & x
                output_masked = v & sbox[x]
                
                # Check if Parity(u.x) == Parity(v.S(x))
                if parity_table[input_masked] == parity_table[output_masked]:
                    matches += 1
            
            # Calculate bias from ideal (128)
            bias = abs(matches - 128)
            if bias > max_bias:
                max_bias = bias
                
    return 128 - max_bias

# ==========================================
# Main Execution
# ==========================================

if __name__ == "__main__":
    # 1. Generate
    aes_sbox = generate_sbox()
    print_sbox(aes_sbox)
    
    # 2. Verify
    print("\n[Verification Spot Check]")
    print(f"Input 0x00 -> {aes_sbox[0]:02X} (Expected 63)")
    print(f"Input 0x01 -> {aes_sbox[1]:02X} (Expected 7C)")
    
    # 3. Experiment
    nl_score = calculate_non_linearity(aes_sbox)
    
    print(f"\n--- Experiment Results ---")
    print(f"Calculated Non-linearity: {nl_score}")
    
    if nl_score == 112:
        print("SUCCESS: Your S-Box matches the cryptographic strength of AES (112).")
    else:
        print(f"Note: Standard AES is 112. You got {nl_score}.")
