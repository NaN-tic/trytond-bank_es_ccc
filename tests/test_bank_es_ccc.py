# This file is part bank_es_ccc module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import unittest

from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.tests.test_tryton import suite as test_suite
from trytond.error import UserError
from trytond.pool import Pool


class BankEsCccTestCase(ModuleTestCase):
    'Test Bank Es Ccc module'
    module = 'bank_es_ccc'

    @with_transaction()
    def test_spanish_ccc_validation(self):
        'Spanish CCC Number'
        pool = Pool()
        Party = pool.get('party.party')
        Bank = pool.get('bank')
        Account = pool.get('bank.account')

        party = Party(name='Test')
        party.save()
        bank = Bank(party=party, bank_code='BNK')
        bank.save()
        with self.assertRaises(UserError):
            Account.create([{
                        'bank': bank.id,
                        'numbers': [('create', [{
                                        'type': 'es_ccc',
                                        'number': '1234-1234-00 1234567890',
                                        }])],
                        }])

    @with_transaction()
    def test_spanish_ccc_number(self):
        'Spanish CCC Number'
        pool = Pool()
        Party = pool.get('party.party')
        Bank = pool.get('bank')
        Account = pool.get('bank.account')

        party = Party(name='Test')
        party.save()
        bank = Bank(party=party, bank_code='BNK')
        bank.save()
        account, = Account.create([{
                    'bank': bank.id,
                    'numbers': [('create', [{
                                    'type': 'es_ccc',
                                    'number': '21000418400200051331',
                                    }])],
                    }])

        iban_number, es_number = account.numbers
        self.assertEqual(es_number.number_compact, '21000418400200051331')
        self.assertEqual(es_number.number, '2100 0418 40 02000 51331')
        self.assertEqual(iban_number.number_compact,
            'ES4021000418400200051331')

        account, = Account.create([{
                    'bank': bank.id,
                    'numbers': [('create', [{
                                    'type': 'other',
                                    'number': '21000418400200051331',
                                    }])],
                    }])

        # Test not created until es_ccc
        number, = account.numbers
        number.type = 'es_ccc'
        number.save()
        iban_number, es_number = account.numbers
        self.assertEqual(es_number.number_compact, '21000418400200051331')
        self.assertEqual(es_number.number, '2100 0418 40 02000 51331')
        self.assertEqual(iban_number.number_compact,
            'ES4021000418400200051331')
        # Test iban not duplicated
        account, = Account.create([{
                    'bank': bank.id,
                    'numbers': [('create', [{
                                    'type': 'es_ccc',
                                    'number': '21000418400200051331',
                                    }, {
                                    'type': 'iban',
                                    'number': 'ES4021000418400200051331',
                                    }])],
                    }])

        iban_number, es_number = account.numbers


def suite():
    suite = test_suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            BankEsCccTestCase))
    return suite
