#!/usr/bin/env python
# encoding: utf-8
"""
API to search Chronicling America

From http://chroniclingamerica.loc.gov/about/api/

    Introduction

    Chronicling America provides access to information about historic
    newspapers and select digitized newspaper pages. To encourage a wide range
    of potential uses, we designed several different views of the data we
    provide, all of which are publicly visible. Each uses common Web protocols,
    and access is not restricted in any way. You do not need to apply for a
    special key to use them. Together they make up an extensive application
    programming interface (API) which you can use to explore all of our data in
    many ways.

    Details about these interfaces are below. In case you want to dive right
    in, though, we use HTML link conventions to advertise the availability of
    these views. If you are a software developer or researcher or anyone else
    who might be interested in programmatic access to the data in Chronicling
    America, we encourage you to look around the site, "view source" often,
    and follow where the different links take you to get started. When
    describing Chronicling America as the source of content, please use the URL
    and a Web site citation, such as "from the Library of Congress, Chronicling
    America: Historic American Newspapers site".

    For more information about the open source Chronicling America software
    please see the LibraryOfCongress/chronam GitHub site. Also, please consider
    subscribing to the ChronAm-Users discussion list if you want to discuss how
    to use or extend the software or data from its APIs.

    The API

    Searching the directory and newspaper pages using OpenSearch

    ...

    Searching newspaper pages is also possible via OpenSearch. This is
    advertised in a LINK header element of the site's HTML template as "NDNP
    Page Search", using this OpenSearch Description document.

    Page search parameters:

     * andtext: the search query
     * format: 'html' (default), or 'json', or 'atom' (optional)
     * page: for paging results (optional)

    Examples:

     * /search/pages/results/?andtext=thomas
       search for "thomas", HTML response
     * /search/pages/results/?andtext=thomas&format=atom
       search for "thomas", Atom response
     * /search/pages/results/?andtext=thomas&format=atom&page=11
       search for "thomas", Atom response, starting at page 11
"""
from __future__ import print_function, unicode_literals
import argparse
import json
import csv
import requests

URL_FORMAT = "http://chroniclingamerica.loc.gov/search/pages/results/?%s"


# cmd.exe cannot do Unicode so encode first
def print_it(text):
    print(text.encode('utf-8'))


class ChronAm():
    def __init__(self, search_text, page=1, max_pages=0):
        """Defines the fetcher URL"""
        self.page = page
        self.max_pages = max_pages

        params = []
        params.append("format=json")
        params.append('phrasetext=%s' % search_text)

        self.url = URL_FORMAT % '&'.join(params)
        self.url += '&page=%d'

    def get_total_pages(self):
        """Retrieves the total number of pages for the current operation"""
        r = requests.get(self.url % 1)
        resp = (json.loads(r.text))
        # Floats for rounding up in Py2
        total_items = float(resp['totalItems'])
        items_per_page = float(resp['itemsPerPage'])
        import math
        # Round up
        total_pages = int(math.ceil(total_items / items_per_page))
        if self.max_pages == 0:
            return total_pages
        else:
            return min(self.max_pages, total_pages)

    def get_data(self, page_number):
        """Fetches a page of items from the API"""

        if(args.write is None) :
            percent = 100.0 * page_number / self.total_pages
            print('Fetching page %i of %i ... %f%%' % (
                page_number, self.total_pages, percent))
        else:
            if(page_number % 100 == 0):
                print("Fetched to page: %i of %i" % 
                    ( page_number, self.total_pages) )

        r = requests.get(self.url % page_number)
        try: 
            resp = (json.loads(r.text))
        except ValueError as e:
            print("ERROR: ValueError - " + str(e))
            return []
        if len(resp['items']) > 0:
            return resp['items']
        return []

    def fetch(self):
        """Starts the fetching process"""
        self.total_pages = self.get_total_pages()
        for i in range(self.page, self.total_pages + 1):
            for item in self.get_data(i):
                yield item


if __name__ == "__main__":

    #Log initial start time of API hit
    import timeit
    timeStart = timeit.default_timer()
    print("Operation started at: " + repr(timeStart))

    parser = argparse.ArgumentParser(
        description="API to search Chronicling America",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('searchterm', help='Phrase to search for')
    parser.add_argument('-y', '--year', type=int, help='Max year')
    parser.add_argument('-w', '--write', type=str, help="Write to file name")
    parser.add_argument('--csv', const=csv, nargs='?', help="File write to CSV")
    parser.add_argument('--count', type=int, help="Max number of returned files")
    args = parser.parse_args()

    if(args.write):
        if(args.csv):
            print("Writing to file: " + args.write + ".csv")
        else:
            print("Writing to file: " + args.write + ".json")

    import os
    from pprint import pprint

    args.searchterm = unicode(args.searchterm)

    fetcher = ChronAm(args.searchterm)

    APIFetchData =[]
    resultsInTimerange = 0;

    if(args.write and args.csv):
            file = open(args.write + '.csv', 'wb')
            csvWriter = csv.writer(file)

    for item in fetcher.fetch():
        try:
            year = item['date'][:4]

            if args.year and int(year) > args.year:
                continue

            # pprint(item.keys())
            # pprint(item)  # Or do something more interesting

            month = item['date'][4:6]
            day = item['date'][6:]
            date = year + "-" + month + "-" + day
            text = item['ocr_eng']
            text = text.replace('\\n', os.linesep)

            # If args.write not present, print to commandline
            if(args.write is None):
                print("=" * 80)
                print(item['date'])
                print(date, item['title'], item['place_of_publication'])
                print("-" * 80)
                print_it(text)
                print("-" * 80)

                print('http://chroniclingamerica.loc.gov' + item['id'] +
                      "#words=" + args.searchterm)

            else:
                if(args.csv):
                    #Have to convert from unicode to play nice with csv
                    #entry = "%s, %s, %s, %s" % ( year,
                     #month, day,
                     #text.replace(',', '') )
                    entry = [year.encode('utf-8'), month.encode('utf-8'), 
                    day.encode('utf-8'), text.replace(',', '').encode('utf-8')];
                    csvWriter.writerow(entry);
                else:
                    entry = {'year': year, 'month': month, 'day': day, 'date': date, 
                            'text': text}
                    APIFetchData.append(entry)
        except ValueError as e:
            print("ERROR: ValueError - " + str(e))
            continue
        except KeyboardInterrupt as e:
            print("INTERRUPT: User stopped operation")
            break
        except Exception as e:
            print("EXCEPTION: Threw exception - " + str(e))
            continue

        resultsInTimerange+=1
        if(args.count and resultsInTimerange > args.count):
            break

    #Write data to file if in --write mode
    if(args.write and args.csv is None):
        if(args.csv):
            #file = open(args.write + '.csv', 'wb')
            #writer = csv.writer(file)
            #for entry in APIFetchData:
            #    entry=[s.encode('utf-8') for s in entry]
            #    writer.writerow(entry)
            file.close()
        else:
            with open(args.write + ".json", 'w') as file:
                json.dump(APIFetchData, file)

    #Print retrieval stats
    print(str(resultsInTimerange) + " relevant results found in time range");

    #Display time for operation to complete
    timeEnd = timeit.default_timer()
    print("Operation ended at: " + repr(timeEnd))
    print("Elapsed time: " + repr(timeEnd - timeStart) + "s")


# End of file
