# -*- coding: utf-8 -*-

"""
/***************************************************************************
 PontoControle
                                 A QGIS plugin
 Ferramentas para a gerência de pontos de controle
                              -------------------
        begin                : 2019-11-18
        copyright            : (C) 2019 by 1CGEO/DSG
        email                : eliton.filho@eb.mil.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = '1CGEO/DSG'
__date__ = '2019-11-18'
__copyright__ = '(C) 2019 by 1CGEO/DSG'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import subprocess
from pathlib import Path
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterString,
                       QgsProcessingParameterField,
                       QgsProcessingParameterNumber)
from qgis.PyQt.QtCore import QCoreApplication
from .handleLoadToBPC import HandleLoadToBPC


class LoadToBPC(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    OUTPUT = 'OUTPUT'
    FOLDERIN = 'FOLDERIN'
    FOLDEROUT = 'FOLDEROUT'
    SERVERIP = 'SERVERIP'
    PORT = 'PORT'
    BDNAME = 'BDNAME'
    USER = 'USER'
    PASSWORD = 'PASSWORD'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(
            QgsProcessingParameterFile(
                self.FOLDERIN,
                self.tr('Selecione a pasta com a estrutura de pontos de controle'),
                behavior=QgsProcessingParameterFile.Folder
            )
        )
        self.addParameter(
            QgsProcessingParameterFile(
                self.FOLDEROUT,
                self.tr('Selecione a pasta na qual serão gerados os arquivos:'),
                behavior=QgsProcessingParameterFile.Folder
            )
        )
        
        self.addParameter(
            QgsProcessingParameterString(
                self.SERVERIP,
                self.tr('Insira o IP do computador')
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.PORT,
                self.tr('Insira a porta')
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.BDNAME,
                self.tr('Insira o nome do banco de dados'),
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.USER,
                self.tr('Insira o usuário do PostgreSQL'),
            )
        )

        password = QgsProcessingParameterString(
            self.PASSWORD,
            self.tr('Insira a senha do PostgreSQL'),
        )
        password.setMetadata({
            'widget_wrapper':
            'ferramentas_pto_controle.utils.wrapper.MyWidgetWrapper'})

        self.addParameter(password)

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        folder_in = self.parameterAsFile(parameters, self.FOLDERIN, context)
        folder_out = self.parameterAsFile(parameters, self.FOLDEROUT, context)
        server_ip = self.parameterAsString(parameters, self.SERVERIP, context)
        port = self.parameterAsInt(parameters, self.PORT, context)
        bdname = self.parameterAsString(parameters, self.BDNAME, context)
        user = self.parameterAsString(parameters, self.USER, context)
        password = self.parameterAsString(parameters, self.PASSWORD, context)

        handle = HandleLoadToBPC(folder_in, folder_out)
        where_clausule = handle.getWhereClausule()

        db_string = "PG:dbname={} host={} port={} user={} password={}".format(
            bdname, server_ip, port, user, password)

        sql_string = f"SELECT * FROM bpc.ponto_controle_p {where_clausule}"

        gpkg_path = Path(folder_out, 'pontos_exportados.gpkg')

        subprocess.run(["ogr2ogr", "-f", "GPKG", f"{gpkg_path}", f"{db_string}", "-sql", f"{sql_string}"])

        return {self.OUTPUT: ''}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return '10- Preparar insumos para carregamento no BPC'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return None

    def shortHelpString(self):
        """
        Retruns a short helper string for the algorithm
        """
        return self.tr('''
        Esta ferramenta gera os insumos necessários para carregamento no BPC: o arquivo GeoPackage o(s) arquivo(s) zipados.
        Note que é necessário a execução da rotina de geração de monografia, uma vez que a monografia é necessária no zip a ser gerado.
        ''')

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return LoadToBPC()
