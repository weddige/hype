import logging
from enum import Enum, auto
from typing import List

import yaml

class BotAccount:
    server: str
    client_id: str
    client_secret: str
    access_token: str

    def __init__(self, server: str, client_id: str, client_secret: str, access_token: str) -> None:
        self.server = server
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token

    def __repr__(self) -> str:
        return f"server: {self.server}, email: {self.email}, password: {self.password}"


class Instance:
    class Software(Enum):
        MASTODON = auto()
        PIXELFED = auto()

    name: str
    limit: int
    software: Software
    boost_text: bool

    def __init__(
        self,
        name: str,
        limit: int,
        software: Software = Software.MASTODON,
        boost_only_media: bool = False,
        boost_only_described: bool = False,
    ) -> None:
        self.name = name
        self.limit = limit if limit > 0 and limit <= 20 else 20
        self.software = software
        self.boost_only_media = boost_only_media
        self.boost_only_described = boost_only_described

    def __repr__(self) -> str:
        return f"{self.name} (top {self.limit})"


class Config:
    bot_account: BotAccount
    interval: int = 60  # minutes
    log_level: str = "INFO"
    subscribed_instances: List = []
    filtered_instances: List = []
    profile: str = ""
    fields: dict = {}
    delay: int = 0 # seconds

    def __init__(self):
        # auth file containing login info
        auth = "/app/config/auth.yaml"
        # settings file containing subscriptions
        conf = "/app/config/config.yaml"

        # only load auth info
        with open(auth, "r") as configfile:
            config = yaml.load(configfile, Loader=yaml.Loader)
            logging.getLogger("Config").debug("Loading auth info")
            if (
                config
                and config.get("bot_account")
                and config["bot_account"].get("server")
                and config["bot_account"].get("client_id")
                and config["bot_account"].get("client_secret")
                and config["bot_account"].get("access_token")
            ):
                self.bot_account = BotAccount(
                    server=config["bot_account"]["server"],
                    client_id=config["bot_account"]["client_id"],
                    client_secret=config["bot_account"]["client_secret"],
                    access_token=config["bot_account"]["access_token"],
                )
            else:
                logging.getLogger("Config").error(config)
                raise ConfigException("Bot account config is incomplete or missing.")

        with open(conf, "r") as configfile:
            config = yaml.load(configfile, Loader=yaml.Loader)
            logging.getLogger("Config").debug("Loading settings")
            if config:
                self.interval = (
                    config["interval"] if config.get("interval") else self.interval
                )
                self.delay = (
                    config["delay"] if config.get("delay") else self.delay
                )
                self.log_level = (
                    config["log_level"] if config.get("log_level") else self.log_level
                )

                self.profile = (
                    config["profile"] if config.get("profile") else self.profile
                )

                self.fields = (
                    {name: value for name, value in config["fields"].items()}
                    if config.get("fields")
                    else {}
                )

                self.subscribed_instances = (
                    [
                        Instance(
                            name,
                            props["limit"],
                            Instance.Software[
                                props.get("software", "mastodon").upper()
                            ],
                            props.get("boost_only_media", False),
                            props.get("boost_only_described", False),
                        )
                        for name, props in config["subscribed_instances"].items()
                    ]
                    if config.get("subscribed_instances")
                    else []
                )

                self.filtered_instances = (
                    [name for name in config["filtered_instances"]]
                    if config.get("filtered_instances")
                    else []
                )


class ConfigException(Exception):
    pass
