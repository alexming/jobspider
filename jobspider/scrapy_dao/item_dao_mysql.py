# -*- coding: utf-8 -*-


from jobspider.scrapy_dao.item_dao import ItemDao


class ItemDaoMysql(ItemDao):

    def object2sql(self):
        command = 'insert ignore into %s(' % self.StoreTable
        for field in self.fields:
            command += '%s,' % field
        command = command[0: -1]
        command += ') values ('
        for field in self.fields:
            if type(self[field]) in [str, unicode]:
                command += "'%s'," % self[field]
            elif type(self[field]) == int:
                command += '%d,' % self[field]
            elif type(self[field]) == float:
                command += '%f,' % self[field]
            elif type(self[field]) == bool:
                try:
                    command += '%s,' % ('1' if self[field] else '0',)
                except:
                    print field
            elif type(self[field]) == datetime:
                command += "'%s'," % self[field].strftime('%Y/%m/%d %H:%M:%S')
            else:
                command += "'%s'," % self[field]
        command = command[0: -1]
        command += ')'
        return command


class ItemDaoReplaceMysql(ItemDao):

    def object2sql(self):
        command = 'replace into %s(' % self.StoreTable
        for field in self.fields:
            command += '%s,' % field
        command = command[0: -1]
        command += ') values ('
        for field in self.fields:
            if type(self[field]) in [str, unicode]:
                command += "'%s'," % self[field]
            elif type(self[field]) == int:
                command += '%d,' % self[field]
            elif type(self[field]) == float:
                command += '%f,' % self[field]
            elif type(self[field]) == bool:
                try:
                    command += '%s,' % ('1' if self[field] else '0',)
                except:
                    print field
            elif type(self[field]) == datetime:
                command += "'%s'," % self[field].strftime('%Y/%m/%d %H:%M:%S')
            else:
                command += "'%s'," % self[field]
        command = command[0: -1]
        command += ')'
        return command
