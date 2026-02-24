import os
import secrets

env_file = ".env"
env_example = ".env.example"

if not os.path.exists(env_file):
    print("Initializing environment...")
    with open(env_example, "r") as src, open(env_file, "w") as dst:
        for line in src:
            if "JWT_SECRET_KEY=" in line:
                # Generate a real 256-bit secure secret key
                new_key = secrets.token_hex(32)
                dst.write(f"JWT_SECRET_KEY={new_key}\n")
            else:
                dst.write(line)
    print("✅ .env file created from template with a randomized secure JWT key!")
else:
    print("ℹ️ .env file already exists. Skipping environment initialization.")

print("\nVirtual HSM + PKI is ready.")
