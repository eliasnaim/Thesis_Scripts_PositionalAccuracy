from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsExpression
import processing


class Modelo(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('EntrecomosdadosdeReferncia', 'Entre com os dados de Referência', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('Entrecomosdadosaseremavaliados', 'Entre com os dados a serem avaliados', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('EntrecomodenominadordeEscaladesejado', 'Entre com o denominador de Escala', type=QgsProcessingParameterNumber.Double, minValue=0, maxValue=1e+09, defaultValue=1000))
        self.addParameter(QgsProcessingParameterFeatureSink('Resultado', 'Resultado', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(12, model_feedback)
        results = {}
        outputs = {}

        # E_ref
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'E_ref',
            'FIELD_PRECISION': 10,
            'FIELD_TYPE': 0,
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
            'FIELD_TYPE': 0,
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
            'FIELD_TYPE': 0,
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
            'FIELD_TYPE': 0,
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
            'METHOD': 1,
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
            'FIELD_TYPE': 0,
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
            'FIELD_TYPE': 0,
            'FORMULA': 'sqrt(sum(\"DE\"^2)/count(\"ID\"))',
            'INPUT': outputs['De']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Emq'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Classe A
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'Classe A',
            'FIELD_PRECISION': 10,
            'FIELD_TYPE': 2,
            'FORMULA': 'CASE WHEN sum(\"DE\"<=0.28*@EntrecomodenominadordeEscaladesejado/1000) >= 0.9*count(\"ID\") AND sqrt(sum(\"DE\"^2)/count(\"ID\"))<=0.17*@EntrecomodenominadordeEscaladesejado/1000\r\nTHEN \'Aceito\'\r\nELSE \'Rejeitado\'\r\nEND',
            'INPUT': outputs['Emq']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ClasseA'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Classe B
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'Classe B',
            'FIELD_PRECISION': 10,
            'FIELD_TYPE': 2,
            'FORMULA': 'CASE WHEN sum(\"DE\"<=0.50*@EntrecomodenominadordeEscaladesejado/1000) >= 0.9*count(\"ID\") AND sqrt(sum(\"DE\"^2)/count(\"ID\"))<=0.30*@EntrecomodenominadordeEscaladesejado/1000\r\nTHEN \'Aceito\'\r\nELSE \'Rejeitado\'\r\nEND',
            'INPUT': outputs['ClasseA']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ClasseB'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Classe C
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'Classe C',
            'FIELD_PRECISION': 10,
            'FIELD_TYPE': 2,
            'FORMULA': 'CASE WHEN sum(\"DE\"<=0.80*@EntrecomodenominadordeEscaladesejado/1000) >= 0.9*count(\"ID\") AND sqrt(sum(\"DE\"^2)/count(\"ID\"))<=0.50*@EntrecomodenominadordeEscaladesejado/1000\r\nTHEN \'Aceito\'\r\nELSE \'Rejeitado\'\r\nEND',
            'INPUT': outputs['ClasseB']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ClasseC'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Classe D
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'Classe D',
            'FIELD_PRECISION': 10,
            'FIELD_TYPE': 2,
            'FORMULA': 'CASE WHEN sum(\"DE\"<=1.0*@EntrecomodenominadordeEscaladesejado/1000) >= 0.9*count(\"ID\") AND sqrt(sum(\"DE\"^2)/count(\"ID\"))<=0.60*@EntrecomodenominadordeEscaladesejado/1000\r\nTHEN \'Aceito\'\r\nELSE \'Rejeitado\'\r\nEND',
            'INPUT': outputs['ClasseC']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ClasseD'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Descartar campo(s)
        alg_params = {
            'COLUMN': QgsExpression('\'N_aval;N_ref;E_aval;E_ref;ID_2\'').evaluate(),
            'INPUT': outputs['ClasseD']['OUTPUT'],
            'OUTPUT': parameters['Resultado']
        }
        outputs['DescartarCampos'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Resultado'] = outputs['DescartarCampos']['OUTPUT']
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
