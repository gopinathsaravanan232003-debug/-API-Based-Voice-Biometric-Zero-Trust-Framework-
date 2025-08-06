import os

print("Checking files:")
print("Enroll file exists:", os.path.exists("recordings/hy.wav"))
print("Auth file exists:", os.path.exists("recordings/hy_auth.wav"))
print("Enroll file size:", os.path.getsize("recordings/hy.wav"))
print("Auth file size:", os.path.getsize("recordings/hy_auth.wav"))
