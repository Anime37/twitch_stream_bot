import requests

from cli import TagCLI
from fs import FS

from .announcement import TwitchAnnouncement
from .bans import TwitchBans
from .channel import TwitchChannel
from .clips import TwitchClips
from .eventsub import TwitchEventSub
from .guest_star import TwitchGuestStar
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
        self._init_dependencies()
        self._init_dependency_api()
        self._init_standard_level_api()
        self._init_affiliate_level_api()

    def _init_dependencies(self):
        self.cli = TagCLI('API')
        self.fs = FS()
        self.session = requests.Session()

    def _init_dependency_api(self):
        self.oauth = TwitchOAuth(self.session, self.cli, self.fs)
        self.streams = TwitchStreams(self.session, self.cli)

    def _init_standard_level_api(self):
        self.announcements = TwitchAnnouncement(self.session, self.cli, self.fs, self.oauth)
        self.bans = TwitchBans(self.session, self.cli, self.oauth)
        self.channel = TwitchChannel(self.session, self.cli, self.oauth)
        self.clips = TwitchClips(self.session, self.cli, self.oauth)
        self.eventsub = TwitchEventSub(self.session, self.cli, self.oauth)
        self.guest_star = TwitchGuestStar(self.session, self.cli, self.oauth)
        self.raid = TwitchRaid(self.session, self.cli, self.fs, self.oauth, self.streams)
        self.segments = TwitchSegments(self.session, self.cli, self.fs, self.oauth)
        self.shoutout = TwitchShoutout(self.session, self.cli, self.fs, self.oauth)
        self.whispers = TwitchWhisper(self.session, self.cli, self.fs, self.oauth)

    def _init_affiliate_level_api(self):
        self.polls = TwitchPolls(self.session, self.cli, self.fs, self.oauth)
        self.predictions = TwitchPredictions(self.session, self.cli, self.fs, self.oauth)