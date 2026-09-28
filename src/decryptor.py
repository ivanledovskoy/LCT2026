import struct
import argparse

def decrypt_sector(lba: int, encrypted_data: bytes) -> bytes:
    if len(encrypted_data) != 512:
        raise ValueError("Aligned")
        
    enc_n = (0x38C9CDA0 * lba - 0x61C85616) & 0xFFFFFFFF
    
    words = list(struct.unpack("<128I", encrypted_data))
    
    for i in range(32):
        idx = i * 4
        
        mask_1 = (
            ((enc_n - 0x255992ED) & 0xFFFFFFFF) >> 24 |
            (((enc_n + 0x78DDE6C4) & 0xFFFFFFFF) >> 24) << 8 |
            (((enc_n + 0x17156075) & 0xFFFFFFFF) >> 24) << 16 |
            (((enc_n - 0x4AB325DA) & 0xFFFFFFFF) >> 24) << 24
        )
        
        mask_2 = (
            ((enc_n + 0x538453D7) & 0xFFFFFFFF) >> 24 |
            (((enc_n - 239350392) & 0xFFFFFFFF) >> 24) << 8 |
            (((enc_n - 1879881927) & 0xFFFFFFFF) >> 24) << 16 |
            (((enc_n + 774553834) & 0xFFFFFFFF) >> 24) << 24
        )
        
        mask_3 = (
            (((enc_n + 1788458060) & 0xFFFFFFFF) >> 24) << 8 |
            ((enc_n - 865977701) & 0xFFFFFFFF) >> 24 |
            (((enc_n + 147926525) & 0xFFFFFFFF) >> 24) << 16 |
            (((enc_n - 1492605010) & 0xFFFFFFFF) >> 24) << 24
        )
        
        mask_0 = (
            ((enc_n + 0x61C8864F) & 0xFFFFFFFF) >> 24 |
            ((enc_n >> 24) & 0xFF) << 8 |
            (((enc_n - 0x61C8864F) & 0xFFFFFFFF) >> 24) << 16 |
            (((enc_n + 0x3C6EF362) & 0xFFFFFFFF) >> 24) << 24
        )
        
        words[idx + 1] ^= mask_1
        words[idx + 2] ^= mask_2
        words[idx + 3] ^= mask_3
        words[idx + 0] ^= mask_0
        
        enc_n = (enc_n + 1103515245) & 0xFFFFFFFF

    return struct.pack("<128I", *words)

def decrypt_dump(input_file_path: str, output_file_path: str, start_lba: int = 0):
    with open(input_file_path, "rb") as f_in, open(output_file_path, "wb") as f_out:
        lba = start_lba
        while True:
            sector = f_in.read(512)
            if not sector:
                break
            if len(sector) < 512:
                sector = sector.ljust(512, b'\x00')
                
            decrypted = decrypt_sector(lba, sector)
            f_out.write(decrypted)
            lba += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True)
    parser.add_argument("-o", required=True)
    args = parser.parse_args()
    decrypt_dump(args.i, args.o)