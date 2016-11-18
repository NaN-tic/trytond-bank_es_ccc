# This file is part bank_es_ccc module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import bank


def register():
    Pool.register(
        bank.Number,
        module='bank_es_ccc', type_='model')
