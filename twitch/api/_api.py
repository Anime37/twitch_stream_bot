import requests

from .announcement import TwitchAnnouncement
from .channel import TwitchChannel
from .clips import TwitchClips
from .eventsub import TwitchEventSub
from .guest_star import TwitchGuestStar
from .logging import TwitchLogging
from .oauth import TwitchOAuth
from .polls import TwitchPolls
from .predictions import TwitchPredictions
from .raid import TwitchRaid
from .segments import TwitchSegments
from .shoutout import TwitchShoutout
from .streams import TwitchStreams
from .whisper import TwitchWhisper


class TwitchAPI():
    def __init__(self):
        self._init_prerequisites()
        self.announcements = TwitchAnnouncement(self.session, self.logging, self.oauth)
        self.channel = TwitchChannel(self.session, self.logging, self.oauth)
        self.clips = TwitchClips(self.session, self.logging, self.oauth)
        self.eventsub = TwitchEventSub(self.session, self.logging, self.oauth)
        self.guest_star = TwitchGuestStar(self.session, self.logging, self.oauth)
        self.polls = TwitchPolls(self.session, self.logging, self.oauth)
        self.predictions = TwitchPredictions(self.session, self.logging, self.oauth)
        self.raid = TwitchRaid(self.session, self.logging, self.oauth, self.streams)
        self.segments = TwitchSegments(self.session, self.logging, self.oauth)
        self.shoutout = TwitchShoutout(self.session, self.logging, self.oauth)
        self.whispers = TwitchWhisper(self.session, self.logging, self.oauth)

    def _init_prerequisites(self):
        self.session = requests.Session()
        self.logging = TwitchLogging()
        self.oauth = TwitchOAuth(self.session, self.logging)
        self.streams = TwitchStreams(self.session, self.logging)
