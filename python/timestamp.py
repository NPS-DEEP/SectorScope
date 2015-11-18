from datetime import datetime
def ts0(msg):
    t0 = datetime.now()
    print(msg, t0)
    return t0

def ts(msg, t0):
    t1 = datetime.now()
    print(msg, t1, t1-t0)
    return t1

