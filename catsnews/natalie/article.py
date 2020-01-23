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
class NatalieArticle:
    url: str
    category: str
    title: str
    update_datetime: str
    star: str
    thumbnail: str
    content: str

class NatalieArticleSite:
    def __init__(self, request:CatsRequest, url:str):
        self.url = url
        self.content = request.get(url=url, response_content_type="html").content
        
    def pull(self) -> NatalieArticle:
        category = ",".join(list(map(lambda x: x.text, self.content.find("ul",{"class", "NA_breadcrumb"}).findAll("li")))[:-1])
        title = self.content.find("div", {"class": "NA_articleHeader"}).find("h1").text
        update_datetime =  self.content.find("p", {"class": "NA_date"}).find("time").text
        star = "0"
        try:
            star = self.content.find("p", {"class": "NA_res2"}).find("a").text
        except Exception:
            logging.info(f"{self.url} star not found")
        thumbnail = "https://s3-ap-northeast-1.amazonaws.com/lifull-homes-press/uploads/press/2019/09/14-300x225.jpg"
        try:
            thumbnail = self.content.find("p", {"class": "NA_figure"}).find("img").get("src")
        except Exception:
            logging.info(f"{self.url} thumbnail not found")
        content = self.content.find("div", {"class": "NA_articleBody"}).text.replace(",","").replace("\n","").replace("\"","")
        return NatalieArticle(
            url=self.url,
            category=category,
            title=title,
            update_datetime=update_datetime,
            star=star,
            thumbnail=thumbnail,
            content=content
        )
        