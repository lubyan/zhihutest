# -*- coding: utf-8 -*-
import  json
from scrapy import Spider, Request
from zhihutest.items import ZhihutestItem

class ZhihuSpider(Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    follows_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    followers_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}'
    start_user = 'excited-vczh'
    user_query = 'locations,employments,gender,educations,business,voteup_count,thanked_Count,follower_count,following_count,cover_url,following_topic_count,following_question_count,following_favlists_count,following_columns_count,answer_count,articles_count,pins_count,question_count,commercial_question_count,favorite_count,favorited_count,logs_count,marked_answers_count,marked_answers_text,message_thread_token,account_status,is_active,is_force_renamed,is_bind_sina,sina_weibo_url,sina_weibo_name,show_sina_weibo,is_blocking,is_blocked,is_following,is_followed,mutual_followees_count,vote_to_count,vote_from_count,thank_to_count,thank_from_count,thanked_count,description,hosted_live_count,participated_live_count,allow_message,industry_category,org_name,org_homepage,badge[?(type=best_answerer)].topics'
    follows_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
    followers_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    # 通过起始的 爬虫元制定 起始用户的主页网址  起始用户的粉丝列表网址  起始用户的关注者网址
    def start_requests(self):
        yield Request(self.user_url.format(user=self.start_user, include=self.user_query), self.parse_user)  #构造并提交起始用户的主页网址
        yield Request(self.follows_url.format(user=self.start_user,include=self.follows_query,offset=0,limit=20),self.parse_following)  #构造并提交起始用户的关注者网址
        yield Request(self.followers_url.format(user=self.start_user,include=self.followers_query,offset=0,linit=20),self.parse_followers) #构造并提交起始用户的粉丝网址
    # 处理用户详情页的函数
    def parse_user(self, response):
        result = json.loads(response.text)
        item = ZhihutestItem() #把自己定制的key和网页上的数据结构的key一一对应起来
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield item  #获取并返还 每个用户的具体参数

        #把现在在处理的用户的关注列表网址生成并提交给处理关注列表的函数
        yield Request(self.follows_url.format(user=result.get('url_token'),include=self.follows_query,offset=0,limit=20),self.parse_following)
        # 把现在在处理的用户的粉丝列表网址生成并提交给处理粉丝列表的函数
        yield Request(
            self.followers_url.format(user=result.get('url_token'), include=self.follows_query, offset=0, limit=20),
            self.parse_followers)

    # 处理用户关注者网址的函数
    def parse_following(self,response):
        result = json.loads(response.text)
        #提取关注者的token
        if 'data' in result.keys():   #判断具体数据是否包含在key中
            for data in result.get('data'):  #制作数据的循环获取
                url_token = data.get('url_token')   #获取到用户的唯一值（关键字）
                yield Request(self.user_url.format(user=url_token,include=self.user_query),self.parse_user) #把获取到的关键字，通过用户首页网址构造每个用户自己的网址，并提交给处理用户主页的函数处理

        #处理翻页
        if 'paging' in result.keys() and result.get('paging').get('is_end') == False: #判断下一页的key是否存在，以及判断是否是最后一页
            next_page = result.get('paging').get('next')   #获取关注列表的下一页网址
            yield Request(next_page,self.parse_following)  #把获取到的关注下一页 提交给处理关注列表的函数，也就是这个函数本身。进行递归

    # 处理用户粉丝网址的函数
    def parse_followers(self,response):
        result = json.loads(response.text)
        # 提取粉丝的token
        if 'data' in result.keys():  # 判断具体数据是否包含在key中
            for data in result.get('data'):  # 制作数据的循环获取
                url_token = data.get('url_token')  # 获取到用户的唯一值（关键字）
                yield Request(self.user_url.format(user=url_token, include=self.user_query),
                              self.parse_user)  # 把获取到的关键字，通过用户首页网址构造每个用户自己的网址，并提交给处理用户主页的函数处理

        # 处理翻页
        if 'paging' in result.keys() and result.get('paging').get('is_end') == False:  # 判断下一页的key是否存在，以及判断是否是最后一页
            next_page = result.get('paging').get('next')  # 获取粉丝列表下一页网址
            yield Request(next_page, self.parse_followers)  # 把获取到的粉丝下一页 提交给处理关注列表的函数，也就是这个函数本身。进行递归