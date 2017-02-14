# -*- coding: utf-8 -*-


from scrapy import Field, Item


#多学网存储结构定义
class DuoXSchool(Item):
    id = Field()
    fullName = Field()
    companyName = Field()
    mainCourse = Field()
    province = Field()
    city = Field()
    zone = Field()
    lat = Field()
    lng = Field()
    address = Field()
    business = Field()
    contact = Field()
    phone = Field()
    discription = Field()
    #品牌
    brandAward = Field()
    brandHistory = Field()
    brandSchoolCount = Field()
    brandStudentCount = Field()
    #环境
    envArea = Field()
    envFacilities = Field()
    envFitment = Field()
    envHealth = Field()
    envPantry = Field()
    envParentRest = Field()
    envType = Field()
    #服务特色
    serviceDetail = Field()
    #师资
    teacherAge = Field()
    teacherCount = Field()
    teacherQualifier = Field()
    #学校图片
    schoolImage = Field()
    #展示图片
    imageTurn = Field()

class DuoXTeacher(Item):
    s_id = Field()
    id = Field()
    teacherName = Field()
    image = Field()

class DuoXCourse(Item):
    s_id = Field()
    id = Field()
    province = Field()
    city = Field()
    zone = Field()
    schoolFullName = Field()
    courseName = Field()
    lat = Field()
    lng = Field()
    typeName1 = Field()
    typeName2 = Field()
    ageStart = Field()
    ageEnd = Field()
    perPrice = Field()
    packagePrice = Field()
    needBook = Field()
    studentCount = Field()
    courseImage = Field()
    discount = Field()
    #
    address = Field()
    business = Field()
    courseDes = Field()
    #
    imageTurn = Field()
    priceList = Field()

class DuoXComment(Item):
    s_id = Field()
    s_name = Field()
    id = Field()
    commentText = Field()
    #1.学校评论 3.课程评论
    commentType = Field()
    contactName = Field()
    contactPhone= Field()
    createTime = Field()
    typeId = Field()
    typeName = Field()
