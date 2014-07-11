DB_SERVER = 'gh45wmpmnu.database.windows.net'
DB_NAME = 'test'
DB_USERNAME = 'kokan@gh45wmpmnu'
DB_PASSWORD = '<password>'

ADD_STAN_SQL = ('INSERT INTO stanovi_stanovi '
              '(id, id_source, title, url, published_date, modified_date, type, price, area,'
              'city, municipality, part, street, floor, total_floors, rooms, construction_year, heating_type_id,'
              'legalized, elevator, sewer, intercom, phone, balcon, basement,'
              'cable_tv, aircondition, internet, parking, useljivo, new_building,'
              'under_construction, description) '
              'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,'
              '?, ?, ?, ?, ?, ?, ?, ?, ?,'
              '?, ?, ?, ?, ?, ?, ?,'
              '?, ?, ?, ?, ?, ?, '
              '?, ?)')

UPDATE_STAN_PRICE_SQL = ('UPDATE stanovi_stanovi SET price = ? WHERE id = ? AND id_source = ?')

def upsert_stan(cnx, stan_data):
    cursor = cnx.cursor()
    
    if stan_exists(cnx, stan_data['id'], stan_data['id_source']):
        price = get_stan_price(cnx, stan_data['id'], stan_data['id_source'])
        if price != stan_data['price']:
            cursor.execute(UPDATE_STAN_PRICE_SQL, stan_data['price'], stan_data['id'], stan_data['id_source'])
    else:
        cursor.execute(ADD_STAN_SQL,
            stan_data['id'], stan_data['id_source'], stan_data['title'], stan_data['url'], stan_data['published_date'], stan_data['modified_date'], stan_data['type'], stan_data['price'], stan_data['area'],
            stan_data['city'], stan_data['municipality'], stan_data['part'], stan_data['street'], stan_data['floor'], stan_data['total_floors'], stan_data['rooms'], stan_data['construction_year'], stan_data['heating_type_id'],
            stan_data['legalized'], stan_data['elevator'], stan_data['sewer'], stan_data['intercom'], stan_data['phone'], stan_data['balcon'], stan_data['basement'],
            stan_data['cable_tv'], stan_data['aircondition'], stan_data['internet'], stan_data['parking'], stan_data['useljivo'], stan_data['new_building'],
            stan_data['under_construction'], stan_data['description'])
        
def stan_exists(cnx, stan_id, id_source):
    cursor = cnx.cursor()
    cursor.execute('SELECT COUNT(id) FROM stanovi_stanovi WHERE id = ? AND id_source = ?', stan_id, id_source)
    return cursor.fetchone()[0] > 0

def get_stan_price(cnx, stan_id, id_source):
    cursor = cnx.cursor()
    cursor.execute('SELECT price FROM stanovi_stanovi WHERE id = ? AND id_source = ?', stan_id, id_source)
    return cursor.fetchone()[0]