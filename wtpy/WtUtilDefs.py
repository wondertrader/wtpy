def singleton(cls):
    instances = {}
    def getinstance(*args,**kwargs):
        if cls not in instances:
            instances[cls] = cls(*args,**kwargs)
        return instances[cls]
    return getinstance


def deprecated(func):
    def wrapper(*args, **kwargs):
        msg = f"Warning: {func.__name__} is deprecated."
        print(msg)
        return func(*args, **kwargs)
    return wrapper
