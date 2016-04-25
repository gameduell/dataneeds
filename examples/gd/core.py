import declares as dc


class Country(dc.Entity):
    code = dc.Categorical('country-code')
    name = dc.String()


class User(dc.Entity):
    id = dc.Number()
    fb_id = dc.String()

    country = Country()

    name = dc.String()
    role = dc.Set(dc.String)
    ...


class Platform(dc.Entity):
    id = dc.Categorical('platform')
    name = dc.String()
    ...


class SoftwareInfo(dc.Entity):
    name = dc.String()
    version = dc.String()


class Game(dc.Entity):
    id = dc.Categorical('game_type')
    name = dc.String()

    players = (dc.Number() + dc.Number()) | dc.Set(dc.Number)
    platforms = dc.Set(Platform.id)
    ...
