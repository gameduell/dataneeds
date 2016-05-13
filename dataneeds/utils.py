import weakref


def nameof(descriptor, owner):
    for name, attr in owner.__dict__.items():
        if attr is descriptor:
            return name
    else:
        return None


class OwningDescriptor:

    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)
        self.__owns__ = weakref.WeakKeyDictionary()

    def __owned__(self, name, instance, owner):
        return Owned(name, instance, owner)

    def __get__(self, instance, owner):
        key = instance or owner
        try:
            return self.__owns__[key]
        except KeyError:
            name = nameof(self, owner)
            self.__owns__[key] = obj = self.__owned__(name, instance, owner)
            return obj


class Owned:

    def __init__(self, name, instance, owner):
        self.name = name
        self.owner = owner
        self.instance = instance

    @property
    def owned(self):
        return self.instance or self.owner
