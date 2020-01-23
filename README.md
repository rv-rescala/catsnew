# kakaku_robot

Kakaku lobot is a scraping library for https://kakaku.com/

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install kakaku_robot
```

## Usage

```python
from kakaku_robot.site.ranking import Ranking
result = Ranking().ranking.all_category_ranking(pandas=True)
result.to_csv("kakau_rank.csv")
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)