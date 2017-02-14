# -*- encoding=utf-8 -*-


import json
from scrapy import Request, log, Selector
from jobspider.spiders.education.dangdang_items import Product, Category, Review
from jobspider.spiders.base_spider import BaseSpider
from jobspider.utils.tools import FmtSQLCharater


class DangDangSpider(BaseSpider):

    name = 'education.dangdang'

    headers = {
        'host': 'mapi.dangdang.com',
        'Accept-Encoding': 'gzip',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Dangdang-android'
    }

    list_url = 'http://mapi.dangdang.com/index.php?permanent_id=&timestamp=1440494371&img_size=b&page_size=200&union_id=537-300055-0&user_client=android&page=<?page?>&sort_type=default_0&action=list_category&time_code=43621d17e133d9b9d55d07c1a4b6d944&udid=37607752567198332df0745d1f056a79&cid=01.41.<?age?>.<?cat?>.00.00&client_version=5.9.9'

    info_url = 'http://mapi.dangdang.com/index.php?permanent_id=&timestamp=1440493785&img_size=b&union_id=537-300055-0&user_client=android&action=get_product&time_code=1ce1499e47391067c188d42492e95b4c&expand=1,2,3,4,5,6&pid=<?pid?>&udid=37607752567198332df0745d1f056a79&is_abtest=0&client_version=5.9.9'

    review_url = 'http://mapi.dangdang.com/index.php?permanent_id=&timestamp=1440494177&pagesize=10&union_id=537-300055-0&user_client=android&product_id=<?pid?>&page=<?page?>&action=get_product_reviews&time_code=61efb17459d56f2c9d43272c4d71ae5c&filtertype=1&udid=37607752567198332df0745d1f056a79&review_cust_img_size=g&client_version=5.9.9'

    #依据年龄分类
    all_category = [
        {'id':'01','name': u'0~2岁','list': [
            {'id':'16','name': u'图画故事'},
            {'id':'11','name': u'认知'},
            {'id':'13','name': u'益智/游戏'},
            {'id':'21','name': u'纸板书'},
            {'id':'19','name': u'入园准备'},
            {'id':'15','name': u'童谣'},
            {'id':'14','name': u'艺术课堂'}]},
        {'id':'02','name': u'3~6岁','list': [
            {'id':'19','name': u'卡通/动漫/图画书'},
            {'id':'20','name': u'科普/百科'},
            {'id':'13','name': u'益智游戏'},
            {'id':'15','name': u'文学'},
            {'id':'22','name': u'少儿英语'},
            {'id':'21','name': u'入学准备'},
            {'id':'17','name': u'艺术课堂'},
            {'id':'12','name': u'玩具书'},
            {'id':'11','name': u'认知'}]},
        {'id':'03','name': u'6~10岁','list': [
            {'id':'11','name': u'文学'},
            {'id':'19','name': u'科普/百科'},
            {'id':'17','name': u'卡通/动漫/图画书'},
            {'id':'06','name': u'童话'},
            {'id':'22','name': u'少儿英语'},
            {'id':'21','name': u'励志/成长'},
            {'id':'05','name': u'益智游戏'},
            {'id':'13','name': u'艺术课堂'},
            {'id':'15','name': u'游戏/手工'},
            {'id':'04','name': u'玩具书'}]},
        {'id':'04','name': u'11~14岁','list': [
            {'id':'11','name': u'文学'},
            {'id':'17','name': u'科普百科'},
            {'id':'15','name': u'动漫/图画书'},
            {'id':'06','name': u'童话'},
            {'id':'21','name': u'励志/成长'},
            {'id':'22','name': u'少儿英语'},
            {'id':'05','name': u'益智游戏'},
            {'id':'14','name': u'游戏/手工'},
            {'id':'13','name': u'艺术课堂'},
            {'id':'04','name': u'玩具书'}]},
        {'id':'27','name': u'外国儿童文学','list':[
            {'id':'03','name': u'成长/校园小说'},
            {'id':'09','name': u'幻想小说'},
            {'id':'01','name': u'童话故事'},
            {'id':'07','name': u'侦探/冒险小说'},
            {'id':'02','name': u'桥梁书'},
            {'id':'11','name': u'经典名著少儿版'},
            {'id':'05','name': u'动物小说'},
            {'id':'15','name': u'寓言/传说'},
            {'id':'13','name': u'诗歌/散文'},
            {'id':'17','name': u'传记文学'}]},
        {'id':'41','name': u'精装图画书','list':[
            {'id':'05','name': u'欧美'},
            {'id':'03','name': u'日韩'},
            {'id':'01','name': u'中国原创'}]},
        {'id':'43','name': u'平装图画书','list':[
            {'id':'05','name': u'欧美'},
            {'id':'03','name': u'日韩'},
            {'id':'01','name': u'中国原创'}]},
        {'id':'05','name': u'科普/百科','list':[
            {'id':'03','name': u'科普'},
            {'id':'01','name': u'百科'},
            {'id':'07','name': u'历史读物'},
            {'id':'05','name': u'数学'},
            {'id':'09','name': u'生活常识'}]},
        {'id':'44','name': u'婴儿读物','list':[
            {'id':'07','name': u'图画故事书'},
            {'id':'01','name': u'认知书'},
            {'id':'09','name': u'游戏书'},
            {'id':'13','name': u'纸板书'},
            {'id':'03','name': u'挂图卡片'},
            {'id':'11','name': u'入园准备'},
            {'id':'05','name': u'儿歌童谣'}]},
        {'id':'45','name': u'幼儿启蒙','list':[
            {'id':'03','name': u'图画故事'},
            {'id':'13','name': u'数学/汉语'},
            {'id':'09','name': u'美术/书法'},
            {'id':'05','name': u'幼儿园教材及入学准备'},
            {'id':'01','name': u'认知'},
            {'id':'07','name': u'音乐/舞蹈'},
            {'id':'11','name': u'国学启蒙'}]},
        {'id':'46','name': u'益智游戏','list':[
            {'id':'07','name': u'互动游戏书'},
            {'id':'17','name': u'贴纸游戏书'},
            {'id':'11','name': u'左右脑开发'},
            {'id':'09','name': u'创意手工书'},
            {'id':'05','name': u'视觉大发现'},
            {'id':'13','name': u'迷宫&谜语'},
            {'id':'15','name': u'脑筋急转弯'}]},
        {'id':'48','name': u'玩具书','list':[
            {'id':'03','name': u'翻翻书'},
            {'id':'01','name': u'立体书'},
            {'id':'02','name': u'触摸/洞洞/手偶书'},
            {'id':'04','name': u'发声/多媒体/乐器书'},
            {'id':'07','name': u'其他'},
            {'id':'05','name': u'拼图书'},
            {'id':'06','name': u'洗澡/塑料/汽车书'}]},
        {'id':'50','name': u'动漫/卡通','list':[
            {'id':'05','name': u'漫画'},
            {'id':'03','name': u'卡通'},
            {'id':'07','name': u'连环画'}]},
        {'id':'51','name': u'少儿英语','list':[
            {'id':'05','name': u'少儿英语读物'},
            {'id':'13','name': u'双语读物'},
            {'id':'01','name': u'幼儿启蒙英语'},
            {'id':'03','name': u'少儿英语教程'},
            {'id':'11','name': u'英语歌谣'},
            {'id':'07','name': u'少儿英语考试'},
            {'id':'09','name': u'少儿英语字典'},
            {'id':'15','name': u'其他语种'}]},
        {'id':'57','name': u'进口儿童书','list':[
            {'id':'47','name': u'3-6岁'},
            {'id':'05','name': u'Stories 图画故事书'},
            {'id':'07','name': u'Picture Book 绘本'},
            {'id':'49','name': u'7-10岁'},
            {'id':'17','name': u'Popular Fiction 流行小说'},
            {'id':'51','name': u'11-14岁'},
            {'id':'13','name': u'Leveled Readers 分级阅读'},
            {'id':'25','name': u'Learn with Fun 学习用书'},
            {'id':'23','name': u'Science & Nature 科普、百科'},
            {'id':'01','name': u'Novelty 玩具书/趣味认知书'},
            {'id':'45','name': u'0-2岁'},
            {'id':'21','name': u'Classic Fiction 经典小说'},
            {'id':'03','name': u'Read to Me 幼儿故事书'},
            {'id':'19','name': u'Award Fiction 获奖小说'},
            {'id':'15','name': u'Early Chapters 桥梁书'},
            {'id':'09','name': u'Nursery Rhym & Poem 童谣、诗歌'},
            {'id':'53','name': u'Young Adult'},
            {'id':'27','name': u'Reference 工具书'},
            {'id':'55','name': u'其他年龄'},
            {'id':'31','name': u'Biography 传记'},
            {'id':'29','name': u'Cartoons & Comics 卡通、漫画'},
            {'id':'37','name': u'For Mothers 给妈妈们'},
            {'id':'11','name': u'Activities 益智游戏'},
            {'id':'39','name': u'港台图书'},
            {'id':'35','name': u'Art 艺术'},
            {'id':'43','name': u'其他'},
            {'id':'33','name': u'Self-help 心理'},
            {'id':'41','name': u'French 法语书'}]},
        {'id':'69','name': u'少儿期刊','list':[
            {'id':'02','name': u'幼儿启蒙'},
            {'id':'01','name': u'婴儿读物'},
            {'id':'05','name': u'科普/百科'},
            {'id':'06','name': u'卡通/动漫'},
            {'id':'04','name': u'儿童文学'},
            {'id':'08','name': u'课外辅导'},
            {'id':'10','name': u'女孩'},
            {'id':'07','name': u'少儿英语'},
            {'id':'03','name': u'益智游戏'},
            {'id':'09','name': u'励志/成长'},
            {'id':'11','name': u'孕产育儿期刊'}]}
         ]

    current_age = 0
    current_cat = 0

    def start_requests(self):

        if self.current_age == len(self.all_category) and self.current_cat == len(self.all_category[self.current_age]['list']):
            log.msg(u'抓取完成,即将退出')
            return
        #
        age = self.all_category[self.current_age]
        cat = age['list'][self.current_cat]
        yield Request(
	        url=self.list_url.replace('<?page?>', '1').replace('<?age?>', age['id']).replace('<?cat?>', cat['id']),
	        callback=self.parse_list,
            headers=self.headers,
	        meta={'page': 1, 'age': age, 'cat': cat}
        )
        self.current_cat += 1
        if self.current_cat == len(self.all_category[self.current_age]['list']):
            self.current_age += 1
            self.current_cat = 0


    def parse_list(self, response):
        data = response.body
        if data == '' or data == '[]':
            log.msg(format= '%(request)s post fail.response is [].', level = log.ERROR, request = response.url)
            return
        age = response.meta['age']
        cat = response.meta['cat']
        try:
            js = json.loads(data)
        except:
            log.msg(u'图书类别[%s]-[%s]列表请求结果解析异常,非json数据.url=%s' % (age['name'], cat['name'], response.url), level = log.INFO)
            return
        #
        log.msg(u'图书类别[%s]-[%s]页码[%d]总数=%d,开始请求详情...' % (age['name'], cat['name'], response.meta['page'], len(js['products'])))
        for item in js['products']:
            #
            '''
            pc = Category()
            pc['product_id'] = item['id']
            pc['category_path'] = '01.41.%s.%s.00.00' % (age['id'], cat['id'])
            pc['path_name'] = cat['name']
            yield pc

            #详情请求
            yield Request(
                url=self.info_url.replace('<?pid?>', item['id']),
                callback=self.parse_info,
                headers=self.headers,
                meta={'age': age, 'cat': cat}
            )
            '''
            #评论请求            
            yield Request(
                url=self.review_url.replace('<?pid?>', item['id']).replace('<?page?>', '1'),
                callback=self.parse_review,
                headers=self.headers,
                meta={'page': 1, 'pid': item['id']}
            )
            
        #下一页
        if len(js['products']) >= 200:
            page = response.meta['page'] + 1
            log.msg(u'请求类别[%s]-[%s]的第%d页' % (age['name'], cat['name'], page))
            yield Request(
	            url=self.list_url.replace('<?page?>', str(page)).replace('<?age?>', age['id']).replace('<?cat?>', cat['id']),
	            callback=self.parse_list,
                headers=self.headers,
	            meta={'page': page, 'age': age, 'cat': cat}
            )

    def parse_info(self, response):
        data = response.body
        if data == '' or data == '[]':
            log.msg(format= '%(request)s post fail.response is [].', level = log.ERROR, request = response.url)
            return
        try:
            js = json.loads(data)
        except:
            log.msg(u'图书详情[%s]请求结果解析异常,非json数据.url=%s' % (response.meta['p']['id'], response.url), level = log.INFO)
            return
        #
        pin = js['product_info_new']
        pd = js['product_desc']
        pds = js['product_desc_sorted']
        p = Product()
        #
        for (key, value) in pin.iteritems():
            if key == 'mobile_exclusive_price':
                continue
            elif key == 'shop_id':
                continue
            elif key == 'product_name':
                p[key] = FmtSQLCharater(value)
            elif key == 'outlets':
                continue
            elif key == 'publish_info':
                for (key1, value1) in value.iteritems():
                    if key1 == 'author_arr':
                        continue
                    else:
                        if key1 == 'author_name':
                            p['publish_' + key1] = FmtSQLCharater(value1)
                        else:
                            p['publish_' + key1] = value1
            elif key == 'promo_model':
                continue
            elif key == 'stock_info':
                p['stock_status'] = value['stock_status']
            elif key == 'category_info':
                continue
            elif key == 'comm_info':
                for (key1, value1) in value.iteritems():
                    if key1 == 'items':
                        continue
                    else:
                        p['comm_' + key1] = value1
            elif key == 'total_review_count':
                continue
            elif key == 'abstract':
                p[key] = FmtSQLCharater(value)
            elif key == 'images':
                p['images'] = '#'.join(value)
            elif key == 'images_big':
                p['images_big'] = '#'.join(value)
            elif key == 'stars':
                p['stars_full_star'] = value['full_star']
                p['stars_has_half_star'] = value['has_half_star']
            elif key == 'ebook_info':
                p['ebook_read_ebook_at_h5'] = value['read_ebook_at_h5']
                p['ebook_is_client_buy'] = value['is_client_buy']
            elif key == 'is_yb_product':
                continue
            elif key == 'is_show_arrive':
                continue
            elif key == 'share_url':
                continue
            elif key == 'spuinfo':
                if value != '':
                    p['spuinfo_num'] = value['num']
                    p['spuinfo_spus_id'] = value['spus_id']
            elif key == 'bd_promo_price':
                continue
            elif key == 'template_id':
                continue
            elif key == 'bang_rank':
                p['bang_rank_word'] = value['word']
                p['bang_rank_path_name'] = value['path_name']
                p['bang_rank_rank'] = value['rank']
                p['bang_rank_catPath'] = value['catPath']
            elif key == 'same_cate_product':
                continue
            elif key == 'show_dangdangsale':
                continue
            elif key == 'in_wishlist':
                continue
            elif key == 'page_template':
                continue
            elif key == 'platform_banner':
                continue
            else:
                p[key] = value
        #
        for (key, value) in pd.iteritems():
            p[key] = FmtSQLCharater(value)
            if key == 'beautiful_image':
                hxs = Selector(None, value)
                images = hxs.xpath('//body/img/@src').extract()
                p['beautiful_image_list'] = '#'.join(images)
        #
        for item in pds:
            if item['name'] == u'推荐语':
                p['recommendation'] = FmtSQLCharater(item['content'])
            elif item['name'] == u'简介':
                p['brief_introduction'] = FmtSQLCharater(item['content'])
            #elif item['name'] == u'目录':
            #    p['catalog'] = item['content']
            elif item['name'] == u'出版信息':
                continue
            elif item['name'] == u'更多':
                p['more_information'] = FmtSQLCharater(item['content'])
        #
        yield p

    def parse_review(self, response):
        data = response.body
        if data == '' or data == '[]':
            log.msg(format= '%(request)s post fail.response is [].', level = log.ERROR, request = response.url)
            return
        try:
            js = json.loads(data)
        except:
            log.msg(u'图书[%s]评论页码[%d]请求结果解析异常,非json数据.url=%s' % (response.meta['pid'], response.meta['page'], response.url), level = log.INFO)
            return
        if js.has_key('review_list') and js['review_list'] is not None:
            log.msg(u'评论请求职位ID[%s]的第%d页,总数=%d' % (response.meta['pid'], response.meta['page'], len(js['review_list'])))
            for review in js['review_list']:
                r = Review()
                r['product_name'] = FmtSQLCharater(js['product']['name'])
                for (key, value) in review.iteritems():
                    if key == 'stars':
                        r['full_star'] = value['full_star']
                        r['has_half_star'] = value['has_half_star']
                    elif key in ('experience_ids', 'point_items'):
                        continue
                    elif key in ('body', 'title'):
                        r[key] = FmtSQLCharater(value)
                    else:
                        r[key] = value
                yield r
            #下一页
            if js['pageinfo'].has_key('next'):
                pid = response.meta['pid']
                page = js['pageinfo']['next']
                log.msg(u'评论请求职位ID[%s]的第%d页' % (pid, page))
                yield Request(
                    url=self.review_url.replace('<?pid?>', pid).replace('<?page?>', str(page)),
                    callback=self.parse_review,
                    headers=self.headers,
                    meta={'page': page, 'pid': pid}
                )
