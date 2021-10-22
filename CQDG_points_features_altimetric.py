from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Modelo(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('entrecomosdadosdereferncia', 'Entre com os dados de Referência', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('entrecomosdadosaseremavaliados', 'Entre com os dados a serem avaliados', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Resultado', 'Resultado', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(11, model_feedback)
        results = {}
        outputs = {}

        # União
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'ID',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'ID',
            'INPUT': parameters['entrecomosdadosdereferncia'],
            'INPUT_2': parameters['entrecomosdadosaseremavaliados'],
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
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'EMQ',
            'FIELD_PRECISION': 10,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': 'sqrt(sum(\"Dz\"^2)/count(\"ID\"))',
            'INPUT': outputs['Dz']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Emq'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # 1:1000
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': '1:1000',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 2,  # String
            'FORMULA': 'CASE WHEN sum(\"Dz\"<=0.27) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=0.17\r\nTHEN \'Classe A\'\r\nWHEN sum(\"Dz\"<=0.50) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=0.33\r\nTHEN \'Classe B\'\r\nWHEN sum(\"Dz\"<=0.60) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=0.40\r\nTHEN \'Classe C\'\r\nWHEN sum(\"Dz\"<=0.75) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=0.50\r\nTHEN \'Classe D\' ELSE \'Rejeitado\'\r\nEND',
            'INPUT': outputs['Emq']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # 1:2000
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': '1:2000',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 2,  # String
            'FORMULA': 'CASE WHEN sum(\"Dz\"<=0.27) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=0.17\r\nTHEN \'Classe A\'\r\nWHEN sum(\"Dz\"<=0.50) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=0.33\r\nTHEN \'Classe B\'\r\nWHEN sum(\"Dz\"<=0.60) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=0.40\r\nTHEN \'Classe C\'\r\nWHEN sum(\"Dz\"<=0.75) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=0.50\r\nTHEN \'Classe D\' ELSE \'Rejeitado\'\r\nEND',
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # 1:5000
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': '1:5000',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 2,  # String
            'FORMULA': 'CASE WHEN sum(\"Dz\"<=0.54) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=0.34\r\nTHEN \'Classe A\'\r\nWHEN sum(\"Dz\"<=1.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=0.67\r\nTHEN \'Classe B\'\r\nWHEN sum(\"Dz\"<=1.20) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=0.80\r\nTHEN \'Classe C\'\r\nWHEN sum(\"Dz\"<=1.5) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=1.0\r\nTHEN \'Classe D\' ELSE \'Rejeitado\'\r\nEND',
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # 1:10000
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': '1:10000',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 2,  # String
            'FORMULA': 'CASE WHEN sum(\"Dz\"<=1.35) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=0.84\r\nTHEN \'Classe A\'\r\nWHEN sum(\"Dz\"<=2.5) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=1.67\r\nTHEN \'Classe B\'\r\nWHEN sum(\"Dz\"<=3.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=2.0\r\nTHEN \'Classe C\'\r\nWHEN sum(\"Dz\"<=3.75) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=2.5\r\nTHEN \'Classe D\' ELSE \'Rejeitado\'\r\nEND',
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # 1:25000
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': '1:25000',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 2,  # String
            'FORMULA': 'CASE WHEN sum(\"Dz\"<=2.7) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=1.67\r\nTHEN \'Classe A\'\r\nWHEN sum(\"Dz\"<=5.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=3.33\r\nTHEN \'Classe B\'\r\nWHEN sum(\"Dz\"<=6.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=4.0\r\nTHEN \'Classe C\'\r\nWHEN sum(\"Dz\"<=7.5) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=5.0\r\nTHEN \'Classe D\' ELSE \'Rejeitado\'\r\nEND',
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # 1:50000
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': '1:50000',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 2,  # String
            'FORMULA': 'CASE WHEN sum(\"Dz\"<=5.5) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=3.33\r\nTHEN \'Classe A\'\r\nWHEN sum(\"Dz\"<=10) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=6.67\r\nTHEN \'Classe B\'\r\nWHEN sum(\"Dz\"<=12.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=8.0\r\nTHEN \'Classe C\'\r\nWHEN sum(\"Dz\"<=15.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=10.0\r\nTHEN \'Classe D\' ELSE \'Rejeitado\'\r\nEND',
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # 1:100000
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': '1:100000',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 2,  # String
            'FORMULA': 'CASE WHEN sum(\"Dz\"<=13.7) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=8.33\r\nTHEN \'Classe A\'\r\nWHEN sum(\"Dz\"<=25) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=16.67\r\nTHEN \'Classe B\'\r\nWHEN sum(\"Dz\"<=30.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=20.0\r\nTHEN \'Classe C\'\r\nWHEN sum(\"Dz\"<=37.5) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=25.0\r\nTHEN \'Classe D\' ELSE \'Rejeitado\'\r\nEND',
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # 1:250000
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': '1:250000',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 2,  # String
            'FORMULA': 'CASE WHEN sum(\"Dz\"<=27.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=16.67\r\nTHEN \'Classe A\'\r\nWHEN sum(\"Dz\"<=50) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=33.33\r\nTHEN \'Classe B\'\r\nWHEN sum(\"Dz\"<=60.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=40.0\r\nTHEN \'Classe C\'\r\nWHEN sum(\"Dz\"<=75.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dz\"^2)/count(\"ID\"))<=50.0\r\nTHEN \'Classe D\' ELSE \'Rejeitado\'\r\nEND',
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': parameters['Resultado']
        }
        outputs[''] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Resultado'] = outputs['']['OUTPUT']
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
