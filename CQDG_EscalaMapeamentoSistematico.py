"""
Model exported as python.
Name : escala definida
Group : 
With QGIS : 32003
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterEnum
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class EscalaDefinida(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('EntrecomosdadosdeReferncia', 'Entre com os dados de Referência', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('Entrecomosdadosaseremavaliados', 'Entre com os dados a serem avaliados', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterEnum('Escala', 'Escala', options=['1000','2000','5000','10000','25000','50000','100000','250000'], allowMultiple=False, usesStaticStrings=False, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Camada_final', 'Camada_Final', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(14, model_feedback)
        results = {}
        outputs = {}

        # E_ref
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'E_ref',
            'FIELD_PRECISION': 10,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '$x',
            'INPUT': parameters['EntrecomosdadosdeReferncia'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['E_ref'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # N_ref
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'N_ref',
            'FIELD_PRECISION': 10,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '$y',
            'INPUT': outputs['E_ref']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['N_ref'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # E_aval
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'E_aval',
            'FIELD_PRECISION': 10,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '$x',
            'INPUT': parameters['Entrecomosdadosaseremavaliados'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['E_aval'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # N_aval
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'N_aval',
            'FIELD_PRECISION': 10,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '$y',
            'INPUT': outputs['E_aval']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['N_aval'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # União
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'ID',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'ID',
            'INPUT': outputs['N_ref']['OUTPUT'],
            'INPUT_2': outputs['N_aval']['OUTPUT'],
            'METHOD': 1,  # Tomar atributos apenas da primeira feição coincidente (uma-por-uma)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Unio'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # DE
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'DE',
            'FIELD_PRECISION': 10,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': 'sqrt((( \"E_aval\" - \"E_ref\" )^\'2\')+(( \"N_aval\" - \"N_ref\")^\'2\'))',
            'INPUT': outputs['Unio']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['De'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # EMQ
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'EMQ',
            'FIELD_PRECISION': 10,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': 'sqrt(sum(\"DE\"^2)/count(\"ID\"))',
            'INPUT': outputs['De']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Emq'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Escala
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'Escala',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Número inteiro
            'FORMULA': 'CASE WHEN @Escala = \'0\' THEN 1000\r\nWHEN @Escala = \'1\' THEN 2000\r\nWHEN @Escala = \'2\' THEN 5000\r\nWHEN @Escala = \'3\' THEN 10000\r\nWHEN @Escala = \'4\' THEN 25000\r\nWHEN @Escala = \'5\' THEN 50000\r\nWHEN @Escala = \'6\' THEN 100000\r\nWHEN @Escala = \'6\' THEN 250000\r\nEND',
            'INPUT': outputs['Emq']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Escala'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # va
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'va',
            'FIELD_PRECISION': 8,
            'FIELD_TYPE': 1,  # Número inteiro
            'FORMULA': '\"Escala\"',
            'INPUT': outputs['Escala']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Va'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Classe_A
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'Classe_A',
            'FIELD_PRECISION': 10,
            'FIELD_TYPE': 2,  # String
            'FORMULA': 'CASE WHEN sum(\"DE\"<=0.28*\"va\"/1000) >= 0.9*count(\"ID\") AND sqrt(sum(\"DE\"^2)/count(\"ID\"))<=0.17*\"va\"/1000\r\nTHEN \'Aceito\'\r\nELSE \'Rejeitado\'\r\nEND',
            'INPUT': outputs['Va']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Classe_a'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Classe_B
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'Classe_B',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # String
            'FORMULA': 'CASE WHEN sum(\"DE\"<=0.50*\"va\"/1000) >= 0.9*count(\"ID\") AND sqrt(sum(\"DE\"^2)/count(\"ID\"))<=0.30*\"va\"/1000\r\nTHEN \'Aceito\'\r\nELSE \'Rejeitado\'\r\nEND',
            'INPUT': outputs['Classe_a']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Classe_b'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Classe_C
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'Classe_C',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # String
            'FORMULA': 'CASE WHEN sum(\"DE\"<=0.80*\"va\"/1000) >= 0.9*count(\"ID\") AND sqrt(sum(\"DE\"^2)/count(\"ID\"))<=0.50*\"va\"/1000\r\nTHEN \'Aceito\'\r\nELSE \'Rejeitado\'\r\nEND',
            'INPUT': outputs['Classe_b']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Classe_c'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Classe_D
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'Classe_D',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # String
            'FORMULA': 'CASE WHEN sum(\"DE\"<=1.0*\"va\"/1000) >= 0.9*count(\"ID\") AND sqrt(sum(\"DE\"^2)/count(\"ID\"))<=0.60*\"va\"/1000\r\nTHEN \'Aceito\'\r\nELSE \'Rejeitado\'\r\nEND',
            'INPUT': outputs['Classe_c']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Classe_d'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Descartar campo(s)
        alg_params = {
            'COLUMN': ['\'','ID_2','N_ref','E_ref','N_aval','E_aval',''],
            'INPUT': outputs['Classe_d']['OUTPUT'],
            'OUTPUT': parameters['Camada_final']
        }
        outputs['DescartarCampos'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Camada_final'] = outputs['DescartarCampos']['OUTPUT']
        return results

    def name(self):
        return 'escala definida'

    def displayName(self):
        return 'escala definida'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return EscalaDefinida()
