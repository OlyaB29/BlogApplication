import random
import string
import hashlib
import aiohttp
from config import settings


# Generating a random string
def get_random_string(length=12):
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


# Password hashing
def password_hash(password: str, salt: str = None):
    if salt is None:
        salt = get_random_string()
    enc = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return enc.hex()


# Checking whether the password hash matches the hash from the database
def password_check(password: str, hashed_password: str):
    salt, hashed = hashed_password.split("$")
    return password_hash(password, salt) == hashed


# Verification of email addresses
async def email_verify(email: str):
    url = "https://api.hunter.io/v2/email-verifier?email={}&api_key={}".format(email, settings.HUNTER_API_KEY)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            return data["data"]["status"]

