# -*- coding: utf-8 -*-


from scrapy import Field
from jobspider.scrapy_dao.item_dao_mysql import ItemDaoReplaceMysql


# 不得姐存储结构定义
class Topic(ItemDaoReplaceMysql):

    DBKey = 'BuDejie'
    StoreTable = 'topic'
    # fields
    id = Field()
    type = Field()
    text = Field()
    user_id = Field()
    create_time = Field()
    passtime = Field()
    comment = Field()
    love = Field()
    hate = Field()
    repost = Field()
    bookmark = Field()
    bimageuri = Field()
    is_gif = Field()
    voiceuri = Field()
    voicetime = Field()
    voicelength = Field()
    status = Field()
    theme_id = Field()
    theme_type = Field()
    theme_name = Field()
    videouri = Field()
    videotime = Field()
    original_pid = Field()
    cache_version = Field()
    playcount = Field()
    playfcount = Field()
    weixin_url = Field()
    image1 = Field()
    image0 = Field()
    image2 = Field()
    cdn_img = Field()
    image_small = Field()
    width = Field()
    height = Field()
    tag = Field()
    t = Field()
    top_cmt = Field()
    themes = Field()


class User(ItemDaoReplaceMysql):

    DBKey = 'BuDejie'
    StoreTable = 'user'
    # fields
    user_id = Field()
    name = Field()
    screen_name = Field()
    profile_image = Field()
    sex = Field()
    personal_page = Field()
    weibo_uid = Field()
    qq_uid = Field()

class Comment(ItemDaoReplaceMysql):

    DBKey = 'BuDejie'
    StoreTable = 'comment'
    # fields
    id = Field()
    content = Field()
    ctime = Field()
    like_count = Field()
    precid = Field()
    preuid = Field()
    voiceuri = Field()
    voicetime = Field()

class Theme(ItemDaoReplaceMysql):

    DBKey = 'BuDejie'
    StoreTable = 'theme'
    # fields
    theme_id = Field()
    theme_name = Field()
    theme_type = Field()
    image_list = Field()
    sub_number = Field()
    is_sub = Field()
    is_default = Field()
