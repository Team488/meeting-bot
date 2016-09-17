from itertools import chain
from errbot import BotPlugin, botcmd

#config keys
ALL_USERS = 'ALL_USERS'
MEETING_THRESHOLD = 'MEETING_THRESHOLD'

CONFIG_TEMPLATE = {
    ALL_USERS: ','.join([
        'alex',
        'johngilbert',
        'wasabifan',
        'robeat101',
        'ronak.shah',
        'tfrancisco',
        'seth_nguyen',
    ]),
    MEETING_THRESHOLD: 2}

# err persisted settings keys
COMING = 'coming_users'
NOT_COMING = 'not_coming_users'
TARGET_DATE = 'target_date'
INITIATOR = 'initiator'

class AreWeMeeting(BotPlugin):

    def get_configuration_template(self):
        return CONFIG_TEMPLATE

    def configure(self, configuration):
        """
            This will setup a default config, called before activate or when user sets config options
        """
        if configuration is not None and configuration != {}:
            config = dict(chain(CONFIG_TEMPLATE.items(),
                                configuration.items()))
        else:
            config = CONFIG_TEMPLATE
        super(AreWeMeeting, self).configure(config)

    def activate(self):
        """
        Initialization on plugin load
        """
        super().activate()

        # init persistent storage
        if COMING not in self:
            self[COMING] = []
        if NOT_COMING not in self:
            self[NOT_COMING] = []
        if TARGET_DATE not in self:
            self[TARGET_DATE] = None

    @botcmd
    def ask_if_coming(self, msg, args):
        if not args:
            return "Please specify when the meeting will be. Eg usage `!ask_if_coming sept-15`."
        self[TARGET_DATE] = args

        # reset store
        self._reset_store()

        # record who kicked off this ask
        self[INITIATOR] = msg.frm.nick

        for user in self.all_users:
            self._ask_user_if_coming(user)
        return "Members asked: {}".format(self.all_users)

    @botcmd
    def ask_missing_if_coming(self, msg, args):
        missing = self.get_missing_rsvp_users()
        for user in missing:
            self._ask_user_if_coming(user)
        return "Members asked: {}".format(self.all_users)


    def _ask_user_if_coming(self, user):
        self.send(
                self._build_id(user),
                "Would you come to a meeting on {}? Reply with `!yes` or `!no`.".format(self[TARGET_DATE])
            )

    def _build_id(self, user):
        return self.build_identifier("@{}".format(user))

    @property
    def all_users(self):
        if self.config and ALL_USERS in self.config:
            return self.config[ALL_USERS].split(',')
        else:
            return []

    def get_missing_rsvp_users(self):
        return [
            user for user in self.all_users
            if (user not in self[NOT_COMING]) and (user not in self[COMING])
        ]

    def _reset_store(self):
        self[COMING] = []
        self[NOT_COMING] = []

    def _add_to_list(self, item, list_key):
        """
        helper util because errbot persistence is awkward
        """
        with self.mutable(list_key) as l:
            l.append(item)

    def _remove_from_list(self, item, list_key):
        """
        helper util because errbot persistence is awkward
        """
        with self.mutable(list_key) as l:
            if item in l:
                l.remove(item)

    @botcmd
    def yes(self, msg, args):
        user = msg.frm.nick

        self.send(
            self._build_id(self[INITIATOR]),
            "{} can make the meeting".format(user)
        )

        self._add_to_list(user, COMING)
        self._remove_from_list(user, NOT_COMING)
        return "Registered that you are coming, thank you."

    @botcmd
    def no(self, msg, args):
        user = msg.frm.nick

        self.send(
            self._build_id(self[INITIATOR]),
            "{} cannot make the meeting".format(user)
        )

        self._add_to_list(user, NOT_COMING)
        self._remove_from_list(user, COMING)
        return "Registered that you cannot make it, thank you."

    @botcmd
    def make_call(self, msg, args):
        if not self[TARGET_DATE]:
            return "No current meeting proposed."

        # decide if we have enough participants to have the meeting
        if len(self[COMING]) >= self.config[MEETING_THRESHOLD]:
            return "There wil be a meeting with {} attending!".format(", ".join(self[COMING]))
        else:
            return "There will be no meeting this week, only {} people could make it which isn't enough.".format(
                len(self[COMING])
            )

    @botcmd
    def missing_rsvps(self, msg, args):
        missing = self.get_missing_rsvp_users()
        if missing:
            return "Still waiting to hear from: {}".format(missing)
        else:
            return "Have heard back from everyone"

    @botcmd
    def debug_break(self, msg, args):
        import pdb; pdb.set_trace()
        return "Done debugging!"

