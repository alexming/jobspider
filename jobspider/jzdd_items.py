# -*- coding: utf-8 -*-


from scrapy import Field
from jobspider.scrapy_dao.item_dao_mysql import ItemDaoMysql


class Job(ItemDaoMysql):

    jid = Field()
    jnumber = Field()
    jtitle = Field()
    mtagstr = Field()
    retag = Field()
    jzhiding = Field()
    jdanweism = Field()
    junit = Field()
    jzhiwei = Field()
    jclass = Field()
    jnum = Field()
    jcouldnum = Field()
    jalreadyNum = Field()
    sjnan = Field()
    jsex = Field()
    jhealth = Field()
    jutixuqiu = Field()
    jsalary = Field()
    jworktime = Field()
    jaddress = Field()
    jworkneir = Field()
    jpoint = Field()
    yuelxt = Field()
    jiviewtime = Field()
    mianstimestr = Field()
    jmsaddress = Field()
    areastr = Field()
    jdetail = Field()
    jtel = Field()
    jqq = Field()
    jaddtime = Field()
    jcount = Field()
    jauthor = Field()
    jtags = Field()
    jzleixing = Field()
    updatetime = Field()
    topendtime = Field()
    jobsbumen = Field()
    paixucount = Field()
    quyustr = Field()
    jclassb = Field()
    jauthortag = Field()
    tutag = Field()
    elogo = Field()
    quyu = Field()
    jiesuan = Field()
    mian = Field()
    hui = Field()
    tui = Field()
    wang = Field()
    ren = Field()
    gao = Field()
    category_title = Field()
    company_name = Field()
    user_uname = Field()
    uid = Field()

    DBKey = 'GSX'
    StoreTable = 'jzdd_job'

