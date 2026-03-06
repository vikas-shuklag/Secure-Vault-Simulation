import hashlib

def firmware_hash(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            sha256.update(data)

    return sha256.hexdigest()


def verify_firmware(file_path, trusted_hash):

    current = firmware_hash(file_path)

    if current == trusted_hash:
        return True
    else:
        return False