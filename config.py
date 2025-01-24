import os

from dotenv import load_dotenv

load_dotenv()

token = os.getenv('token')

width=int(os.getenv('width'))
height=int(os.getenv('height'))
code_length=int(os.getenv('code_length'))
