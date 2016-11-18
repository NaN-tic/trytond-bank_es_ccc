# This file is part of bank_es module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from stdnum.es import ccc

from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = ['Number']


class Number:
    __name__ = 'bank.account.number'
    __metaclass__ = PoolMeta

    @classmethod
    def __setup__(cls):
        super(Number, cls).__setup__()
        spanish = ('es_ccc', 'Spanish Cuenta Corriente')
        if spanish not in cls.type.selection:
            cls.type.selection.append(spanish)
        cls._error_messages.update({
                'invalid_es_ccc': 'Invalid Spanish Cuenta Corriente "%s".',
                })

    @classmethod
    def create_iban_from_es_ccc(cls, numbers):
        to_save = []
        for number in numbers:
            if number.type != 'es_ccc':
                continue
            iban = ccc.to_iban(number.number_compact)
            found = False
            for existing in number.account.numbers:
                if (existing.type == 'iban'
                        and existing.number_compact == iban):
                    found = True
                    break
            if not found:
                if not number.sequence:
                    number.sequence = 20
                    to_save.append(number)
                new_number = cls(type='iban', number=iban)
                new_number.account = number.account
                new_number.sequence = number.sequence - 10
                to_save.append(new_number)
        if to_save:
            cls.save(to_save)

    @classmethod
    def create(cls, vlist):
        vlist = [v.copy() for v in vlist]
        for values in vlist:
            if values.get('type') == 'es_ccc' and 'number' in values:
                values['number'] = ccc.format(values['number'])
                values['number_compact'] = ccc.compact(values['number'])
        numbers = super(Number, cls).create(vlist)
        cls.create_iban_from_es_ccc(numbers)
        return numbers

    @classmethod
    def write(cls, *args):
        actions = iter(args)
        args = []
        all_numbers = []
        for numbers, values in zip(actions, actions):
            values = values.copy()
            if values.get('type') == 'es_ccc' and 'number' in values:
                values['number'] = ccc.format(values['number'])
                values['number_compact'] = ccc.compact(values['number'])
            args.extend((numbers, values))
            all_numbers.extend(numbers)

        super(Number, cls).write(*args)

        to_write = []
        for number in sum(args[::2], []):
            if number.type == 'es_ccc':
                formated_number = ccc.format(number.number)
                compacted_number = ccc.compact(number.number)
                if ((formated_number != number.number)
                        or (compacted_number != number.number_compact)):
                    to_write.extend(([number], {
                                'number': formated_number,
                                'number_compact': compacted_number,
                                }))
        if to_write:
            cls.write(*to_write)
        cls.create_iban_from_es_ccc(all_numbers)

    @fields.depends('type', 'number')
    def pre_validate(self):
        super(Number, self).pre_validate()
        if (self.type == 'es_ccc' and self.number
                and not ccc.is_valid(self.number)):
            self.raise_user_error('invalid_es_ccc', self.number)
