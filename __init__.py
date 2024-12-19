# SPDX-FileCopyrightText: 2008-2024 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2024 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                        HEALTH LAB package                             #
#              __init__.py: Package declaration file                    #
#########################################################################

from trytond.pool import Pool
from . import health_explo
from . import wizard
from . import sequences
# from .wizard import wizard_create_explo_test

__all__ = ['register']

def register():
    Pool.register(
        health_explo.PatientData,
        health_explo.TestType,
        health_explo.ExpTestType,
        health_explo.Exp,
        health_explo.GnuHealthExpTestUnits,
        health_explo.GnuHealthTestCritearea,
        health_explo.GnuHealthPatientExpTest,
        wizard.CreateExploTestOrderInit,
        wizard.RequestPatientExploTestStart,
        wizard.RequestTest,
        health_explo.PatientHealthCondition,
        sequences.GnuHealthSequences,
        sequences.ExpRequestSequence,
        sequences.ExpTestSequence,
        module='health_explo', type_='model')
    Pool.register(
        wizard.CreateExploTestOrder,
        wizard.RequestPatientExploTest,
        module='health_explo', type_='wizard')
