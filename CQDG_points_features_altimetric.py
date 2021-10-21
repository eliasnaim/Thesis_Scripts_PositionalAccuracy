from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Modelo(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterNumber('EntrecomodenominadordeEscaladesejado', 'Entre com o denominador de Escala', type=QgsProcessingParameterNumber.Double, minValue=0, maxValue=1e+09, defaultValue=1000))
        self.addParameter(QgsProcessingParameterVectorLayer('Entrecomosdadosaseremavaliados', 'Entre com os dados a serem avaliados', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('EntrecomosdadosdeReferncia', 'Entre com os dados de Referência', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Resultado', 'Resultado', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(8, model_feedback)
        results = {}
        outputs = {}

        # União
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'ID',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'ID',
            'INPUT': parameters['EntrecomosdadosdeReferncia'],
            'INPUT_2': parameters['Entrecomosdadosaseremavaliados'],
            'METHOD': 1,  # Tomar atributos apenas da primeira feição coincidente (uma-por-uma)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Unio'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Dz
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'Dz',
            'FIELD_PRECISION': 10,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '\"Ztest\" - \"Zref\"',
            'INPUT': outputs['Unio']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Dz'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # EMQ
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'EMQ',
            'FIELD_PRECISION': 50,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': 'sqrt(sum(\"Dz\"^2)/count(\"ID\"))',
            'INPUT': outputs['Dz']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Emq'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # va
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'va',
            'FIELD_PRECISION': 10,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': parameters['EntrecomodenominadordeEscaladesejado'],
            'INPUT': outputs['Emq']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Va'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Classe_A
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'Classe_A',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # String
            'FORMULA': 'CASE WHEN sum(\"Dz\"<=0.27*\"va\"/1000) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=0.17*\"va\"/1000\r\nTHEN \'Aceito\'\r\nELSE \'Rejeitado\'\r\nEND',
            'INPUT': outputs['Va']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Classe_a'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Classe_B
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'Classe_B',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # String
            'FORMULA': 'CASE WHEN sum(\"Dz\"<=0.50*\"va\"/1000) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=0.33*\"va\"/1000\r\nTHEN \'Aceito\'\r\nELSE \'Rejeitado\'\r\nEND',
            'INPUT': outputs['Classe_a']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Classe_b'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Classe_C
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'Classe_C',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # String
            'FORMULA': 'CASE WHEN sum(\"Dz\"<=0.60*\"va\"/1000) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=0.40*\"va\"/1000\r\nTHEN \'Aceito\'\r\nELSE \'Rejeitado\'\r\nEND',
            'INPUT': outputs['Classe_b']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Classe_c'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Classe_D
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'Classe_D',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # String
            'FORMULA': 'CASE WHEN sum(\"Dz\"<=0.75*\"va\"/1000) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=0.50*\"va\"/1000\r\nTHEN \'Aceito\'\r\nELSE \'Rejeitado\'\r\nEND',
            'INPUT': outputs['Classe_c']['OUTPUT'],
            'OUTPUT': parameters['Resultado']
        }
        outputs['Classe_d'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Resultado'] = outputs['Classe_d']['OUTPUT']
        return results

    def name(self):
        return 'modelo'

    def displayName(self):
        return 'modelo'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Modelo()
