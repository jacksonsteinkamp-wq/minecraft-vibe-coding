STOP = False
STOP_REASON = None

def check_stop():
    if STOP:
        if STOP_REASON == "user":
            raise Exception("Stopped by user")
