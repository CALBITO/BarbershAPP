import secrets
import base64

def generate_key(length=32):
    """Generate a secure random key"""
    return base64.urlsafe_b64encode(secrets.token_bytes(length)).decode('utf-8')

if __name__ == "__main__":
    # Generate keys
    secret_key = generate_key()
    jwt_secret_key = generate_key()
    
    print("\nGenerated Keys (add these to your .env file):")
    print("-" * 50)
    print(f"SECRET_KEY={secret_key}")
    print(f"JWT_SECRET_KEY={jwt_secret_key}")
    print("-" * 50)