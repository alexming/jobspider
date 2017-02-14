# -*- coding: utf-8 -*-


from scrapy import log


class WubaPipeline:

    def process_item(self, item, spider):

        if hasattr(item, 'default2store'):
            item.default2store()
        else:
            log.msg(u'%s.item不支持default2store接口,无法通过管道.' % spider.name, level=log.ERROR)

        return item
