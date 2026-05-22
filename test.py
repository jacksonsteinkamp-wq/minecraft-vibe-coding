import sys

print("PYTHON:", sys.executable)
print("VERSION:", sys.version)

try:
    import requests
    print("REQUESTS OK")
except Exception as e:
    print("REQUESTS FAIL:", e)