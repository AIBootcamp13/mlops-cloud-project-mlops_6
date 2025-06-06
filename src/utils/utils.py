import os
import hashlib


def calculate_hash(filename):
    sha256_hash = hashlib.sha256()
    with open(filename, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def save_hash(dst):
    hash_ = calculate_hash(dst)
    dst, _ = os.path.splitext(dst)
    with open(f"{dst}.sha256", "w") as f:
        f.write(hash_)


def read_hash(dst):
    dst, _ = os.path.splitext(dst)
    with open(f"{dst}.sha256", "r") as f:
        return f.read()