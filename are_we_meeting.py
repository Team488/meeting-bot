from itertools import chain
from errbot import BotPlugin, botcmd

#config keys
ALL_USERS = 'ALL_USERS'
MEETING_THRESHOLD = 'MEETING_THRESHOLD'

CONFIG_TEMPLATE = {ALL_USERS: ['alex'], MEETING_THRESHOLD: 1}

# err persisted settings keys
COMING = 'coming_users'
NOT_COMING = 'not_coming_users'
TARGET_DATE = 'target_date'

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

        # init storage
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

        for user in self.config[ALL_USERS]:
            self.send(
                self.build_identifier("@{}".format(user)),
                "Would you come to a meeting on {}? Reply with `!yes` or `!no`.".format(self[TARGET_DATE])
            )
        return "Members asked: {}".format(self.config[ALL_USERS])

    def _reset_store(self):
        self[COMING] = []
        self[NOT_COMING] = []

    def _add_to_list(self, item, list_key):
        """
        helper util because errbot persistence is awkward
        """
        with self.mutable(list_key) as l:
            l.append(item)

    @botcmd
    def yes(self, msg, args):
        if msg.is_direct:
            user = msg.frm.username
            self._add_to_list(user, COMING)
            return "Registered that you are coming, thank you."

    @botcmd
    def no(self, msg, args):
        if msg.is_direct:
            user = msg.frm.username
            self._add_to_list(user, NOT_COMING)
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

    def callback_message(self, mess):
        #import pdb; pdb.set_trace()
        pass

