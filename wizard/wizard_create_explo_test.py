# SPDX-FileCopyrightText: 2008-2024 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2024 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime
from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateTransition, StateView, Button
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.pyson import Eval, Not, Bool
from trytond.i18n import gettext
from ..exceptions import ExploOrderExists

__all__ = [
    'CreateExploTestOrderInit', 'CreateExploTestOrder', 'RequestTest',
    'RequestPatientExploTestStart', 'RequestPatientExploTest']


from trytond.modules.health.core import get_health_professional


class CreateExploTestOrderInit(ModelView):
    'Create Test Report Init'
    __name__ = 'gnuhealth.exp.test.create.init'


class CreateExploTestOrder(Wizard):
    'Create Explo Test Report'
    __name__ = 'gnuhealth.exp.test.create'

    start = StateView(
        'gnuhealth.exp.test.create.init',
        'health_explo.view_explo_make_test', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Create Test Order', 'create_explo_test', 'tryton-ok', True),
            ])

    create_explo_test = StateTransition()

    def transition_create_explo_test(self):
        TestRequest = Pool().get('gnuhealth.patient.exp.test')
        Explo = Pool().get('gnuhealth.exp')

        tests_report_data = []

        tests = TestRequest.browse(Transaction().context.get('active_ids'))

        for explo_test_order in tests:

            test_cases = []
            test_report_data = {}

            if explo_test_order.state == 'ordered':
                raise ExploOrderExists(
                    gettext('health_explo.msg_explo_order_exists')
                    )

            test_report_data['test'] = explo_test_order.name.id
            test_report_data['source_type'] = explo_test_order.source_type
            test_report_data['patient'] = explo_test_order.patient_id and explo_test_order.patient_id.id
            test_report_data['other_source'] = explo_test_order.other_source
            if explo_test_order.doctor_id:
                test_report_data['requestor'] = explo_test_order.doctor_id.id
            test_report_data['date_requested'] = explo_test_order.date
            test_report_data['request_order'] = explo_test_order.request

            for critearea in explo_test_order.name.critearea:
                test_cases.append(('create', [{
                        'name': critearea.name,
                        'code': critearea.code,
                        'sequence': critearea.sequence,
                        'lower_limit': critearea.lower_limit,
                        'upper_limit': critearea.upper_limit,
                        'normal_range': critearea.normal_range,
                        'units': critearea.units and critearea.units.id,
                    }]))
            test_report_data['critearea'] = test_cases

            tests_report_data.append(test_report_data)

        Explo.create(tests_report_data)
        TestRequest.write(tests, {'state': 'ordered'})

        return 'end'


class RequestEXPTest(ModelView):
    'Request - Test'
    __name__ = 'gnuhealth.request_test'
    _table = 'gnuhealth_request_test'

    request = fields.Many2One(
        'gnuhealth.patient.exp.test.request.start',
        'Request', required=True)
    test = fields.Many2One('gnuhealth.exp.test_type', 'Test', required=True)


class RequestPatientExploTestStart(ModelView):
    'Request Patient Explo Test Start'
    __name__ = 'gnuhealth.patient.exp.test.request.start'

    date = fields.DateTime('Date')
    source_type = fields.Selection([
        ('patient', 'Patient'),
        ('other_source', 'Other')
        ], 'Source', 
        help='Sample source type.',
        sort=False, select=True)
    patient = fields.Many2One('gnuhealth.patient', 
        'Patient',
        states={'invisible': (Eval('source_type') != 'patient')})
    other_source = fields.Char('Other', 
        states={'invisible': (Eval('source_type') != 'other_source')},
        help="Other sample source.")
    context = fields.Many2One(
        'gnuhealth.pathology', 'Context',
        help="Health context for this order. It can be a suspected or"
             " existing health condition, a regular health checkup, ...")
    doctor = fields.Many2One(
        'gnuhealth.healthprofessional', 'Health prof',
        help="Health professional who ordered the explo tests.")
    tests = fields.Many2Many('gnuhealth.request_test', 'request', 'test', 'Tests', required=True)
    urgent = fields.Boolean('Urgent')

    @staticmethod
    def default_date():
        return datetime.now()

    @staticmethod
    def default_source_type():
        return 'patient'

    @staticmethod
    def default_patient():
        if Transaction().context.get('active_model') == 'gnuhealth.patient':
            return Transaction().context.get('active_id')

    @staticmethod
    def default_doctor():
        return get_health_professional()


class RequestPatientExploTest(Wizard):
    'Request Patient Explo Test'
    __name__ = 'gnuhealth.patient.exp.test.request'

    start = StateView(
        'gnuhealth.patient.exp.test.request.start',
        'health_explo.patient_explo_test_request_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Request', 'request', 'tryton-ok', default=True),
            ])
    request = StateTransition()

    def generate_code(self, **pattern):
        Config = Pool().get('gnuhealth.sequences')
        config = Config(1)
        sequence = config.get_multivalue(
            'exp_request_sequence', **pattern)
        if sequence:
            return sequence.get()

    def transition_request(self):
        PatientExploTest = Pool().get('gnuhealth.patient.exp.test')
        request_number = self.generate_code()
        explo_tests = []
        for test in self.start.tests:
            explo_test = {}
            explo_test['request'] = request_number
            explo_test['name'] = test.id
            explo_test['source_type'] = self.start.source_type
            explo_test['patient_id'] = self.start.patient and self.start.patient.id
            explo_test['other_source'] = self.start.other_source
            if self.start.doctor:
                explo_test['doctor_id'] = self.start.doctor.id
            if self.start.context:
                explo_test['context'] = self.start.context.id
            explo_test['date'] = self.start.date
            explo_test['urgent'] = self.start.urgent
            explo_tests.append(explo_test)
        PatientExploTest.create(explo_tests)

        return 'end'
