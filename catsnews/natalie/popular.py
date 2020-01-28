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
from catsnews.natalie.article import NatalieArticleSite, NatalieArticle
from catscore.lib.functional import filter_none

@dataclass
@dataclass_json
class NataliePopularPage:
    populer_url: str
    popular_category: str
    natalie_articles: List[NatalieArticle]
    update_date: str = get_today_date()
    
@dataclass
@dataclass_json
class NataliePopular:
    natalie_populare_pages: List[NataliePopularPage]
    update_date: str = get_today_date()
    
@dataclass
@dataclass_json
class AllNataliePopular:
    natalie_populares: List[NataliePopular]
    update_date: str = get_today_date()

class NataliePopularSite:
    base_file_name = "natalie_popular"
    
    def __init__(self, request: CatsRequest):
        self.request:CatsRequest = request
        
    def pull_page(self, url) -> NataliePopularPage:
        try:
            content = self.request.get(url=url, response_content_type="html").content
            popular_category = ",".join(list(map(lambda x: x.text, content.find("ul", {"class": "NA_breadcrumb"}).findAll("li"))))
            article_lists = content.find("ul", {"class": "NA_articleList"}).findAll("li")
            def _parse_article(article):
                try:
                    title = article.find("dt", {"class": "NA_title"}).text.replace("\n","").replace(",","").replace("\"","")
                    detail_link = article.find("a").get("href")
                    article = NatalieArticleSite(request=self.request, url=detail_link).pull()
                    return article
                except Exception:
                    logging.error(f"_parse_article error occured : {sys.exc_info()}")
                    return None
            natalie_articles = filter_none(list(map(lambda a: _parse_article(a), article_lists)))
            return NataliePopularPage(populer_url=url, popular_category=popular_category, natalie_articles=natalie_articles)
        except Exception:
            return None

    def pull_all_page(self, url, range_num=10) -> NataliePopular:
        top = f"{url}/news/list/order_by/views"
        def _page_link(id):
            return f"{url}/news/list/page/{id}/order_by/views"
        page_links = list(map(lambda id: _page_link(id=id), list(range(1, range_num))))
        natalie_populare_pages = filter_none(list(map(lambda url: self.pull_page(url=url), page_links)))
        return NataliePopular(natalie_populare_pages=natalie_populare_pages)
        
    def pull_all_category(self) -> AllNataliePopular:
        categories = ["music", "comic", "owarai", "eiga", "stage"]
        def _popular_url(category):
            return f"https://natalie.mu/{category}"
        category_links = list(map(lambda x: _popular_url(x), categories))
        natalie_populares = list(map(lambda x: self.pull_all_page(x), category_links))
        return AllNataliePopular(natalie_populares = natalie_populares)
    
    def save_all_category_as_json(self, output_path: str):
        dj = self.pull_all_category()
        json = dj.to_json(indent=4, ensure_ascii=False)
        full_output_path = f"{output_path}/{self.base_file_name}_{get_today_date()}.json"
        logging.info(f"save_all_category_as_json: output to {full_output_path}")
        with open(full_output_path, "w") as f:
            f.write(json)
        