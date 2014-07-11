# -- coding: utf-8 --
import urllib3
import pyodbc
from bs4 import BeautifulSoup
from common import upsert_stan, DB_SERVER, DB_NAME, DB_USERNAME, DB_PASSWORD
import datetime
from urllib import parse

HEATING_TYPE_DICT = {'CG': 1, 'EG': 2, 'TA': 3, 'mermerni radijatori': 4, 'gas': 5, 'podno': 6, 'norveški radijatori': 7, 'kaljeva peć':8}

def parse_page(soup):
    for result_nek_elem in soup.select('div.result_nek'):
        href = result_nek_elem.select('article > div.frame > div.txt > p.data > a')[0]['href']
        if not href.startswith('/nekretnine/prodaja/stan/'): raise Exception
        yield href[25:]
            
def get_stan_ids(http):
    current_page = 1
    while(True):
        print('Current page ', current_page)
        page = http.request('GET', 'http://www.halooglasi.com/nekretnine/stambeni-prostor/pretraga.57.html?grupa=Stambeni+prostor&valid=true&rubrika=12&location=Beograd&offset=%d&noOnPage=50' % current_page)
        soup = BeautifulSoup(page.data)
        for stan_id in parse_page(soup): yield stan_id
        if len(soup.select('div.pagination > p.next > a')) == 0: break
        current_page += 1

def parse_floors(floor_string):
    """Parses floors and total number of floors. Can be in various forms: '3 od 5', '0.5 od 5', '4', 'pr od 4', 'pr'..."""
    zero_floors = ('psut', 'pr', 'vpr')
    top_floors = ('ptk', 'penthouse')
    floor_total_floors = floor_string.split(' od ')
    if len(floor_total_floors) == 1:
        if floor_total_floors[0].strip() in zero_floors: return (0, None)
        elif floor_total_floors[0].strip() in top_floors: return (None, None)
        elif floor_total_floors[0].strip() == 'sut': return (-1, None)
        else: return (float(floor_total_floors[0]), None)
    else:
        total_floors = int(floor_total_floors[1])
        if floor_total_floors[0].strip() in zero_floors: return (0, total_floors)
        elif floor_total_floors[0].strip() in top_floors: return (total_floors, total_floors)
        elif floor_total_floors[0].strip() == 'sut': return (-1, total_floors)
        elif floor_total_floors[0].strip() == '': return (None, total_floors)
        else: return (float(floor_total_floors[0]), total_floors)

def parse_cmps(text, default_street):
    """Parses city, municipality, part and street. In the form <city> - <municipality> - <part> - <street>. Additional hyphens can appear only in part or street."""
    text = text.split(' - ')
    if len(text) == 4: return text
    elif len(text) == 3: return (text[0], text[1], text[2], default_street)
    elif len(text) == 5:
        city, municipality = text[0], text[1]
        if default_street is not None and ' - ' in default_street:
            return (city, municipality, text[2], text[3] + ' - ' + text[4])
        else:
            return (city, municipality, text[2] + ' - ' + text[3], text[4])
    elif len(text) == 6:
        city, municipality, part = text[0], text[1], text[2]
        if default_street is not None and default_street == text[3] + ' - ' + text[4] + ' - ' + text[5]:
            return (city, municipality, part, text[3] + ' - ' + text[4] + ' - ' + text[5])
        else: raise Exception('Unknown location: %s' % str(text))
    else: raise Exception('Unknown location: %s' % str(text))

