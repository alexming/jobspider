# -*- coding: utf-8 -*-


from scrapy import Field
from jobspider.scrapy_dao.item_dao_mysql import ItemDaoMysql


class Book(ItemDaoMysql):

    sitename = Field()
    product_id = Field()
    original_price = Field()
    sale_price = Field()
    discount = Field()
    product_name = Field()
    category_id = Field()
    cat_age = Field()
    age = Field()
    #
    publish_publisher = Field()
    publish_author_name = Field()
    publish_product_size = Field()
    publish_print_copy = Field()
    publish_paper_quality = Field()
    publish_publish_date = Field()
    publish_number_of_pages = Field()
    publish_version_num = Field()
    publish_subtitle_language = Field()
    publish_binding = Field()
    publish_standard_id = Field()
    #
    abstract = Field()
    images = Field()
    images_big = Field()
    authorintro = Field()
    catalog = Field()
    content = Field()
    extract = Field()
    recommendation = Field()
    brief_introduction = Field()
    more_information = Field()
    product_features = Field()

    DBKey = 'GSX'
    StoreTable = 'dangdang_book_v2'

    def __init__(self):
        super(Book, self).__init__()
        self['sitename'] = 'jd'


class Review(ItemDaoMysql):

    sitename = Field()
    product_id = Field()
    product_name = Field()
    review_id = Field()
    creation_date = Field()
    score = Field()
    cust_name = Field()
    cust_lev = Field()
    cust_level_simple = Field()
    cust_img = Field()
    total_feedback_num = Field()
    total_helpful_num = Field()
    title = Field()
    body = Field()
    comment_tags = Field()
    images = Field()

    DBKey = 'GSX'
    StoreTable = 'dangdang_comment'

    def __init__(self):
        super(Review, self).__init__()
        self['sitename'] = 'jd'
