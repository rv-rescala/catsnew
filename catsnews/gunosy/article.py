from catscore.http.request import CatsRequest
from catscore.lib.time import get_today_date
from catscore.lib.logger import CatsLogging as logging
from catsslave.model.nhk import NHKProgramTable, NHKProgram
import sys
from typing import List
from catscore.lib.pandas import PandasConverter
from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass
@dataclass_json
class GunosyArticle:
    category: str
    title: str
    lead_by: str
    update_date: str
    tag: str
    content: str

class GunosyArticleSite:
    def __init__(self, request:CatsRequest, url:str):
        self.content = request.get(url=url, response_content_type="html").content
        
    def pull(self) -> GunosyArticle:
        article_category = ",".join(list(map(lambda x: x.text, self.content.find("div",{"class", "breadcrumb_inner"}).findAll("span")))[:-1])
        article_header_text = self.content.find("div", {"class", "article_header_text"})
        article_header_title = article_header_text.find("h1").text
        article_header_lead_by = article_header_text.find("li", {"class", "article_header_lead_by"}).text
        article_update_date = article_header_text.find("li", {"class", "article_header_lead_date"}).text.split("更新日：")[1]
        article_header_tags = article_header_text.find("ul", {"class", "article_header_tags"})
        article_tags = ""
        if article_header_tags != None:
            article_tags = ",".join(list(map(lambda x: x.text, article_header_tags.findAll("li"))))
        article_content = ",".join(list(map(lambda x: x.text.replace(",","").replace("\n","").replace("\"",""), self.content.find("div", {"class", "article"}).findAll("p"))))
        return GunosyArticle(
            category=article_category,
            title=article_header_title,
            lead_by=article_header_lead_by,
            update_date=article_update_date,
            tag=article_tags,
            content=article_content)
        