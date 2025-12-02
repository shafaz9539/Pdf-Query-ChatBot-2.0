from pwdlib import PasswordHash

hash_generator = PasswordHash.recommended()

def generate_hash(raw_string: str) -> str:
    """Hashes a plain password."""
    return hash_generator.hash(raw_string)

def verify_hash(raw_string: str, hashed_string: str) -> bool:
    """Verifies a plain password against a stored hash."""
    return hash_generator.verify(raw_string, hashed_string)