# -*- coding: utf-8 -*-


from scrapy import Field
from jobspider.scrapy_dao.item_dao_mysql import ItemDaoMysql


#58同城教育信息存储结构
class WubaEnterprice(ItemDaoMysql):

    category = Field()
    category_name = Field()
    city = Field()
    cityname = Field()
    title = Field()
    publish = Field()
    click_times = Field()
    book_num = Field()
    comment_num = Field()
    company_name = Field()
    auth_title = Field()
    company_address = Field()
    shop_id = Field()
    shop_url = Field()
    telnum = Field()
    contact = Field()
    info_id = Field()
    src_url = Field()
    username = Field()
    course = Field()
    form = Field()
    area_name = Field()
    stage = Field()
    teacher_grade = Field()
    address = Field()
    lat = Field()
    lon = Field()
    desc_area = Field()
    images = Field()
    #
    DBKey = 'GSX'
    StoreTable = 'WubaEnterprice'

#58教育机构信息存储结构
class WubaShop(ItemDaoMysql):

    shop_id = Field()
    shop_name = Field()
    telphone = Field()
    registe_time = Field()
    open_time = Field()
    route = Field()
    description = Field()
    address = Field()
    lat = Field()
    lon = Field()
    #
    DBKey = 'GSX'
    StoreTable = 'wuba_school'

#58评论信息存储结构
class WubaComment(ItemDaoMysql):

    shop_id = Field()
    user_name = Field()
    c_time = Field()
    content = Field()
    #
    DBKey = 'GSX'
    StoreTable = 'wuba_comment'

if __name__ == '__main__':
    wb = WubaEnterprice()
    print wb.object2sql()
    if hasattr(wb, 'default2store'):
        print 'default2store'
