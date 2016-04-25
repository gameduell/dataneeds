import declares as dc

import gd.core as gd


class Agent(dc.Entity):
    browser = gd.SoftwareInfo()
    os = gd.SoftwareInfo()
    device = gd.SoftwareInfo()
    ...


class RequestHeader(dc.Entity):
    host = dc.String()
    user_agent = Agent()
    accept_language = dc.String()
    cid = dc.String()
    ...


class HttpRequest(dc.Event):
    timestamp = dc.Timestamp()
    path = dc.String()
    params = dc.Dict(dc.String(), dc.Any())
    referrer = dc.String()  # Url
    request = dc.Dict(dc.String(), dc.Any())
    ip = dc.String()  # Ip
    session = dc.String()
    response = dc.Dict(dc.String(), dc.Any()) >> RequestHeader()
    typ = dc.Categorical('request-type')
    user_id = ~gd.User.id
    app = dc.Categorical('app')
    status = dc.Number()
    country = dc.Categorical('country')
    role = ~gd.User.role
    data = dc.Any()
    debug = dc.Any()


class TrackingEvent(dc.Cons):
    name = dc.Categorical('event-name')
    step_1 = ~dc.Categorical('event-step-1')
    step_2 = ~dc.Categorical('event-step-2')


class ClientTracking(dc.Event):
    arrival_ts = dc.Timestamp()  #
    device_ts = dc.Timestamp()
    batch_ts = ~dc.Timestamp()
    seq_num = dc.Number()

    game = gd.Game.id  #
    event = TrackingEvent()
    parameters = dc.Dict(dc.String(), dc.Any())

    user_id = gd.User.id  #
    fb_id = gd.User.fb_id

    country = gd.Country()

    gd_session = ~dc.String()  #
    fb_session = ~dc.String()


class SocialTrackingParameters:
    json = ...


class SocialTrackingRequest(HttpRequest):
    HttpRequest.timestamp >> ClientTracking.arrival_ts
    HttpRequest.path >> (dc.Regexp('/social/rest/(...)/event/tracking.*')
                         >> ClientTracking.game)
    HttpRequest.user_id >> ClientTracking.user_id
    HttpRequest.session >> ClientTracking.gd_session

    HttpRequest.params >> SocialTrackingParameters()
