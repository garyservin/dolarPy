#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import json
import requests
import urllib3
import calendar
import time
import os.path

from decimal import Decimal
from bs4 import BeautifulSoup
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def format_decimal(number):
    return str(number).replace('.', '').replace(',', '.')


def vision():
    soup = None
    try:
        soup = BeautifulSoup(
            requests.get('https://www.visionbanco.com', timeout=10,
                         headers={'user-agent': 'Mozilla/5.0'}, verify=False).text, "html.parser")

        efectivo = soup.select('#efectivo')[0]
        compra = efectivo.select('table > tr > td:nth-of-type(2) > p:nth-of-type(1)')[0].get_text().replace('.', '')
        venta  = efectivo.select('table > tr > td:nth-of-type(3) > p:nth-of-type(1)')[0].get_text().replace('.', '')

        online = soup.select('#online')[0]
        comprao = online.select('table > tr > td:nth-of-type(2) > p:nth-of-type(1)')[0].get_text().replace('.', '')
        ventao  = online.select('table > tr > td:nth-of-type(3) > p:nth-of-type(1)')[0].get_text().replace('.', '')
    except requests.ConnectionError:
        compra, venta, comprao, ventao = 0, 0, 0, 0
    except:
        compra, venta, comprao, ventao = 0, 0, 0, 0

    return Decimal(compra), Decimal(venta), Decimal(comprao), Decimal(ventao)


def bcp():
    try:
        soup = BeautifulSoup(
            requests.get('https://www.bcp.gov.py/webapps/web/cotizacion/monedas', timeout=10,
                         headers={'user-agent': 'Mozilla/5.0'}, verify=False).text, "html.parser")
        ref = soup.select(
            '#cotizacion-interbancaria > tbody > tr > td:nth-of-type(4)')[0].get_text()
        ref = ref.replace('.', '').replace(',', '.')
        soup = BeautifulSoup(
            requests.get(
                'https://www.bcp.gov.py/webapps/web/cotizacion/referencial-fluctuante', timeout=10,
                headers={'user-agent': 'Mozilla/5.0'}, verify=False).text, "html.parser")
        compra_array = soup.find(
            class_="table table-striped table-bordered table-condensed").select('tr > td:nth-of-type(4)')
        venta_array = soup.find(
            class_="table table-striped table-bordered table-condensed").select('tr > td:nth-of-type(5)')
        posicion = len(compra_array) - 1
        compra = compra_array[posicion].get_text(
        ).replace('.', '').replace(',', '.')
        venta = venta_array[posicion].get_text().replace(
            '.', '').replace(',', '.')
    except requests.ConnectionError:
        compra, venta, ref = 0, 0, 0
    except:
        compra, venta, ref = 0, 0, 0

    return Decimal(compra), Decimal(venta), Decimal(ref)


def setgov():
    try:
        soup = BeautifulSoup(
            requests.get('http://www.set.gov.py/portal/PARAGUAY-SET', timeout=10).text, "html.parser")
        compra = soup.find_all(class_="UITipoGrafiaCotizacion")[0].select('div')[
            1].contents[4].replace('.', '').replace(',', '.')
        venta = soup.find_all(class_="UITipoGrafiaCotizacion")[0].select('div')[
            2].contents[4].replace('.', '').replace(',', '.')
    except requests.ConnectionError:
        compra, venta = 0, 0
    except:
        compra, venta = 0, 0

    return Decimal(compra), Decimal(venta)


def create_data():
    bcpcompra, bcpventa, bcpref = bcp()
    setcompra, setventa = setgov()
    visioncompra, visionventa, visioncomprao, visionventao = vision()
    current_epoch = calendar.timegm(time.localtime())
    date_str = time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime())

    new_data = {
        '{}'.format(current_epoch): {
            'bcp': {
                'compra': bcpcompra,
                'venta': bcpventa,
                'referencial_diario': bcpref
            },
            'set': {
                'compra': setcompra,
                'venta': setventa
            },
            'vision': {
                'compra': visioncompra,
                'venta': visionventa,
                'compra_online': visioncomprao,
                'venta_online': visionventao
            },
	    'date': date_str
        },
    }

    return new_data


def get_current_data():
    with open('dolar.json', 'r') as f:
        response = f.read()
    return json.loads(response)


def write_output(json):
    with open('dolar.json', 'w') as f:
        f.write(json)

if __name__ == "__main__":
    json_data = {}

    if os.path.exists('dolar.json'):
        json_data = get_current_data()

    json_data.update(create_data())

    tmp = json.dumps(
        json_data, indent=4, sort_keys=True, separators=(',', ': '), default=decimal_default)

    write_output(tmp)
