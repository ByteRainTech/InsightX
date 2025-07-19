"""
缓存
"""
def store(key, value):
    global caches
    if 'caches' not in globals():
        caches = {key: value}
    else:
        caches["key"] = value
    return True # 成功!
def get(key):
    global caches
    if 'caches' not in globals():
        return None
    return caches[key]
