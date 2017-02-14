# -*- coding: utf-8 -*-


from scrapy import Field
from jobspider.scrapy_dao.item_dao_mysql import ItemDaoMysql


class Book(ItemDaoMysql):

    sitename = Field()
    brand = Field()
    product_id = Field()
    original_price = Field()
    sale_price = Field()
    discount = Field()
    product_name = Field()
    subname = Field()
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
    publish_standard_id = Field()
    #
    abstract = Field()
    images = Field()
    images_big = Field()
    catalog = Field()
    recommendation = Field()
    more_information = Field()
    #
    publish_barcode = Field()
    publish_product_size2 = Field()
    publish_product_weight = Field()

    DBKey = 'GSX'
    StoreTable = 'dangdang_book_v2'

    def __init__(self):
        super(Book, self).__init__()
        self['sitename'] = 'amazon'

class Category(ItemDaoMysql):
    sitename = Field()
    product_id = Field()
    category_path = Field()
    path_name = Field()

    DBKey = 'GSX'
    StoreTable = 'dangdang_book_category'

    def __init__(self):
        super(Category, self).__init__()
        self['sitename'] = 'amazon'

class Review(ItemDaoMysql):

    sitename = Field()
    product_id = Field()
    product_name = Field()
    review_id = Field()
    creation_date = Field()
    full_star = Field()
    cust_name = Field()
    total_feedback_num = Field()
    total_helpful_num = Field()
    title = Field()
    body = Field()

    DBKey = 'GSX'
    StoreTable = 'dangdang_comment'

    def __init__(self):
        super(Review, self).__init__()
        self['sitename'] = 'amazon'
        self['total_feedback_num'] = 0
        self['total_helpful_num'] = 0
