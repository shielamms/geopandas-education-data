import pandas as pd
import requests
import string

from bs4 import BeautifulSoup
from urllib.parse import urljoin


class Unversity(object):
    """
    Representation of a University object used by a UniversityScraper
    """

    name = None
    url = None
    address = None
    postcode = None

    def __dict__(self):
        return {
            'name': self.name,
            'url': self.url,
            'address': self.address,
            'postcode': self.postcode,
        }


class UniversityScraper(object):
    """
    Base class for any scraper that extracts university data,
    using the University class to represent extracted data about universities.
    """

    def __init__(self):
        self._start_url = None
        self._params = None
        self.data = []

    def _extract_university_list(self):
        pass

    def _extract_university_info(self, university):
        pass

    def scrape(self):
        for item in self._extract_university_list():
            university = self._extract_university_info()
            self.data.append(university)

    def save(self, output_location='output.csv'):
        pass


class UcasUniversityScraper(UniversityScraper):
    """
    Scraper for the list of UK universities from the UCAS website:
    https://www.ucas.com/explore/unis
    """

    def __init__(self,
                 url='https://www.ucas.com/explore/unis',
                 params={'letter': None}):
        self._start_url = url
        self._params = params

    def _extract_university_list(self):
        all_letters = string.ascii_lowercase
        for letter in all_letters:
            self.params['letter'] = letter
            print(f'Getting all universities from letter {letter}')

            response = requests.get(self.start_url, params=self.params)
            results_soup = BeautifulSoup(response.content)

            unis = results_soup.select('.link-container__link')
            print(f'  Got {len(unis)}')
            yield from unis

    def _extract_university_info(self, university):
        uni_name = university.get('title')
        uni_url = urljoin(self.start_url, university.get('href'))
        response = requests.get(uni_url)
        uni_content_soup = BeautifulSoup(response.content)
        location = (
            uni_content_soup
            .select_one(
                '.content-block__section.content-block__section--grow p')
            .text
        )
        postcode = location.split(',')[-1]

        uni_data = {'name': uni_name,
                    'url': uni_url,
                    'address': location,
                    'postcode': postcode}
        return Unversity(**uni_data)

    def save(self, output_location='output.csv', index=False):
        pd.DataFrame(self.data).to_csv(output_location, index=index)
        print(f'UcasUniversityScraper data saved to {output_location}')


def test_extract_ucas_universities():
    ucas_scraper = UcasUniversityScraper()
    ucas_scraper.scrape()
    ucas_scraper.save('datasets/UK/ucas_universities_2022.csv')
