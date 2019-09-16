import base64 as b64
import urllib.parse

from .song import Song
from .user import UserStats, User
from .colors import Colour, colors
from .comment import Comment
from .abstractuser import AbstractUser
from .level import Level
from .message import Message
from .iconset import IconSet
from .friend_request import FriendRequest
from .level_packs import MapPack, Gauntlet

from .utils import convert_to_type
from .utils.converter import Converter
from .utils.indexer import Index as i
from .utils.crypto.coders import Coder
from .utils.mapper import mapper_util
from .utils.enums import (
    MessagePolicyType, FriendRequestPolicyType,
    CommentPolicyType, StatusLevel,
    LevelLength, TimelyType, CommentType,
    MessageOrRequestType, IconType, GauntletEnum
)

class ClassConverter:

    @classmethod
    def song_convert(cls, s):
        quoted_url = s[i.SONG_URL]
        dl_link = urllib.parse.unquote(quoted_url)
        return Song(
            name = s[i.SONG_TITLE],
            author = s[i.SONG_AUTHOR],
            id = s[i.SONG_ID],
            size = float(s[i.SONG_SIZE]),
            links = (
                f'https://www.newgrounds.com/audio/listen/{s[i.SONG_ID]}',
                dl_link
            ),
            custom = True,
        )

    @classmethod
    def song_from_kwargs(cls, **kwargs):
        return Song(**kwargs)

    @classmethod
    def user_stats_convert(cls, s, client=None):
        return UserStats(
            account_id = s[i.USER_ACCOUNT_ID], name = s[i.USER_NAME], id = s[i.USER_PLAYER_ID],
            stars = s[i.USER_STARS], demons = s[i.USER_DEMONS], cp = s[i.USER_CREATOR_POINTS],
            diamonds = s[i.USER_DIAMONDS], coins = s[i.USER_COINS], client = client,
            secret_coins = s[i.USER_SECRET_COINS], lb_place = s.get(i.USER_TOP_PLACE, -1)
        )

    @classmethod
    def user_convert(cls, s, client=None):
        dm = MessagePolicyType.from_value(s[i.USER_PRIVATE_MESSAGE_POLICY])
        fr_rq = FriendRequestPolicyType.from_value(s[i.USER_FRIEND_REQUEST_POLICY])
        comment = CommentPolicyType.from_value(s[i.USER_COMMENT_HISTORY_POLICY])

        stat = StatusLevel.from_value(s[i.USER_ROLE])
        rnk = s[i.USER_GLOBAL_RANK]
        rank = rnk if rnk else None

        youtube = s[i.USER_YOUTUBE]
        yt = (youtube, f'https://www.youtube.com/channel/{youtube}') if youtube else (None, None)

        twitter = s[i.USER_TWITTER]
        twt = (twitter, f'https://twitter.com/{twitter}') if twitter else (None, None)

        twitch = s[i.USER_TWITCH]
        twch = (twitch, f'https://twitch.tv/{twitch}') if twitch else (None, None)

        return User(
            name = s[i.USER_NAME], id = s[i.USER_PLAYER_ID],
            stars = s[i.USER_STARS], demons = s[i.USER_DEMONS],
            secret_coins = s[i.USER_SECRET_COINS], coins = s[i.USER_COINS],
            cp = s[i.USER_CREATOR_POINTS], diamonds = s[i.USER_DIAMONDS],
            role = stat, global_rank = rank,
            account_id = s[i.USER_ACCOUNT_ID], youtube = yt,
            twitter = twt, twitch = twch,
            messages = dm, friend_requests = fr_rq, comments = comment,
            icon_setup = IconSet(
                main_icon = s[i.USER_ICON],
                color_1 = colors[s[i.USER_COLOR_1]],
                color_2 = colors[s[i.USER_COLOR_2]],
                main_icon_type = IconType.from_value(s[i.USER_ICON_TYPE]),
                has_glow_outline = bool(s[i.USER_GLOW_OUTLINE_2]),
                icon_cube = s[i.USER_ICON_CUBE],
                icon_ship = s[i.USER_ICON_SHIP],
                icon_ball = s[i.USER_ICON_BALL],
                icon_ufo = s[i.USER_ICON_UFO],
                icon_wave = s[i.USER_ICON_WAVE],
                icon_robot = s[i.USER_ICON_ROBOT],
                icon_spider = s[i.USER_ICON_SPIDER]
            ),
            client = client
        )


    @classmethod
    def level_convert(cls, s, song, creator, client=None):
        try:  # decode password
            password = Coder.decode(type='levelpass', string=s.get(i.LEVEL_PASS))
        except TypeError:
            password = None
        if password == '1':
            password = ''

        desc = b64.b64decode(mapper_util.normalize(s[i.LEVEL_DESCRIPTION])).decode()
        length = LevelLength.from_value(s[i.LEVEL_LENGTH])
        type = TimelyType.from_value(s[i.LEVEL_TIMELY_TYPE])
        game_version = s[i.LEVEL_GAME_VERSION]  # needs to be converted to represent real version.

        try:
            leveldata = Coder.unzip(s[i.LEVEL_DATA])
        except KeyError:  # level data not present
            leveldata = None

        diff = s[i.LEVEL_DIFFICULTY]
        demon_diff = s[i.LEVEL_DEMON_DIFFICULTY]
        is_demon = bool(s[i.LEVEL_IS_DEMON])
        is_auto = bool(s[i.LEVEL_IS_AUTO])
        difficulty = Converter.convert_level_difficulty(
            diff=diff, demon_diff=demon_diff, is_demon=is_demon, is_auto=is_auto)

        return Level(
            id = s[i.LEVEL_ID],
            name = s[i.LEVEL_NAME],
            description = desc,
            version = s[i.LEVEL_VERSION],
            creator = creator,
            song = song,
            data = leveldata,
            is_demon = is_demon,
            is_auto = is_auto,
            difficulty = difficulty,
            stars = s[i.LEVEL_STARS],
            coins = s[i.LEVEL_COIN_COUNT],
            verified_coins = bool(s[i.LEVEL_COIN_VERIFIED]),
            is_epic = bool(s[i.LEVEL_IS_EPIC]),
            original = s[i.LEVEL_ORIGINAL],
            downloads = s[i.LEVEL_DOWNLOADS],
            rating = s[i.LEVEL_LIKES],
            score = s[i.LEVEL_FEATURED_SCORE],
            uploaded_timestamp = s.get(i.LEVEL_UPLOADED_TIMESTAMP),
            last_updated_timestamp = s.get(i.LEVEL_LAST_UPDATED_TIMESTAMP),
            length = length,
            game_version = game_version,
            stars_requested = s[i.LEVEL_REQUESTED_STARS],
            object_count = s[i.LEVEL_OBJECT_COUNT],
            type = type,
            time_n = s[i.LEVEL_TIMELY_INDEX],
            cooldown = s[i.LEVEL_TIMELY_COOLDOWN],
            client = client
        )

    @classmethod
    def map_pack_convert(cls, s, client=None):
        level_id_string = s.get(i.MAP_PACK_LEVEL_IDS, '0,0,0')
        level_ids = tuple(map(int, level_id_string.split(',')))

        color_string = s.get(i.MAP_PACK_COLOR, '255,255,255')
        color = Colour.from_rgb(*map(int, color_string.split(',')))

        difficulty = Converter.value_to_pack_difficulty(s.get(i.MAP_PACK_DIFFICULTY))

        return MapPack(
            id = s[i.MAP_PACK_ID],
            name = s[i.MAP_PACK_NAME],
            level_ids = level_ids,
            stars = s[i.MAP_PACK_STARS],
            coins = s[i.MAP_PACK_COINS],
            difficulty = difficulty,
            color = color,
            client = client
        )

    @classmethod
    def gauntlet_convert(cls, s, client=None):
        level_id_string = s.get(i.GAUNTLET_LEVEL_IDS, '0,0,0,0,0')
        level_ids = tuple(map(int, level_id_string.split(',')))

        typeid = s[i.GAUNTLET_ID]

        name = GauntletEnum.from_value(typeid).desc + ' Gauntlet'

        return Gauntlet(
            id = typeid, name = name, level_ids = level_ids, client = client
        )

    @classmethod
    def message_convert(cls, s, s_2, client=None):
        _type = MessageOrRequestType.from_value(s[i.MESSAGE_INDICATOR])

        useful_dict = {
            'name': s[i.MESSAGE_SENDER_NAME],
            'id': s[i.MESSAGE_SENDER_ID],
            'account_id': s[i.MESSAGE_SENDER_ACCOUNT_ID]
        }
        user_1, user_2 = [
            ClassConverter.abstractuser_convert(elem, client) for elem in (useful_dict, s_2)
        ]

        is_normal = _type.value ^ 1

        subject = b64.b64decode(mapper_util.normalize(s[i.MESSAGE_SUBJECT])).decode()
        return Message(
            id = s[i.MESSAGE_ID],
            timestamp = s[i.MESSAGE_TIMESTAMP],
            subject = subject,
            is_read = bool(s[i.MESSAGE_IS_READ]),
            author = user_1 if is_normal else user_2,
            recipient = user_2 if is_normal else user_1,
            type = _type,
            client = client
        )

    @classmethod
    def request_convert(cls, s, s_2, client=None):
        _type = MessageOrRequestType.from_value(s[i.REQUEST_INDICATOR])
        useful_dict = {
            'name': s[i.REQUEST_SENDER_NAME],
            'id': s[i.REQUEST_SENDER_ID],
            'account_id': s[i.REQUEST_SENDER_ACCOUNT_ID]
        }

        is_normal = _type.value ^ 1
        user_1, user_2 = (ClassConverter.abstractuser_convert(elem, client) for elem in (useful_dict, s_2))

        return FriendRequest(
            id = s[i.REQUEST_ID],
            timestamp = s[i.REQUEST_TIMESTAMP],
            body = b64.b64decode(mapper_util.normalize(s[i.REQUEST_BODY])).decode(),
            is_read = True if bool(s[i.REQUEST_STATUS]) ^ 1 else False,
            author = user_1 if is_normal else user_2,
            recipient = user_2 if is_normal else user_1,
            type = _type,
            client = client
        )

    @classmethod
    def comment_convert(cls, s, s_2, client=None):
        type = CommentType.from_value(s[i.COMMENT_TYPE])

        color_string = s.get(i.COMMENT_COLOR, '255,255,255')
        color = Colour.from_rgb(*map(int, color_string.split(',')))

        return Comment(
            body = b64.b64decode(mapper_util.normalize(s[i.COMMENT_BODY])).decode(),
            rating = s[i.COMMENT_RATING],
            timestamp = s[i.COMMENT_TIMESTAMP],
            id = s[i.COMMENT_ID],
            is_spam = bool(s.get(i.COMMENT_IS_SPAM, 0)),
            type = type,
            color = color,
            level_id = s.get(i.COMMENT_LEVEL_ID, 0),
            level_percentage = s.get(i.COMMENT_LEVEL_PERCENTAGE, -1),
            author = ClassConverter.abstractuser_convert(s_2, client),
            client = client
        )

    @classmethod
    def abstractuser_convert(cls, d, client=None):
        from_dict = {k: convert_to_type(v, int) for k, v in d.items()}
        return AbstractUser(**from_dict).attach_client(client)
