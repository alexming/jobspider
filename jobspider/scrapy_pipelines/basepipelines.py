# -*- coding: utf-8 -*-


class BasePipelines(object):

    def process_item(self, item, spider):

        if hasattr(item, 'default2store'):
            item.default2store()
        else:
            log.msg(u'spider=[%s],item=[%s]不支持[default2store]接口,无法通过管道.' % (spider.name, item.__class__.__name__), level=log.ERROR)
            return None

        return item
