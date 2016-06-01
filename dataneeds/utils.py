import weakref


def nameof(descriptor, owner):
    for name, attr in owner.__dict__.items():
        if attr is descriptor:
            return name
    else:
        return None


class OwningDescriptor:
    """
    The OwiningDescriptor takes care of relation to owning class/object.

    When accessed as a discriptor form another object / class,
    the `__owned__` method is called and should create an Owned object with the
    relation to the owner / instance. Forthermore the Owned object is cached,
    so only a single instance is used for any access to the descriptor.
    """

    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)
        self.__owns__ = weakref.WeakKeyDictionary()

    def __owned__(self, name, instance, owner):
        """Return object for when this object is accessed as a descriptor."""
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
    """For objects that are part of (owned by) another object."""

    def __init__(self, name, instance, owner):
        self.name = name
        self.owner = owner
        self.instance = instance

    @property
    def owned(self):
        return self.instance or self.owner
