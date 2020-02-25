# -*- coding: utf-8 -*-
import scrapy


class CodesSpider(scrapy.Spider):
    BASE_URL = 'https://en.wikipedia.org/'
    name = 'codes'
    start_urls = [
        '{}/wiki/List_of_ISO_3166_country_codes'.format(BASE_URL)
    ]

    def parse(self, response):
        # Get all table rows
        rows = response.xpath('//*[contains(@class,"wikitable sortable")]//tr')

        for row in rows[2:]:
            try:
                country_name = row.xpath('td/a//text()').extract_first()
                alpha_3 = row\
                    .css('a[title="ISO 3166-1 alpha-3"]')\
                    .xpath('span//text()')\
                    .extract_first()
                alpha_2 = row\
                    .css('a[title="ISO 3166-1 alpha-2"]')\
                    .xpath('span//text()')\
                    .extract_first()
                subdivision_link = '{}wiki/ISO_3166-2:{}'.format(
                    self.BASE_URL,
                    alpha_2
                )

                # Propagate data with subdivision regions and their codes
                request = scrapy.Request(
                    subdivision_link,
                    callback=self.get_subdivisions,
                    meta={
                        'country_name': country_name,
                        'alpha_2': alpha_2,
                        'alpha_3': alpha_3,
                    }
                )
                yield request
            except IndexError:
                pass

    def get_subdivisions(self, response):
        divisions = {}
        item = {}
        try:
            #  rows = response.xpath('//*[contains(@class,"wikitable sortable")]//tr')
            table = response.xpath('//*[contains(@class,"wikitable sortable")]')[0]
            rows = table.xpath('*//tr')

            # Start looping through all rows, but add only with both code
            # and name extracted
            for row in rows:
                # Extract code
                code = row.xpath('td/span/text()')
                if not code:
                    code = row.xpath('td/span/span/text()')
                code = code.extract_first()

                # Extract name
                name = row.xpath('td/a//text()')
                if not name:
                    name = row.xpath('td/span/a//text()')
                name = name.extract_first()

                if code and name:
                    divisions.update({
                        name: code
                    })
            item.update({
                'Subdivisions': divisions,
                'Subdivisions URL': response.url,
            })
        except IndexError:
            print('Did not find any tables for subdivisions for {}'.format(
                    response.meta.get('country_name')
                )
            )

        item.update({
            'Country name': response.meta.get('country_name'),
            'ISO 3166-2': response.meta.get('alpha_2'),
            'ISO 3166-3': response.meta.get('alpha_3'),
        })
        yield item

