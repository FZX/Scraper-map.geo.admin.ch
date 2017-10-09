#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import csv
import json
import xlsxwriter
import requests
from bs4 import BeautifulSoup
from math import ceil
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import models

from bottle import route, run, template, request, static_file

engine = create_engine("sqlite:///./data.db")
Session = sessionmaker(bind=engine)
session = Session()


models.Base.metadata.create_all(engine)


def get_feature_id(address):
    search_link = "https://api3.geo.admin.ch/1710041248/rest/services/ech/" \
        "SearchServer?searchText={search_text}&lang=en&type=featuresearch&" \
        "bbox=746901.61,250960.6,747243.11,251032.6&features="\
        "ch.bfs.gebaeude_wohnungs_register&timeEnabled=" \
        "false&timeStamps=".format(search_text=address)
    respond = requests.get(search_link)
    feature_id = respond.json()["results"][0]["attrs"]["feature_id"]
    return feature_id


def get_popup(place_id):
    popup_link = "https://api3.geo.admin.ch/1710041248/rest/services/ech/" \
        "MapServer/ch.bfs.gebaeude_wohnungs_register/{place}/htmlPopup?" \
        "imageDisplay=1366,288,96&lang=en&mapExtent=" \
        "740223.115,249570.097,753883.115,252450.097".format(place=place_id)
    respond = requests.get(popup_link)
    return respond.text


def table_parser(data):
    soup = BeautifulSoup(data, "html.parser")
    rev = soup.findAll("tr")

    parsed_data = {}
    for i in rev:

        name, value = i.findAll("td")
        if len(name.text) > 0:
            parsed_data[name.text] = value.text
    return parsed_data


def write_csv(data):
    with open("./static/data.csv", "w") as csvfile:
        fields = list(data.keys())
        print(fields)

        writer = csv.DictWriter(csvfile, fieldnames=fields)

        writer.writeheader()
        writer.writerow(data)


def write_json(data):
    with open("./static/data.json", "w") as jsonfile:
        jsonfile.write(json.dumps(data))


def write_xlsx(data):
    workbook = xlsxwriter.Workbook("./static/data.xlsx")
    worksheet = workbook.add_worksheet()

    col = 0
    for name in (data.keys()):
        worksheet.write(0, col, name)
        col += 1

    col = 0
    row = 1

    for value in data.values():
        worksheet.write(row, col, value)
        col += 1
    col = 0
    row += 1
    workbook.close()


def write_db(data):
    new_row = models.Address(
        egid=data["EGID"],
        street=data["Street"],
        nr=data["Nr."],
        zip_code=data["Zip"],
        plz=data["PLZ6"],
        location=data["Location"],
        city=data["City"],
        bfs_number=data["BFS-Nummer"]
        )
    session.add(new_row)
    session.commit()

# address = "Schützenbergstrasse 12 9053 Teufen AR"

# data = table_parser(get_popup(get_feature_id(address)))
#write_xlsx(data)
# write_csv(data)
#write_json(data)
#write_db(data)

def select_addresses(page=None, search=None):

    MAX_ELEMENT = 10
    offset_num = MAX_ELEMENT
    if page:
        offset_num = MAX_ELEMENT * page

    address_count = session.query(func.count(models.Address.id))

    address = session.query(models.Address)
    address_count = address_count.first()
    off_num = address_count[0] - offset_num
    off_num = off_num if off_num >= 0 else 0
    address = address.order_by(models.Address.id)
    address = address.limit(MAX_ELEMENT)
    address = address.offset(off_num)
    address = address.all()

    pages = ceil(address_count[0] / MAX_ELEMENT)

    return address[::-1], pages


def pagination(pages, max_pages=10, current_page=1):
    """Pagination.

    At this moment works only with 10 shown pages.
    This is worst pagination ever you have seen
    in your life. Forgive me.
    """

    if pages > 10:
        if current_page > 4 and current_page < (pages - 4):
            start = current_page - 4
        elif (pages - current_page) <= 4:
            start = pages - max_pages + 1
        else:
            start = 1
    else:
        start = 1

    inc = 1
    while inc < max_pages + 1:
        if start < pages + 1:
            yield start
        inc += 1
        start += 1

@route("/")
def index():
    search = request.query.search
    page = int(request.query.page) if len(request.query.page) > 0 else 1
    data, pages = select_addresses(page=page)
    paginated = pagination(pages, current_page=page)
    return template("./templates/index.html", data=data, current_page=page,
                    paginated=paginated, pages=pages, search=search)

@route("/check_address", method="POST")
def check_address():
    print("I am here")
    address = request.forms.keyword
    if address:
        data = table_parser(get_popup(get_feature_id(address)))
        #write_xlsx(data)
        # write_csv(data)
        #write_json(data)
        write_db(data)
        return {"status": "success"}


def get_demo_data():
    address = "Schützenbergstrasse 12 9053 Teufen AR"

    data = table_parser(get_popup(get_feature_id(address)))
    return data


@route("/export/data.xlsx")
def export_data_xlsx():
    write_xlsx(get_demo_data())
    return static_file('data.xlsx', root='./static', download = 'data.xlsx')


@route("/export/data.csv")
def export_data_csv():
    write_csv(get_demo_data())
    return static_file('data.csv', root='./static', download = 'data.csv')


@route("/export/data.json")
def export_data_json():
    write_json(get_demo_data())
    return static_file('data.json', root='./static', download = 'data.json')


@route('/static/<filepath:path>')
def static_js(filepath):
    return static_file(filepath, root='./static/')


if __name__ == '__main__':
    run(host="localhost", port=8080, debug=True, reloader=True)
