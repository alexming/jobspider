# -*- coding: utf-8 -*-


from scrapy import Field
from jobspider.scrapy_dao.item_dao_mysql import ItemDaoMysql


class Product(ItemDaoMysql):

	sitename = Field()
	brand = Field()
	product_id = Field()
	original_price = Field()
	sale_price = Field()
	discount = Field()
	is_vip_discount = Field()
	product_points = Field()
	product_points_gold = Field()
	product_points_diamond = Field()
	vip_price_1 = Field()
	vip_price_2 = Field()
	vip_price_3 = Field()
	product_name = Field()
	display_status = Field()
	is_direct_buy = Field()
	main_product_id = Field()
	product_medium = Field()
	product_type = Field()
	category_id = Field()
	is_catalog_product = Field()
	has_ebook = Field()
	subname = Field()
	support_seven_days = Field()
	activity_type = Field()
	tax_rate = Field()
	is_overseas = Field()
	#
	publish_publisher = Field()
	publish_author_name = Field()
	publish_product_size = Field()
	publish_print_copy = Field()
	publish_paper_quality = Field()
	publish_publish_date = Field()
	publish_number_of_pages = Field()
	publish_number_of_words = Field()
	publish_version_num = Field()
	publish_singer = Field()
	publish_director = Field()
	publish_actors = Field()
	publish_prod_length = Field()
	publish_effective_period = Field()
	publish_subtitle_language = Field()
	publish_binding = Field()
	publish_manufacture_format = Field()
	publish_standard_id = Field()
	#
	stock_status = Field()
	pre_sale = Field()
	#
	#category_id = Field()
	#category_path = Field()
	#path_name = Field()
	#has_sub_path = Field()
	#refund_expire_days = Field()
	#confirm_refund_expire_days = Field()
	#exchange_expire_days = Field()
	#confirm_exchange_expire_days = Field()
	#category_orderno = Field()
	#fullpath = Field()
	#guan_id = Field()
	#catid_path = Field()
	#
	comm_total_review_count = Field()
	comm_total_like_count = Field()
	comm_total_dislike_count = Field()
	comm_average_score = Field()
	comm_total_buyer_review_count = Field()
	#
	collection_num = Field()
	is_ebook = Field()
	abstract = Field()
	images = Field()
	images_big = Field()
	#
	stars_full_star = Field()
	stars_has_half_star = Field()
	#
	is_pub_product = Field()
	ebook_read_ebook_at_h5 = Field()
	ebook_is_client_buy = Field()
	#
	spuinfo_num = Field()
	spuinfo_spus_id = Field()
	#
	item_mobile_exclusive_price = Field()
	show_price_name = Field()
	is_support_mobile_buying = Field()
	#
	bang_rank_word = Field()
	bang_rank_path_name = Field()
	bang_rank_rank = Field()
	bang_rank_catPath = Field()
	#
	product_description = Field()
	#product_abstract = Field()
	authorintro = Field()
	catalog = Field()
	content = Field()
	extract = Field()
	mediafeeback = Field()
	preface = Field()
	beautiful_image = Field()
	beautiful_image_list = Field()
	#
	recommendation = Field()
	brief_introduction = Field()
	#catalog = Field()
	more_information = Field()

	DBKey = 'GSX'
	StoreTable = 'dangdang_book_v2'

	def __init__(self):
		super(Product, self).__init__()
		self['sitename'] = 'dd'

class Category(ItemDaoMysql):

	sitename = Field()
	product_id = Field()
	category_path = Field()
	path_name = Field()

	DBKey = 'GSX'
	StoreTable = 'dangdang_book_category'

	def __init__(self):
		super(Category, self).__init__()
		self['sitename'] = 'dd'

class Review(ItemDaoMysql):

	sitename = Field()
	product_id = Field()
	product_name = Field()
	review_id = Field()
	creation_date = Field()
	score = Field()
	full_star = Field()
	has_half_star = Field()
	cust_id = Field()
	cust_name = Field()
	cust_lev = Field()
	cust_level_simple = Field()
	cust_img = Field()
	total_feedback_num = Field()
	total_helpful_num = Field()
	total_points = Field()
	title = Field()
	body = Field()

	DBKey = 'GSX'
	StoreTable = 'dangdang_comment'

	def __init__(self):
		super(Review, self).__init__()
		self['sitename'] = 'dd'
