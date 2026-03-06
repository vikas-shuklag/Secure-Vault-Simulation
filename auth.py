import hashlib

PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()

def authenticate():
    password = input("Enter system password: ")

    if hashlib.sha256(password.encode()).hexdigest() == PASSWORD_HASH:
        print("Authentication Successful")
        return True
    else:
        print("Authentication Failed")
        return False