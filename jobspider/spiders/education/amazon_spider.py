# -*- coding: utf-8 -*-


import re
import urllib2
from scrapy import Request, log, Selector
from jobspider.spiders.education.amazon_items import Book, Category, Review
from jobspider.spiders.base_spider import BaseSpider
from jobspider.scrapy_db.db_pool import TQDbPool
from jobspider.utils.tools import FmtSQLCharater, first_item


class AmazonSpider(BaseSpider):

    name = 'education.amazon'
    #download_delay = 0.5
    #randomize_download_delay = True

    headers = {
        'Host': 'www.amazon.cn',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.130 Safari/537.36'
    }

    list_url = 'http://www.amazon.com/s/ref=sr_pg_2?fst=as:off&rh=n:658390051,n:!658391051,n:658409051,n:<?root?>,n:<?leaf?>,p_72:<?star?>,p_n_age_range:<?age?>&page=<?page?>'

    info_url = 'http://www.amazon.com/gp/product/<?asin?>?showDetailProductDesc=1'

    review_url = 'http://www.amazon.com/product-reviews/<?asin?>/ref=cm_cr_pr_btm_link_2?ie=UTF8&showViewpoints=1&sortBy=helpful&reviewerType=all_reviews&formatType=all_formats&filterByStar=positive&pageNumber=<?page?>'

    #分类
    all_category = [
        {'id':658734051, 'name': u'幼儿启蒙', 'list':[
            {'id': 660488051, 'name': u'幼儿认知'},
            {'id': 660487051, 'name': u'数学算数'},
            {'id': 663611051, 'name': u'识字说话'},
            {'id': 663612051, 'name': u'拼音读物'}]},
        {'id':658735051, 'name': u'儿童文学', 'list':[
            {'id': 660494051, 'name': u'童话故事'},
            {'id': 1441336071, 'name': u'校园/成长小说'},
            {'id': 1441340071, 'name': u'侦探/冒险小说'},
            {'id': 1441341071, 'name': u'幻想小说'},
            {'id': 1441338071, 'name': u'动物小说'},
            {'id': 660496051, 'name': u'神话传说'},
            {'id': 1441319071, 'name': u'诗歌/散文'},
            {'id': 1978360051, 'name': u'少儿版名著'},
            {'id': 1441001071, 'name': u'传记'},
            {'id': 1441332071, 'name': u'寓言/成语故事'},
            {'id': 660498051, 'name': u'童谣/儿歌'}]},
        {'id':658738051, 'name': u'漫画绘本与图画书', 'list':[
            {'id': 1978361051, 'name': u'卡通'},
            {'id': 660523051, 'name': u'漫画'},
            {'id': 660522051, 'name': u'绘本图画书'},
            {'id': 660524051, 'name': u'连环画'}]},
        {'id':658737051, 'name': u'科普百科', 'list':[
            {'id': 660518051, 'name': u'百科全书'},
            {'id': 660508051, 'name': u'动物'},
            {'id': 660509051, 'name': u'植物'},
            {'id': 660511051, 'name': u'历史'},
            {'id': 153389071, 'name': u'人文地理'},
            {'id': 660515051, 'name': u'天文海洋'},
            {'id': 660514051, 'name': u'航天航空'},
            {'id': 660513051, 'name': u'人体奥秘'},
            {'id': 660512051, 'name': u'数理化'},
            {'id': 660516051, 'name': u'科学技术'}]},
        {'id':215166805, 'name': u'少儿英语', 'list':[{'id': 2151668051, 'name': u'少儿英语'}]},
        {'id':660532051, 'name': u'国学启蒙', 'list':[{'id': 660532051, 'name': u'国学启蒙'}]},
        {'id':660536051, 'name': u'音乐舞蹈', 'list':[{'id': 660536051, 'name': u'音乐舞蹈'}]},
        {'id':197836305, 'name': u'绘画书法', 'list':[{'id': 1978363051, 'name': u'绘画书法'}]},
        {'id':660501051, 'name': u'儿童手工', 'list':[{'id': 660501051, 'name': u'儿童手工'}]},
        {'id':658736051, 'name': u'智力游戏', 'list':[{'id': 658736051, 'name': u'智力游戏'}]},
        {'id':660552051, 'name': u'励志与成长', 'list':[{'id': 660552051, 'name': u'励志与成长'}]},
        {'id':660550051, 'name': u'生活知识', 'list':[{'id': 660550051, 'name': u'生活知识'}]},
        {'id':658739051, 'name': u'立体书', 'list':[{'id': 658739051, 'name': u'立体书'}]}
    ]
    #年龄
    all_age = [
        {'id': 2111929051, 'name': u'0-2岁'},
        {'id': 2111930051, 'name': u'3-6岁'},
        {'id': 2111931051, 'name': u'7-10岁'},
        {'id': 2111932051, 'name': u'11-14岁'},
    ]
    #星级
    all_star = [
        {'id': 2039727051, 'name': u'五星级'},
        {'id': 2039714051, 'name': u'四星级'},
        {'id': 2039715051, 'name': u'三星级'},
        {'id': 2039716051, 'name': u'二星级'},
        {'id': 2039717051, 'name': u'一星级'},
    ]
    #
    current_cat_root = 0
    current_cat_leaf = 0
    current_age = 0
    current_star = 0

    def start_requests(self):

        SQLSeedUrl = 'select * from book_20160328 where status=0 and pkid in (44,49,51,58) limit 5'
        idrows = TQDbPool.query('proxy_server',SQLSeedUrl)
        
        for isbnid in idrows:
            TargetUrl = 'http://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=' + str(isbnid['isbn'])
            log.msg(TargetUrl)
            yield Request(
                #url=self.list_url.replace('<?page?>', '1').replace('<?cat?>', str(category['id'])).replace('<?age?>', age['id']),
                url=TargetUrl,
                callback=self.parse_list,
                headers=dict({'Host': ''}, **self.headers),
                meta={'page': 1,'proxy':'http://192.168.1.130:8888'},
                #meta={'page': 1, 'category': category, 'age': age}
            )
            TQDbPool.execute('proxy_server','update book_20160328 set status=1 where pkid=' + str(isbnid['pkid']))
        """
        if self.current_cat_root == len(self.all_category):
            log.msg(u'抓取完成,即将退出')
            return
        #
        root = self.all_category[self.current_cat_root]
        leaf = root['list'][self.current_cat_leaf]
        age = self.all_age[self.current_age]
        star = self.all_star[self.current_star]
        page = 1
        #
        link = self.list_url.replace('<?page?>', str(page))
        link = link.replace('<?root?>', str(root['id']))
        link = link.replace('<?leaf?>', str(leaf['id']))
        link = link.replace('<?age?>', str(age['id']))
        link = link.replace('<?star?>', str(star['id']))
        #
        yield Request(
            url=link,
            callback=self.parse_list,
            headers=dict({'Host': 'list.jd.com'}, **self.headers),
            meta={'page': page, 'root': root, 'leaf': leaf, 'age': age, 'star': star}
        )
        #逐级移动
        self.current_star += 1
        if self.current_star == len(self.all_star):
            self.current_age += 1
            self.current_star = 0
        if self.current_age == len(self.all_age):
            self.current_cat_leaf += 1
            self.current_age = 0
        if self.current_cat_leaf == len(self.all_category[self.current_cat_root]['list']):
            self.current_cat_root += 1
            self.current_cat_leaf = 0
            """

    def parse_list(self, response):
        data = response.body
        if data == '':
            log.msg(format= '%(request)s post fail.response is empty.', level = log.ERROR, request = response.url)
            return
        #
        """
        root = response.meta['root']
        leaf = response.meta['leaf']
        age = response.meta['age']
        star = response.meta['star']
        """
        page = response.meta['page']
        #
        hxs = Selector(None, data)
        #
        plist_a = hxs.xpath("//div[@id='resultsCol']/div[@id='centerMinus']/div[@id='atfResults']/ul[@id='s-results-list-atf']/li")
        plist_b = hxs.xpath("//div[@id='btfResults']/ul/li")
        plist = plist_a + plist_b
        #log.msg(u'类别[图书->少儿->%s->%s->%s->%s]页码[%d]总数=%d,开始请求详情...' % (root['name'], leaf['name'], age['name'], star['name'], page, len(plist)))
        #og.msg(u'Start Request:%s' % plist);
        """
        if len(plist) == 0:
            if data.find(u'verify'):
                log.msg(u'verify ban')
        """
        for item in plist:
            asin = first_item(item.xpath('@data-asin').extract())
            log.msg('Request ASIN Detail Page:' + str(asin))
            #
            """
            c = Category()
            c['product_id'] = asin
            c['category_path'] = 'n:658390051,n:!658391051,n:658409051,n:%d,n:%d,p_72:%d,p_n_age_range:%d' % (root['id'], leaf['id'], star['id'], age['id'])
            c['path_name'] = ' 图书 : 少儿 : %s : %s : %s : %s' % (root['name'], leaf['name'], star['name'], age['name'])
            yield c
            """
            #请求详情
            detailUrl = self.info_url.replace('<?asin?>', asin)
            log.msg('DetailUrl:' + detailUrl)
            yield Request(
                url=self.info_url.replace('<?asin?>', asin),
                callback=self.parse_info,
                headers=self.headers,
                meta={'asin':asin,'proxy':'http://192.168.1.130:8888'},
                #meta={'root': root, 'leaf': leaf, 'age': age, 'star': star, 'asin': asin}
            )
            """
            #请求评论            
            yield Request(
                url=self.review_url.replace('<?asin?>', asin).replace('<?page?>', '1'),
                callback=self.parse_review,
                headers=self.headers,
                meta={'page': 1, 'asin': asin}
            )
            """
            
        """
        #下一页
        if len(plist) == 16:
            page += 1
            log.msg(u'请求类别[图书->少儿->%s->%s->%s->%s]的第[%d]页' % (root['name'], leaf['name'], age['name'], star['name'], page))
            #
            link = self.list_url.replace('<?page?>', str(page))
            link = link.replace('<?root?>', str(root['id']))
            link = link.replace('<?leaf?>', str(leaf['id']))
            link = link.replace('<?age?>', str(age['id']))
            link = link.replace('<?star?>', str(star['id']))
            #
            yield Request(
                url=link,
                callback=self.parse_list,
                headers=dict({'Host': 'list.jd.com'}, **self.headers),
                meta={'page': page, 'root': root, 'leaf': leaf, 'age': age, 'star': star}
             )
        """
    def parse_info(self, response):
        data = response.body
        if data == '':
            log.msg(format= '%(request)s post fail.response is empty.', level = log.ERROR, request = response.url)
            return
        #
        """
        root = response.meta['root']
        leaf = response.meta['leaf']
        age = response.meta['age']
        star = response.meta['star']
        """
        asin = response.meta['asin']
        #
        hxs = Selector(None, data)
        #
        container = hxs.xpath("//div[@class='a-container']")
        right = container.xpath("div[@id='rightCol']")
        left = container.xpath("div[@id='leftCol']")
        center = container.xpath("div[@id='centerCol']")
        #
        log.msg('Book--')
        b = Book()
        b['product_id'] = asin
        b['product_name'] = FmtSQLCharater(first_item(center.xpath("div[@id='booksTitle']/div/h1[@id='title']/span[@id='productTitle']/text()").extract()))
        b['subname'] = b['product_name']
        b['publish_paper_quality'] = FmtSQLCharater(first_item(center.xpath("div[@id='booksTitle']/div/h1[@id='title']/span[2]/text()").extract()))
        author = center.xpath("div[@id='booksTitle']/div[@id='byline']")
        log.msg('author html:' + author.extract())
        b['publish_author_name'] = FmtSQLCharater(first_item(author.xpath('string(.)').extract()))
        b['publish_author_name'] = b['publish_author_name'].replace('\n', '').replace('\t', '').replace(' ', '')
        b['abstract'] = FmtSQLCharater(first_item(hxs.xpath("div[@id='bookDescription_feature_div']/noscript/text()").extract()))
        images = left.xpath("div[@id='booksImageBlock_feature_div']/div[@id='imageBlockOuter']/div[@id='imageBlockThumbs']/span/div/img/@src").extract()
        bigImages = map(lambda x: x.replace('_AC_SY60_CR,0,0,60,60_', '_SY498_BO1,204,203,200_').replace('_AC_SX60_CR,0,0,60,60_', '_SX443_BO1,204,203,200_'), images)
        b['images'] = '#'.join(images)
        b['images_big'] = '#'.join(bigImages)
        #
        buybox = right.xpath("div[@id='buybox_feature_div']/div[@id='combinedBuyBox']/form[@id='addToCart']/div[@id='buybox']/div/div[@class='a-box-inner']/div")
        b['sale_price'] = FmtSQLCharater(first_item(buybox.xpath("//*[@id='a-autoid-5-announce']/span[2]/span").extract()))
        b['discount'] = FmtSQLCharater(first_item(buybox.xpath("div[@id='buyNewSection']/div/div[@id='soldByThirdParty']/span[2]/text()").extract()))
        b['original_price'] = FmtSQLCharater(first_item(buybox.xpath("//*[@id='a-autoid-4-announce']/span[2]").extract()))
        b['sale_price'] = b['sale_price'].replace('￥', '')
        b['discount'] = b['discount'].replace(' (', '').replace(u'折) ', '')
        b['original_price'] = b['original_price'].replace(u'￥', '')
        #基本信息
        bullets = hxs.xpath("//div[@id='productDetails']/table/tr/td[@class='bucket']/div[@class='content']/ul/li")
        for li in bullets:
            log.msg('Book-base-info')
            if li.xpath(u"b[contains(text(), 'Publisher')]"):
                publisher = FmtSQLCharater(first_item(li.xpath("text()").extract()).lstrip())
                #未来出版社; 第1版 (2011年11月1日)
                match = re.search(u'(.+); 第(.+)版 \((.+)\)', publisher, re.I|re.M)
                if match:
                    b['publish_publisher'] = match.group(1)
                    b['publish_version_num'] = match.group(2)
                    b['publish_publish_date'] = match.group(3)
            elif li.xpath(u"b[contains(text(), 'Series')]"):
                b['product_name'] = FmtSQLCharater(first_item(li.xpath("a/text()").extract()).lstrip())
            elif li.xpath(u"b[contains(text(), 'Paperback')]"):
                b['publish_paper_quality'] = u'Paperback'
                b['publish_number_of_pages'] = FmtSQLCharater(first_item(li.xpath("text()").extract()).lstrip())
            elif li.xpath(u"b[contains(text(), 'Hardcover')]"):
                b['publish_paper_quality'] = u'Hardcover'
                b['publish_number_of_pages'] = FmtSQLCharater(first_item(li.xpath("text()").extract()).lstrip())
            elif li.xpath(u"b[contains(text(), '纸板书')]"):
                b['publish_paper_quality'] = u'纸板书'
                b['publish_number_of_pages'] = FmtSQLCharater(first_item(li.xpath("text()").extract()).lstrip())
            elif li.xpath(u"b[contains(text(), 'Age Range')]"):
                b['age'] = FmtSQLCharater(first_item(li.xpath("text()").extract()).lstrip())
            elif li.xpath(u"b[contains(text(), 'Language')]"):
                b['publish_subtitle_language'] = FmtSQLCharater(first_item(li.xpath("text()").extract()).lstrip())
            elif li.xpath(u"b[contains(text(), '开本')]"):
                b['publish_product_size'] = FmtSQLCharater(first_item(li.xpath("text()").extract()).lstrip())
            elif li.xpath(u"b[contains(text(), 'ISBN-13')]"):
                b['publish_standard_id'] = FmtSQLCharater(first_item(li.xpath("text()").extract()).lstrip())
            #elif li.xpath(u"b[contains(text(), '条形码')]"):
            #    b['publish_barcode'] = first_item(li.xpath("text()").extract()).lstrip()
            elif li.xpath(u"b[contains(text(), 'Product Dimensions')]"):
                b['publish_product_size2'] = FmtSQLCharater(first_item(li.xpath("text()").extract()).replace('\n', '').lstrip().rstrip())
            elif li.xpath(u"b[contains(text(), 'Shipping Weight')]"):
                b['publish_product_weight'] = FmtSQLCharater(first_item(li.xpath("text()").extract()).replace('\n', '').lstrip().rstrip())
            #elif li.xpath(u"b[contains(text(), '品牌')]"):
            #    b['brand'] = first_item(li.xpath("text()").extract()).lstrip()
        #商品描述
        begin = data.find('var iframeContent =')
        end = data.find('obj.onloadCallback = onloadCallback;')
        if begin and end:
            desc = data[begin + 21: end - 10]
            desc = urllib2.unquote(desc)
            hxs = Selector(None, desc)
            b['recommendation'] = first_item(hxs.xpath(u"//div[@class='content']/h3[contains(text(), '编辑推荐')]/following-sibling::div[1]/text()").extract())
            b['catalog'] = first_item(hxs.xpath(u"//div[@class='content']/h3[contains(text(), '目录')]/following-sibling::div[1]/text()").extract())
            b['more_information'] = first_item(hxs.xpath(u"//div[@class='content']/h3[contains(text(), '文摘')]/following-sibling::div[1]/text()").extract())
        #
        yield b

    def parse_review(self, response):
        hxs = Selector(response)
        asin = response.meta['asin']
        title = FmtSQLCharater(first_item(hxs.xpath('//title/text()').extract()))
        title = title.replace(u'Amazon.com: Customer Reviews: ', '')
        rlist = hxs.xpath("//div[@id='cm_cr-review_list']/div[@class='a-section review']")
        for div in rlist:
            r = Review()
            r['product_id'] = asin
            r['product_name'] = title
            r['review_id'] = first_item(div.xpath('@id').extract())
            votes = FmtSQLCharater(first_item(div.xpath('div[1]/span/text()').extract()))
            match = re.search(u'(.+) people found this helpful', votes, re.I)
            if match:
                r['total_feedback_num'] = match.group(1)
                r['total_helpful_num'] = match.group(2)
            #
            r['full_star'] = FmtSQLCharater(first_item(div.xpath("div[2]/a[1]/i/span/text()").extract()))
            r['title'] = FmtSQLCharater(first_item(div.xpath("div[2]/a[2]/text()").extract()))
            r['cust_name'] = FmtSQLCharater(first_item(div.xpath("div[3]/span[1]/a/text()").extract()))
            r['creation_date'] = FmtSQLCharater(first_item(div.xpath("div[3]/span[4]/text()").extract()))
            #r['creation_date'] = r['creation_date'].replace(u'于 ', '').replace('年', '/').replace(u'月', '/').replace(u'日', '/')
            r['body'] = first_item(div.xpath("div[5]/span").extract())
            yield r
        #下一页
        if len(rlist) == 10:
            page = response.meta['page'] + 1
            log.msg('Request Product[%s]-[%d] page review ...' % (asin, page))
            yield Request(
                url=self.review_url.replace('<?asin?>', asin).replace('<?page?>', str(page)),
                callback=self.parse_review,
                headers=self.headers,
                meta={'page': page, 'asin': asin}
            )
