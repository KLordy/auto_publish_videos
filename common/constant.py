import enum


class TencentZoneTypes(enum.Enum):
    LIFESTYLE = '生活'
    CUTE_KIDS = '萌娃'
    MUSIC = '音乐'
    KNOWLEDGE = '知识'
    EMOTION = '情感'
    TRAVEL_SCENERY = '旅行风景'
    FASHION = '时尚'
    FOOD = '美食'
    LIFE_HACKS = '生活技巧'
    DANCE = '舞蹈'
    MOVIES_TV_SHOWS = '影视综艺'
    SPORTS = '运动'
    FUNNY = '搞笑'
    CELEBRITIES = '明星名人'
    NEWS_INFO = '新闻资讯'
    GAMING = '游戏'
    AUTOMOTIVE = '车'
    ANIME = '二次元'
    TALENT = '才艺'
    CUTE_PETS = '萌宠'
    INDUSTRY_MACHINERY_CONSTRUCTION = '机械'
    ANIMALS = '动物'
    PARENTING = '育儿'
    TECHNOLOGY = '科技'


class VideoStatus(enum.Enum):
    INIT = "init"
    PENDING = "pending"
    DEDUPLICATED = "deduplicated"
    PUBLISHED = "published"
