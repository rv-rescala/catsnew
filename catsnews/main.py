import argparse
import logging
from catscore.http.request import CatsRequest
from catscore.lib.time import get_today_date
import json
from catscore.lib.logger import CatsLogging as logging
from catsnews.gunosy.ranking import GunosyRankingSite

def main():
    parser = argparse.ArgumentParser(description="cats slave")

    # args params
    parser.add_argument('-conf', '--conf', help="configuration file", required=True)
    parser.add_argument('-gunocy', '--gunocy', nargs='*', choices=['ranking'], help="gunocy functions")
    args = parser.parse_args()
    print(args)
    
    # init
    with open(args.conf) as f:
        conf = json.load(f)
        print(conf)
        try:
            logging.init(app_name=conf["logging"]["app_name"], ouput_dir=conf["logging"]["log_dir"], log_level=conf["logging"]["log_level"])
        except Exception:
            print("logging conf not found.")
    request = CatsRequest()

    if args.gunocy:
        for args in args.gunocy:
            r = GunosyRankingSite(request).save_all_ranking_as_json(conf["output"]["dir"])
            print(r)

if __name__ == "__main__":
    main()
