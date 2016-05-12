def nameof(descriptor, owner):
    for name, attr in owner.__dict__.items():
        if attr is descriptor:
            return name
    else:
        return None
