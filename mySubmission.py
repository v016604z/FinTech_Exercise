#############################################################
# Problem 0: Find base point
def GetCurveParameters():
    # Certicom secp256-k1
    # Hints: https://en.bitcoin.it/wiki/Secp256k1
    _p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    _a = 0x0000000000000000000000000000000000000000000000000000000000000000
    _b = 0x0000000000000000000000000000000000000000000000000000000000000007
    _Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798  #基於橢圓曲線的公開金鑰加密演算法 非壓縮形式
    _Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8  
    _Gz = 0x0000000000000000000000000000000000000000000000000000000000000001
    _n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    _h = 0x01
    return _p, _a, _b, _Gx, _Gy, _Gz, _n, _h


#############################################################
# Problem 1: Evaluate 4G
def compute4G(G, callback_get_INFINITY):
    """Compute 4G"""

    """ Your code here """
    result = G
    for _ in range(2):
        result = result.double()
    return result   


#############################################################
# Problem 2: Evaluate 5G
def compute5G(G, callback_get_INFINITY):
    """Compute 5G"""

    """ Your code here """
    result = compute4G(G, callback_get_INFINITY)
    result = result + G
    return result   


#############################################################
# Problem 3: Evaluate dG
# Problem 4: Double-and-Add algorithm
def double_and_add(n, point, callback_get_INFINITY):
    """Calculate n * point using the Double-and-Add algorithm."""

    """ Your code here """
    result = callback_get_INFINITY()
    num_doubles = 0
    num_additions = 0

    for bit in bin(n)[2:]:  # 將 n 的二進制從最低位依次遍歷
        if result == callback_get_INFINITY(): # 如果結果是無窮點，則將結果設為基點，並跳過計數器
            result = result.double()
            result += point
            continue

        result = result.double()  # 每位都進行一次倍點運算
        num_doubles += 1

        if bit == '1':            # 如果當前位是 1 ，則進行加法運算
            result += point       # 加上基點 G
            num_additions += 1    # 記錄加法次數

    return result, num_doubles, num_additions

#############################################################
# Problem 5: Optimized Double And Add (#Doubles, #Addiotns)
def optimized_double_and_add(n, point, callback_get_INFINITY):
    """Optimized Double-and-Add algorithm that simplifies sequences of consecutive 1's."""

    result = callback_get_INFINITY()
    num_doubles = 0
    num_additions = 0

    for bit in bin(n)[2:]:  # 將 n 的二進制從最低位依次遍歷
        if result == callback_get_INFINITY(): # 如果結果是無窮點，則將結果設為基點，並跳過計數器
            result = result.double()
            result += point
            continue

        result = result.double()  # 每位都進行一次倍點運算
        num_doubles += 1

        if bit == '1':            # 如果當前位是 1 ，則進行加法運算
            result -= point       # 加上基點 G
            num_additions += 1    #          

    return result, num_doubles, num_additions

#############################################################
# Problem 6: Sign a Bitcoin transaction with a random k and private key d
def sign_transaction(private_key, hashID, callback_getG, callback_get_n, callback_randint):
    """Sign a bitcoin transaction using the private key."""

    """ Your code here """

    G = callback_getG()
    n = callback_get_n()
    k = callback_randint(1, n - 1)
    R = k * G  # R = kG
    r = R.x() % n
    hashID = int(hashID,16)  # 如果hashID是字符串，將其轉為整數
    s = ((hashID + r * private_key) * pow(k, -1, n)) % n
    return (r, s)


##############################################################
# Step 7: Verify the digital signature with the public key Q
def verify_signature(public_key, hashID, signature, callback_getG, callback_get_n, callback_get_INFINITY):
    """Verify the digital signature."""

    """ Your code here """

    n = callback_get_n()
    is_valid_signature = n > 0

    r, s = signature
    G = callback_getG()
    #計算 s 的模數反元素
    w = pow(s, -1, n)
    
    u1 = (int(hashID , 16) * w) % n
    u2 = ((r) * w) % n  
    point = u1 * G + u2 * public_key  # Point addition

    return point.x() % n == r and is_valid_signature
