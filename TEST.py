# 橢圓曲線 secp256k1 的參數
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
a = 0  # 橢圓曲線的 a 參數
b = 7  # 橢圓曲線的 b 參數

# 測試點座標 (13G 的結果)
x = 0xfe8d1eb1bcb3432b1db5833ff5f2226d9cb5e65cee430558c18ed3a3c86ce1af
y = 0x07b158f244cd0de2134ac7c1d371cffbfae4db40801a2572e531c573cda9b5b4

# 驗證點是否在橢圓曲線上：y^2 ≡ x^3 + ax + b (mod p)
lhs = pow(y, 2, p)  # 計算 y^2 mod p
rhs = (pow(x, 3, p) + a * x + b) % p  # 計算 x^3 + ax + b mod p

print(f"lhs (y^2 mod p): {lhs}")
print(f"rhs (x^3 + ax + b mod p): {rhs}")
print(f"Point is on the curve: {lhs == rhs}")