def get_stan_data(http, stan_id):
    url = 'http://www.halooglasi.com/nekretnine/prodaja/stan/%s' % stan_id
    # next 3 lines are fixing UTF-8 urls by quoting them
    scheme, netloc, path, query, fragment = parse.urlsplit(url)
    path = parse.quote(path)
    url = parse.urlunsplit((scheme, netloc, path, query, fragment))
    
    page = http.request('GET', url)
    soup = BeautifulSoup(page.data)
    int_id = stan_id[stan_id[:-8].rfind('-') + 1:-8]
    ogl_details_elem = soup.select('div.ogl_details')[0]
    title = ogl_details_elem.select('div.detail_bar_nek > h2')[0].text
    published_date = ogl_details_elem.select('div.detail_right > table.status > tr > td.posted')[0].text
    published_date = datetime.datetime.strptime(published_date.strip()[17:], '%d.%m.%Y')
    modified_date = published_date # for halooglasi we don't have modified date
    
    price = None
    if 'Dogovor' not in ogl_details_elem.select('div.detail_bar_nek > div.price')[0].text:
        price = int(ogl_details_elem.select('div.detail_bar_nek > div.price')[0].text[:-1].replace('.', ''))
    
    area = rooms = None
    for main_data_elem in ogl_details_elem.select('div.detail_right > div.main_data > ul > li'):
        main_data_elem_type = main_data_elem.select('span')[0].text
        if main_data_elem_type == 'Tip': pass
        elif main_data_elem_type == 'Kvadratura':
            area = float(main_data_elem.select('h5')[0].text.strip().replace(',', '.')[:-2])
        elif main_data_elem_type == 'Broj soba':
            rooms = float(main_data_elem.select('h5')[0].text.strip().replace('+', ''))
        else:
            raise Exception('Unknown main data %s' % main_data_elem_type)
        
    street = heating_type_id = floor = total_floors = None
    legalized = useljivo = new_building = under_construction = 0
    for list_elem in ogl_details_elem.select('div.detail_right > div.additional_data > ul > li'):
        list_elem_type = list_elem.select('strong')[0].text
        list_elem_value = list_elem.contents[-1]
        if list_elem_type == 'Tip objekta':
            if list_elem_value == 'stara gradnja': pass
            elif list_elem_value == 'novogradnja': new_building = 1
            elif list_elem_value == 'u izgradnji': under_construction = 1
            else: raise Exception('Unknown tip objekta: %s' % list_elem_value)
        elif list_elem_type == 'Ulica': street = list_elem_value.strip()
        elif list_elem_type == 'Sprat': floor, total_floors = parse_floors(list_elem_value)
        elif list_elem_type == 'Uknjižen':
            if list_elem_value == 'Da': legalized = 1
            elif list_elem_value == 'Ne': legalized = 0
            else: raise Exception('Unknown uknjižen: %s' % list_elem_value)
        elif list_elem_type == 'Odmah useljiv':
            if list_elem_value == 'Da': useljivo = 1
            elif list_elem_value == 'Ne': useljivo = 0
            else: raise Exception('Unknown odmah useljiv: %s' % list_elem_value)
        elif list_elem_type == 'Grejanje': heating_type_id = HEATING_TYPE_DICT[list_elem_value]
        elif list_elem_type == 'Sprat': pass
        elif list_elem_type == 'Opis objekta': pass
        elif list_elem_type == 'Oglašivač nekretnine': pass
        elif list_elem_type == 'Može zamena': pass
        elif list_elem_type == 'Depozit': pass
        elif list_elem_type == 'Nameštenost': pass
        elif list_elem_type == 'Način plaćanja': pass
        else: raise Exception('Unknown list elem: %s' % list_elem_type)

    city, municipality, part, street = parse_cmps(ogl_details_elem.select('div.detail_bar_nek > h3')[0].text, street)
    
    construction_year = None
    elevator = sewer = intercom = phone = balcon = basement = cable_tv = aircondition = internet = parking = 0
    description = ''
    for txt_elem in ogl_details_elem.select('div.detail_right > div.txt > h3'):
        if txt_elem.text.strip() == 'Dodatno':
            additional = txt_elem.next_sibling.next_sibling.text.strip()
            for item in additional.split(','):
                item = item.strip()
                if item == 'podrum': basement = 1
                elif item == 'telefon': phone = 1
                elif item == 'interfon': intercom = 1
                elif item == 'internet': internet = 1
                elif item == 'klima': aircondition = 1
                elif item == 'topla voda': pass
                elif item == 'ktv': cable_tv = 1
                elif item == 'terasa': balcon = 1
                elif item == 'parking': parking = 1
                elif item == 'lift': elevator = 1
                elif item == 'garaža': pass
                elif item == 'lođa': pass
                else: raise Exception('Unknown additional element: %s' % item)
        elif txt_elem.text.strip() == 'Dodatni opis':
            description = txt_elem.next_sibling.next_sibling.text.strip()
        else:
            raise Exception('Unknown additional: %s' % txt_elem.text)
        
    stan_data = {'id': int_id, 'id_source': 2, 'title': title, 'url': url, 'published_date': published_date, 'modified_date': modified_date, 'type': 'stan', 'price': price,
                 'area': area, 'city': city, 'municipality': municipality, 'part': part, 'street': street, 'floor': floor, 'total_floors': total_floors, 'rooms': rooms,
                 'construction_year': construction_year, 'legalized': legalized, 'elevator': elevator, 'sewer': sewer, 'intercom': intercom, 'phone': phone,
                 'heating_type_id': heating_type_id, 'balcon': balcon, 'basement': basement, 'cable_tv': cable_tv, 'aircondition': aircondition, 'internet': internet,
                 'parking': parking, 'useljivo': useljivo, 'new_building': new_building, 'under_construction': under_construction, 'description': description}
    return stan_data

def process_stan(cnx, http, stan_id):
    print('Processing id %s' % stan_id)
    stan_data = get_stan_data(http, stan_id)
    if stan_data is None: raise Exception('Unknown error occured processing %s' % stan_id)
    upsert_stan(cnx, stan_data)
    cnx.commit()

if __name__ == '__main__':
    http = urllib3.PoolManager()
    cnx = pyodbc.connect('DRIVER={SQL Server};SERVER=%s;DATABASE=%s;UID=%s;PWD=%s' % (DB_SERVER, DB_NAME, DB_USERNAME, DB_PASSWORD))
    for stan_id in get_stan_ids(http):
        process_stan(cnx, http, stan_id)
    cnx.close()