chroniclingamerica.py
=====================

## Python API to search Chronicling America newspaper pages.

### Usage

```python
from chroniclingamerica import ChronAm
from pprint import pprint

fetcher = ChronAm(search_term)
for item in fetcher.fetch():
    pprint(item)  # Or do something more interesting
```

Calling `fetch()` returns a generator of articles in JSON format. Articles are retrieved one [results] page at a time. 
To get the total number of pages available, use `get_total_pages()`.

Or just run it from the terminal and then manipulate the output files direclty.

### Parameters

Currently there's only one parameter.

* `search_term`
  * The search query
* `-y or --year`
  * The Max year you want to search for articles from
* `-w or --write`
  * Declare if you want the results written to a file and, if so, what file name to write to
* `--csv`
  * Get the output file in CSV as opposed to JSON. Note, JSON stores data in memory before writing, while CSV writes straight to file. If you are performing operations on a large dataset, use the CSV flag or risk bogging down your machine.
* `--count`
  * The maximum number of article results you would like returned

### Examples

* Get up to 1000 news articles containing the term "housewife" that appeared in newspapers from year 1836 - 1900 and write to CSV.
  * `python chroniclingamerica.py housewife -y 1900 -w outputFile --csv --count 1000`

### To Do

* More search parameters.
* Allow for multiprocessing - helpful if request handling the bottleneck, not the network speed 

### Origin

The base fetcher was forked from [@hugovk's](https://github.com/hugovk) [Chronicling America API Wrapper](https://github.com/hugovk/chroniclingamerica.py)

#### @hugovk's Original Attribution Section:

Thanks to [@zeroviscosity](https://github.com/zeroviscosity/) for the
[Article fetcher for The Guardian newspaper's Open Platform API](https://github.com/zeroviscosity/guardian-article-fetcher),
which this project is based on, and to 
[The Library of Congress](http://www.loc.gov/) for [Chronicling America](http://chroniclingamerica.loc.gov/) and their 
[API](http://chroniclingamerica.loc.gov/about/api/).
