from catscore.http.request import CatsRequest
from catscore.lib.time import get_today_date
from catscore.lib.logger import CatsLogging as logging
from catsslave.model.nhk import NHKProgramTable, NHKProgram
import sys
from typing import List
from catscore.lib.pandas import PandasConverter
from dataclasses import dataclass
from catsnews.gunosy.article import GunosyArticleSite, GunosyArticle
from typing import List
from catscore.lib.time import get_today_date
from dataclasses_json import dataclass_json
from itertools import chain

@dataclass
@dataclass_json
class GunosyRanknedArticle:
    thumb_url: str
    detail_url: str
    runk_num: str
    article: GunosyArticle

@dataclass
@dataclass_json
class GunosyRanking:
    ranking_title: str
    articles: List[GunosyArticle]
    update_date: str = get_today_date()

@dataclass
@dataclass_json
class AllGunosyRanking:
    gunosy_rankings: List[GunosyRanking]
    update_date: str = get_today_date()

class GunosyRankingSite:
    base_url = "https://gunosy.com/ranking"
    base_file_name = "gunosy_ranking"
    
    def __init__(self, request: CatsRequest):
        self.request:CatsRequest = request
    
    def ranking_links(self):
        def _ranking_links(url):
            contnt = self.request.get(url=url, response_content_type="html").content
            return list(set(map(lambda a: a.get("href"), contnt.findAll("a", {"class", "parent_link"}) + contnt.findAll("a", {"class", "sub_link"}))))
        
        top_url = f"{self.base_url}/daily"
        top_ranking_links = _ranking_links(top_url)
        parent_links = list(filter(lambda x: "categories" in x, top_ranking_links))
        all_links = list(chain.from_iterable(list(map(lambda x: _ranking_links(x), parent_links))))
        return list(set(top_ranking_links + all_links))
        
    def pull_ranking(self, url) -> GunosyRanking:
        page = self.request.get(url=url, response_content_type="html").content
        ranking_title = page.find("h1", {"class", "list_header_title"}).text
        logging.info(f"pull_ranking: {ranking_title}")
        def _parge_page(list_content):
            try:
                list_thumb = list_content.find("div", {"class", "list_thumb"})
                detail_url = list_thumb.find("a").get("href")
                thumb_url = "https://" + list_thumb.find("img").get("style").split("(//")[1].replace(")","")
                article = GunosyArticleSite(request=self.request, url=detail_url).pull()
                runk_num = list_content.find("span", {"class", "list_rank_no"}).text
                return GunosyRanknedArticle(
                    thumb_url=thumb_url,
                    detail_url=detail_url,
                    runk_num=runk_num,
                    article=article)
            except:
                print(f"{list_content} page cannot parse")
                return None
        list_contents = page.findAll("div", {"class", "list_content"})
        articles = list(filter(lambda x: x != None, list(map(lambda x: _parge_page(x), list_contents))))
        return GunosyRanking(ranking_title=ranking_title, articles=articles)
    
    def pull_all_ranking(self) -> AllGunosyRanking:
        gunosy_rankings = list(map(lambda l: self.pull_ranking(l), self.ranking_links()))
        return AllGunosyRanking(gunosy_rankings=gunosy_rankings)
        
    def save_all_ranking_as_json(self, output_path: str):
        dj = self.pull_all_ranking()
        json = dj.to_json(indent=4, ensure_ascii=False)
        full_output_path = f"{output_path}/{self.base_file_name}_{get_today_date()}.json"
        with open(full_output_path, "w") as f:
            f.write(json)