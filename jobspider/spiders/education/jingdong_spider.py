# -*- coding: utf-8 -*-


import json
from scrapy import Request, log, Selector
from jobspider.spiders.education.jingdong_items import Book, Review
from jobspider.spiders.base_spider import BaseSpider
from jobspider.utils.tools import FmtSQLCharater, first_item


class JingDongSpider(BaseSpider):

    name = 'education.jingdong'

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.130 Safari/537.36'
    }

    list_url = 'http://list.jd.com/list.html?cat=1713,3263,<?cat?>&page=<?page?>&JL=<?age?>'

    info_url = 'http://item.jd.com/<?sku?>.html'

    desc_url = 'http://d.3.cn/desc/<?sku?>'

    price_url = 'http://p.3.cn/prices/mgets?skuIds=J_<?sku?>'

    review_url = 'http://s.club.jd.com/productpage/p-<?sku?>-s-0-t-0-p-<?page?>.html'

    #书籍类别
    all_category = [
        {'id':3394, 'name': u'儿童文学'},
        {'id':3399, 'name': u'科普/百科'},
        {'id':4761, 'name': u'绘本'},
        {'id':3396, 'name': u'手工/游戏'},
        {'id':3395, 'name': u'幼儿启蒙'},
        {'id':3398, 'name': u'智力开发'},
        {'id':3391, 'name': u'动漫/卡通'},
        {'id':12081, 'name': u'玩具书'},
        {'id':3400, 'name': u'励志/成长'},
        {'id':3393, 'name': u'儿童教育'},
        {'id':3397, 'name': u'音乐/舞蹈'},
        {'id':4762, 'name': u'美术/书法'},
        {'id':3392, 'name': u'少儿国学'},
        {'id':3401, 'name': u'少儿英语'},
        {'id':4760, 'name': u'笑话/幽默'},
        {'id':4763, 'name': u'入园准备及教材'},
        {'id':12411, 'name': u'儿童期刊'}
    ]

    #阅读年龄
    all_age = [
        {'id': u'3_年龄_0-2岁', 'name': u'0~2岁'},
        {'id': u'3_年龄_3-6岁', 'name': u'3~6岁'},
        {'id': u'3_年龄_7-10岁', 'name': u'7~10岁'},
        {'id': u'3_年龄_11-14岁', 'name': u'11~14岁'}
    ]

    current_cat_age = {'cat': 0, 'age': 0}

    def start_requests(self):

        if self.current_cat_age['cat'] == len(self.all_category) or self.current_cat_age['age'] == len(self.all_age):
            log.msg(u'抓取完成,即将退出')
            return
        #
        category = self.all_category[self.current_cat_age['cat']]
        age = self.all_age[self.current_cat_age['age']]
        yield Request(
            url=self.list_url.replace('<?page?>', '1').replace('<?cat?>', str(category['id'])).replace('<?age?>', age['id']),
            callback=self.parse_list,
            headers=dict({'Host': 'list.jd.com'}, **self.headers),
            meta={'page': 1, 'category': category, 'age': age}
        )
        self.current_cat_age['age'] += 1
        if self.current_cat_age['age'] == len(self.all_age):
            self.current_cat_age['cat'] += 1
            self.current_cat_age['age'] = 0

    def parse_list(self, response):
        data = response.body
        if data == '':
            log.msg(format= '%(request)s post fail.response is empty.', level = log.ERROR, request = response.url)
            return
        category = response.meta['category']
        age = response.meta['age']
        hxs = Selector(None, data)
        #
        plist = hxs.xpath("//li/div/div[@class='gl-i-wrap j-sku-item']")
        log.msg(u'类别[%s]年龄[%s]页码[%d]总数=%d,开始请求详情...' % (category['name'], age['name'], response.meta['page'], len(plist)))
        for item in plist:
            sku = first_item(item.xpath('@data-sku').extract())
            '''
            #请求详情
            yield Request(
                url=self.info_url.replace('<?sku?>', sku),
                callback=self.parse_info,
                headers=dict({'Host': 'item.jd.com', 'Upgrade-Insecure-Requests': '1'}, **self.headers),
                meta={'category': category, 'age': age, 'sku': sku}
            )
            '''
            #请求评论
            yield Request(
                url=self.review_url.replace('<?sku?>', sku).replace('<?page?>', '1'),
                callback=self.parse_review,
                headers=self.headers,
                meta={'page': 1, 'sku': sku}
            )

        #下一页
        if len(plist) == 60:
            page = response.meta['page'] + 1
            log.msg(u'请求类别[%s]年龄[%s]的第%d页' % (category['name'], age['name'], page))
            yield Request(
                url=self.list_url.replace('<?page?>', str(page)).replace('<?cat?>', str(category['id'])).replace('<?age?>', age['id']),
                callback=self.parse_list,
                headers=dict({'Host': 'list.jd.com'}, **self.headers),
                meta={'page': page, 'category': category, 'age': age}
             )

    def parse_info(self, response):
        data = response.body
        if data == '':
            log.msg(format= '%(request)s post fail.response is empty.', level = log.ERROR, request = response.url)
            return
        category = response.meta['category']
        age = response.meta['age']
        data = data.decode('GBK', 'ignore')
        hxs = Selector(None, data)
        #
        p = hxs.xpath("//div[@id='product-intro']")
        preview = p.xpath("div[@id='preview']")
        item = p.xpath("div[@class='m-item-inner']/div[@id='itemInfo']")
        b = Book()
        b['product_id'] = response.meta['sku']
        b['product_name'] = first_item(item.xpath("div[@id='name']/h1/text()").extract())
        b['category_id'] = category['id']
        b['cat_age'] = age['name']
        b['age'] = first_item(item.xpath("div[@id='name']/h1/strong/text()").extract())
        author = item.xpath("div[@id='name']/div[@id='p-author']")
        b['publish_author_name'] = first_item(author.xpath('string(.)').extract())
        b['publish_author_name'] = b['publish_author_name'].replace('\t', '').replace('\r', '').replace('\n', '')
        b['publish_author_name'] = b['publish_author_name'].lstrip().rstrip()
        #images
        images = preview.xpath("div[@id='spec-list']/div[@class='spec-items']/ul/li/img/@src").extract()
        b['images'] = '#'.join(images)
        b['images_big'] = b['images'].replace('/n5/', '/n1/')
        #
        detail = hxs.xpath("//div[@id='product-detail-1']/div[@class='p-parameter']/ul[@class='p-parameter-list']")
        b['publish_publisher'] = first_item(detail.xpath(u"li[contains(text(), '出版社')]/@title").extract())
        b['publish_standard_id'] = first_item(detail.xpath(u"li[contains(text(), 'ISBN')]/@title").extract())
        b['publish_version_num'] = first_item(detail.xpath(u"li[contains(text(), '版次')]/@title").extract())
        b['publish_binding'] = first_item(detail.xpath(u"li[contains(text(), '包装')]/@title").extract())
        b['publish_product_size'] = first_item(detail.xpath(u"li[contains(text(), '开本')]/@title").extract())
        b['publish_publish_date'] = first_item(detail.xpath(u"li[contains(text(), '出版时间')]/@title").extract())
        b['publish_paper_quality'] = first_item(detail.xpath(u"li[contains(text(), '用纸')]/@title").extract())
        b['publish_print_copy'] = first_item(detail.xpath(u"li[contains(text(), '印次')]/@title").extract())
        b['publish_number_of_pages'] = first_item(detail.xpath(u"li[contains(text(), '套装数量')]/@title").extract())
        b['publish_subtitle_language'] = first_item(detail.xpath(u"li[contains(text(), '正文语种')]/@title").extract())

        log.msg(u'请求商品[%s]的描述信息...' % response.meta['sku'])

        yield Request(
            url=self.desc_url.replace('<?sku?>', response.meta['sku']),
            callback=self.parse_desc,
            headers=self.headers,
            meta={'b': b}
        )

    def parse_desc(self, response):
        data = response.body
        data = data.decode('GBK', 'ignore')
        data = data[9: -1]
        try:
            js = json.loads(data)
        except:
            log.msg(u'图书[%s]描述请求结果解析异常,非json数据.url=%s' % (response.meta['b']['product_id'], response.url), level = log.INFO)
            return
        b = response.meta['b']
        hxs = Selector(None, js['content'])
        b['product_features'] = first_item(hxs.xpath("//div[@id='detail-tag-id-1']/div[2]/div[@class='book-detail-content']").extract())
        b['abstract'] = first_item(hxs.xpath("//div[@id='detail-tag-id-2']/div[2]/div[@class='book-detail-content']").extract())
        b['recommendation'] = b['abstract']
        b['content'] = first_item(hxs.xpath("//div[@id='detail-tag-id-3']/div[2]/div[@class='book-detail-content']").extract())
        b['brief_introduction'] = b['content']
        b['authorintro'] = first_item(hxs.xpath("//div[@id='detail-tag-id-4']/div[2]/div[@class='book-detail-content']").extract())
        b['extract'] = first_item(hxs.xpath("//div[@id='detail-tag-id-5']/div[2]/div[@class='book-detail-content']").extract())
        b['catalog'] = first_item(hxs.xpath("//div[@id='detail-tag-id-6']/div[2]/div[@class='book-detail-content']").extract())
        b['more_information'] = first_item(hxs.xpath("//div[@id='detail-tag-id-8']/div[2]/div[@class='book-detail-content']").extract())
        #
        b['abstract'] = FmtSQLCharater(b['abstract'])
        b['catalog'] = FmtSQLCharater(b['catalog'])
        b['recommendation'] = FmtSQLCharater(b['recommendation'])
        b['content'] = FmtSQLCharater(b['content'])
        b['brief_introduction'] = FmtSQLCharater(b['brief_introduction'])
        b['authorintro'] = FmtSQLCharater(b['authorintro'])
        b['extract'] = FmtSQLCharater(b['extract'])
        b['more_information'] = FmtSQLCharater(b['more_information'])

        log.msg(u'请求商品[%s]的价格信息...' % b['product_id'])

        yield Request(
            url=self.price_url.replace('<?sku?>', b['product_id']),
            callback=self.parse_price,
            headers=self.headers,
            meta={'b': b}
        )

    def parse_price(self, response):
        data = response.body
        if data == '':
            log.msg(format= '%(request)s post fail.response is empty.', level = log.ERROR, request = response.url)
            return
        try:
            js = json.loads(data)
        except:
            log.msg(u'图书[%s]价格请求结果解析异常,非json数据.url=%s' % (response.meta['b']['product_id'], response.url), level = log.INFO)
            return
        b = response.meta['b']
        price = js[0]
        b['sale_price'] = price['p']
        b['original_price'] = price['m']
        b['discount'] = int(float(b['sale_price']) / float(b['original_price']) * 100) / 10.0
        #
        log.msg(u'存储商品[%s]的详细信息' % b['product_id'])
        yield b

    def parse_review(self, response):
        data = response.body
        if data == '':
            log.msg(format= '%(request)s post fail.response is empty.', level = log.ERROR, request = response.url)
            return
        try:
            data = data.decode('GBK', 'ignore')
            js = json.loads(data)
        except:
            log.msg(u'图书[%s]评论请求结果解析异常,非json数据.url=%s' % (response.meta['sku'], response.url), level = log.INFO)
            return
        for item in js['comments']:
            r = Review()
            r['product_id'] = item['referenceId']
            r['product_name'] = item['referenceName']
            r['review_id'] = item['id']
            r['title'] = item['title'] if item.has_key('title') else ''
            r['body'] = FmtSQLCharater(item['content'])
            r['creation_date'] = item['creationTime']
            r['score'] = item['score']
            r['cust_name'] = FmtSQLCharater(item['nickname'])
            r['cust_lev'] = item['userLevelName']
            r['cust_level_simple'] = item['userLevelId']
            r['cust_img'] = item['userImageUrl']
            r['comment_tags'] = '#'.join(map(lambda x: x['name'], item['commentTags'])) if item.has_key('commentTags') else ''
            r['images'] = '#'.join(map(lambda x: x['imgUrl'], item['images'])) if item.has_key('images') else ''
            r['total_feedback_num'] = item['replyCount']
            r['total_helpful_num'] = item['usefulVoteCount']
            yield r
        #下一页
        if len(js['comments']) == 10:
            sku = response.meta['sku']
            page = response.meta['page'] + 1
            log.msg(u'请求商品[%s]的第[%d]页评论...' % (sku, page))
            yield Request(
                url=self.review_url.replace('<?sku?>', sku).replace('<?page?>', str(page)),
                callback=self.parse_review,
                headers=self.headers,
                meta={'page': page, 'sku': sku}
            )
