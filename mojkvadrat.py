# -- coding: utf-8 --
import urllib3
from bs4 import BeautifulSoup
import datetime
import pyodbc
from common import upsert_stan, DB_SERVER, DB_NAME, DB_USERNAME, DB_PASSWORD

def process_stan(cnx, http, stan_id):
    print('Processing id %d' % stan_id)
    stan_data = get_stan_data(http, stan_id)
    if stan_data is None: raise Exception('Unknown error occured processing %s' % stan_id)
    upsert_stan(cnx, stan_data)
    cnx.commit()

def get_stan_data(http, stan_id):
    url = 'http://www.mojkvadrat.rs/nekretnine/prodaja/stan/beograd/%d' % stan_id
    page = http.request('GET', url)
    soup = BeautifulSoup(page.data)
    title_elem = soup.select('div.realEstate-details > h1')
    if len(title_elem) == 0: return None
    title = title_elem[0].text
    published_date, modified_date = soup.select('div.realEstate-details > span.estate-date')[0].text.split('/')
    published_date = datetime.datetime.strptime(published_date.strip()[11:], '%d.%m.%Y.')
    modified_date =  datetime.datetime.strptime(modified_date.replace('\r', '').replace('\n', '').replace(' ', '')[12:], '%d.%m.%Y.')
    
    area = price = floor = total_floors = street = part = rooms = construction_year = heating_type_id = None
    for elem in soup.select('div.realEstate-details > div > p'):
        if elem.text.startswith('Tip:'): stan_type = elem.select('span')[0].text
        elif elem.text.startswith('Cena:'): price = float(elem.select('span')[0].text[:-4])
        elif elem.text.startswith('Površina:'): area = float(elem.select('span')[0].text[:-3])
        elif elem.text.startswith('Grad:'): city = elem.select('span')[0].text
        elif elem.text.startswith('Opština:'): municipality = elem.select('span')[0].text
        elif elem.text.startswith('Deo:'): part = elem.select('span')[0].text
        elif elem.text.startswith('Ulica:'): street = elem.select('span')[0].text
        elif elem.text.startswith('Sprat:'): floor = float(elem.select('span')[0].text)
        elif elem.text.startswith('Spratnost:'): total_floors = int(elem.select('span')[0].text)
        elif elem.text.startswith('Soba:'): rooms = float(elem.select('span')[0].text)
        elif elem.text.startswith('Godina izgradnje:'): construction_year = int(elem.select('span')[0].text)

    legalized = elevator = sewer = intercom = phone = balcon = basement = cable_tv =\
    aircondition = internet = parking = useljivo = new_building = under_construction = 0
    for elem in soup.select('div.detail-description-list > ul > li'):
        if elem.text == 'Uknjiženo': legalized = 1
        elif elem.text == 'Kablovska': cable_tv = 1
        elif elem.text == 'Klima': aircondition = 1
        elif elem.text == 'Interfon': intercom = 1
        elif elem.text == 'Useljivo': useljivo = 1
        elif elem.text == 'Internet': internet = 1
        elif elem.text == 'Parking': parking = 1
        elif elem.text == 'Podrum': basement = 1
        elif elem.text == 'Telefon': phone = 1
        elif elem.text == 'Lift': elevator = 1
        elif elem.text == 'Daljinsko grejanje': heating_type_id = 9
        elif elem.text == 'Centralno grejanje': heating_type_id = 1
        elif elem.text == 'Kanalizacija': sewer = 1
        elif elem.text == 'Novogradnja': new_building = 1
        elif elem.text == 'Terasa': balcon = 1
        elif elem.text == 'U izgradnji': under_construction = 1
        else: raise Exception('Unknown property %s' % elem.text)
    stan_data = {'id': stan_id, 'id_source': 1, 'title': title, 'url': url, 'published_date': published_date, 'modified_date': modified_date, 'type': stan_type, 'price': price,
                 'area': area, 'city': city, 'municipality': municipality, 'part': part, 'street': street, 'floor': floor, 'total_floors': total_floors, 'rooms': rooms,
                 'construction_year': construction_year, 'legalized': legalized, 'elevator': elevator, 'sewer': sewer, 'intercom': intercom, 'phone': phone,
                 'heating_type_id': heating_type_id, 'balcon': balcon, 'basement': basement, 'cable_tv': cable_tv, 'aircondition': aircondition, 'internet': internet,
                 'parking': parking, 'useljivo': useljivo, 'new_building': new_building, 'under_construction': under_construction, 'description': ''}
    return stan_data

def parse_page(soup):
    for agency_elem in soup.select('div#container-middle > div.agency'):
        href = agency_elem.find('a')['href']
        if not href.startswith('/nekretnine/prodaja/stan/beograd/'): raise Exception
        yield int(href[33:])
    
def get_stan_ids(http):
    current_page = 1
    while(True):
        print('Current page %d' % current_page)
        page = http.request('GET', 'http://www.mojkvadrat.rs/nekretnine/pretraga/YT0xJnQ9MSZsYz0y/%d' % current_page)
        soup = BeautifulSoup(page.data)
        for stan_id in parse_page(soup): yield stan_id
        if len(soup.select('div.fw-PaginatorNext')) == 0: break
        current_page += 1

if __name__=='__main__':
    http = urllib3.PoolManager()
    cnx = pyodbc.connect('DRIVER={SQL Server};SERVER=%s;DATABASE=%s;UID=%s;PWD=%s' % (DB_SERVER, DB_NAME, DB_USERNAME, DB_PASSWORD))
    for stan_id in get_stan_ids(http):
        process_stan(cnx, http, stan_id)
    cnx.close()