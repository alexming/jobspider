# -*- coding: utf-8 -*-


from scrapy import Field
from jobspider.scrapy_dao.item_dao_mysql import ItemDaoMysql


class Job(ItemDaoMysql):

    id = Field()
    title = Field()
    content = Field()
    time = Field()
    status = Field()
    recommend = Field()
    poster_name = Field()
    sex = Field()
    workplace = Field()
    salary = Field()
    payment = Field()
    population = Field()
    worktime = Field()
    dis = Field()
    city_name = Field()
    area_name = Field()
    salary_num = Field()
    salary_text = Field()
    zjz_id = Field()
    zjz_name = Field()
    zjz_list_icon = Field()
    zjz_detail_icon = Field()
    tel = Field()
    contact = Field()

    DBKey = 'GSX'
    StoreTable = 'xiaolianbang_job'
