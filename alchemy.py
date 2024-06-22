import sqlalchemy
import json
import sqlalchemy.orm
import alchmodels
import configparser


def configurate_session():
    config = configparser.ConfigParser()
    config.read("settings1.ini")
    login = config['Db']['login']
    dbname = config['Db']['dbname']
    password = config['Db']['password']

    DSN = f"postgresql://{login}:{password}@localhost:5432/{dbname}"
    engine = sqlalchemy.create_engine(DSN)

    alchmodels.drop_tables(engine)
    alchmodels.create_tables(engine)

    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    session = Session()
    return session


def queryresult(publishername):
    q = session.query(alchmodels.Stock) \
        .join(alchmodels.Stock.book) \
        .join(alchmodels.Stock.shop) \
        .join(alchmodels.Book.publisher) \
        .join(alchmodels.Stock.sale)
    if publishername.isdigit():
        result = q.filter(alchmodels.Publisher.id == publishername)
    else:
        result = q.filter(alchmodels.Publisher.name.like(f'{publishername}'))
    for s in result.all():
        return print(f'{s.book.title} | {s.shop.name} |'
                     f' {s.sale.price} | {s.sale.date_sale}')


def load_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def add_data(data):
    for record in data:
        model = {
            'publisher': alchmodels.Publisher,
            'shop': alchmodels.Shop,
            'book': alchmodels.Book,
            'stock': alchmodels.Stock,
            'sale': alchmodels.Sale,
        }
        models = model[record.get('model')]
        zapis = models(**record['fields'])
        session.add(zapis)
    session.commit()


if __name__ == "__main__":
    session = configurate_session()
    data = load_file('tests_data.json')
    add_data(data)
    publishername = input('Введите имя издателя или его id\n')
    queryresult(publishername)
    session.close()
