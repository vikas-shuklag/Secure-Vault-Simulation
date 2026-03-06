from auth import authenticate
from secure_vault import store_secret, retrieve_secret
from root_of_trust import verify_root

def menu():

    print("\nSecure Storage System")
    print("1 Store Secret")
    print("2 Retrieve Secret")
    print("3 Exit")

    return input("Select option: ")

def main():

    if not authenticate():
        return

    while True:

        choice = menu()

        if choice == "1":

            data = input("Enter secret data: ")

            if verify_root(data.encode()):
                store_secret(data)
            else:
                print("Root of Trust verification failed")

        elif choice == "2":

            retrieve_secret()

        elif choice == "3":

            print("System exiting")
            break

        else:
            print("Invalid option")


if __name__ == "__main__":
    main()