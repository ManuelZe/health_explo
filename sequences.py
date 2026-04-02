# SPDX-FileCopyrightText: 2008-2024 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2024 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# GNU Health HMIS Exp sequences for this package

from trytond.model import (ModelSQL, ValueMixin, fields)
from trytond import backend
from trytond.pyson import Id
from trytond.pool import Pool, PoolMeta

# Sequences
exp_request_sequence = fields.Many2One(
    'ir.sequence', 'Exp request sequence', required=True,
    domain=[('sequence_type', '=', Id(
        'health_explo', 'seq_type_gnuhealth_exp_request'))])


exp_test_sequence = fields.Many2One(
    'ir.sequence', 'Exp test sequence', required=True,
    domain=[('sequence_type', '=', Id(
        'health_explo', 'seq_type_gnuhealth_exp_test'))])


# GNU HEALTH SEQUENCES
class GnuHealthSequences(metaclass=PoolMeta):
    'Standard Sequences for GNU Health'
    __name__ = 'gnuhealth.sequences'

    exp_request_sequence = fields.MultiValue(
        exp_request_sequence)

    exp_test_sequence = fields.MultiValue(
        exp_test_sequence)

    @classmethod
    def default_exp_request_sequence(cls, **pattern):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        try:
            return ModelData.get_id('health_explo',
                                    'seq_gnuhealth_exp_request')
        except KeyError:
            return None

    @classmethod
    def default_exp_test_sequence(cls, **pattern):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        try:
            return ModelData.get_id('health_explo',
                                    'seq_gnuhealth_exp_test')
        except KeyError:
            return None


class _ConfigurationValue(ModelSQL):

    _configuration_value_field = None

    @classmethod
    def __register__(cls, module_name):
        exist = backend.TableHandler.table_exist(cls._table)

        super(_ConfigurationValue, cls).__register__(module_name)


class ExpRequestSequence(_ConfigurationValue, ModelSQL, ValueMixin):
    'Exp Request Sequence setup'
    __name__ = 'gnuhealth.sequences.exp_request_sequence'
    exp_request_sequence = exp_request_sequence
    _configuration_value_field = 'exp_request_sequence'

    @classmethod
    def check_xml_record(cls, records, values):
        return True


class ExpTestSequence(_ConfigurationValue, ModelSQL, ValueMixin):
    'Exp Test Sequence setup'
    __name__ = 'gnuhealth.sequences.exp_test_sequence'
    exp_test_sequence = exp_test_sequence
    _configuration_value_field = 'exp_test_sequence'

    @classmethod
    def check_xml_record(cls, records, values):
        return True
