# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BPEJRUIANSWATDialog
                                 A QGIS plugin
 Plugin stahuje a upravuje data BPEJ a upravuje data RÚIAN pro model SWAT
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-03-26
        git sha              : $Format:%H$
        copyright            : (C) 2023 by Tomáš Hájek
        email                : tomas.hajek123@gmail.com
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

import os
import urllib.request
import re
import processing

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QAction
from qgis.core import edit, QgsProject, QgsVectorLayer, Qgis, QgsCoordinateReferenceSystem, QgsField, QgsExpressionContext, QgsExpression
from qgis.utils import iface

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'BPEJ_RUIAN_SWAT_dialog_base.ui'))


class BPEJRUIANSWATDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(BPEJRUIANSWATDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.pbclipBPEJ.clicked.connect(self.clip_bpej)
        self.pbLUparcely.clicked.connect(self.lu_parcely)
        self.pbdownloadBPEJ.clicked.connect(self.download_bpej)

    def clip_bpej(self):
        # let the user select input, output, and clip files using a file dialog
        input_file, _ = QFileDialog.getOpenFileName(None, "Select input file", "", "Shapefile (*.shp)")
        clip_file, _ = QFileDialog.getOpenFileName(None, "Select clip file", "", "Shapefile (*.shp)")
        output_file, _ = QFileDialog.getSaveFileName(None, "Select output file", "", "Shapefile (*.shp)")
        if not input_file:
            QMessageBox.critical(None, "Error", "Nebyly správně vložené vstupní a výstupní vrstvy")
            return
        # load input and clip layers
        layer = QgsVectorLayer(input_file, 'layer_name', 'ogr')
        msg_box = QMessageBox()
        msg_box.setText('Právě se chystáte zahájit opravu geometriií u vstupního souboru?')
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        result = msg_box.exec_()
        if result == QMessageBox.Ok:
        # Run the fix geometries algorithm
            result = processing.run('native:fixgeometries', {
                'INPUT': layer,
                'OUTPUT': 'memory:'
            })

        # Get the fixed layer from the result
            fixed_layer = result['OUTPUT']
            clip_layer = QgsVectorLayer(clip_file, 'layer_name', 'ogr')
            processing.run('native:clip', {
            'INPUT': fixed_layer,
            'OVERLAY': clip_layer,
            'OUTPUT': output_file,
            })
            clipped_layer = QgsVectorLayer(output_file, 'povodi_BPEJ', "ogr")
            field_names_to_keep = ['B5']
            fields = clipped_layer.fields()
            field_indices_to_remove = []
            for i, field in enumerate(fields):
                if field.name() not in field_names_to_keep:
                    field_indices_to_remove.append(i)
            clipped_layer.dataProvider().deleteAttributes(field_indices_to_remove)
            clipped_layer.updateFields()
            clipped_layer.commitChanges()
        # Add the fixed layer to the QGIS project
            QgsProject.instance().addMapLayer(clipped_layer)

            if not clipped_layer.isValid():
                QMessageBox.critical(None, "Error", "Oprava geometrií neproběhla nebo výřez neproběhli v pořádku, zkontrolujte vstupní data.")
            else:
                QMessageBox.information(None, "Gratuluji!", "Oprava, výřez a úprava dat úspěšně provedena.")

        #dodělat mazání sloupců

    def lu_parcely(self):
        # set the path to the original shapefile
        input_path, _ = QFileDialog.getOpenFileName(None, "Select Input Shapefile", "", "Shapefiles (*.shp)")

        # load the shapefile into a QgsVectorLayer object
        layer = QgsVectorLayer(input_path, os.path.basename(input_path), 'ogr')
        if not layer.isValid():
            QMessageBox.critical(None, "Error", "Nepodařilo se nahrát vrstvu")
            return
        # get the current project instance
        project = QgsProject.instance()

        # add the layer to the project
        project.addMapLayer(layer)
        dialog = QFileDialog()
        dialog.setDefaultSuffix('.shp')
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setDirectory('.')
        dialog.setNameFilter('Shapefile (*.shp)')
        # add field "SWAT_LU" that is base on the values of ZpusobyVyu a DruhPozemk
        if dialog.exec_() == QFileDialog.Accepted:
            output_path = dialog.selectedFiles()[0]
        else:
            output_path = None
        if output_path is not None:
            layer = iface.activeLayer()  # Get the active layer
            if layer is not None:
                processing.runAndLoadResults("qgis:fieldcalculator", {
                'INPUT': layer,
                'FIELD_NAME': 'SWAT_LU',
                'FIELD_TYPE': 2,  # Set the data type to String
                'FIELD_LENGTH': 4,
                'FIELD_PRECISION': 0,
                'FORMULA': "CASE WHEN \"ZpusobyVyu\" is '6' or \"ZpusobyVyu\" is '7' or \"ZpusobyVyu\" is '8' or \"ZpusobyVyu\" is '9' or \"ZpusobyVyu\" is '10' or \"ZpusobyVyu\" is '28' THEN 'WATR' WHEN \"ZpusobyVyu\" is '12' or \"ZpusobyVyu\" is '13' or \"ZpusobyVyu\" is '23' or \"ZpusobyVyu\" is '26' THEN 'URML' WHEN \"ZpusobyVyu\" is '20' or \"ZpusobyVyu\" is '21' THEN 'UCOM' WHEN \"ZpusobyVyu\" is '25' THEN 'UIDU' WHEN \"ZpusobyVyu\" is '14' or \"ZpusobyVyu\" is '15' or \"ZpusobyVyu\" is '16' or \"ZpusobyVyu\" is '17' or \"ZpusobyVyu\" is '18' or \"ZpusobyVyu\" is '19' THEN 'UTRN' WHEN \"ZpusobyVyu\" is '24' THEN 'SWRN' WHEN \"ZpusobyVyu\" is '3' or \"ZpusobyVyu\" is '4' or \"ZpusobyVyu\" is '5' THEN 'FRST' WHEN \"ZpusobyVyu\" is '1' or \"ZpusobyVyu\" is '2' THEN 'ORCD' WHEN \"ZpusobyVyu\" is '27' THEN 'AGRL' WHEN \"ZpusobyVyu\" is '11' THEN 'WETN' WHEN \"DruhPozemk\" is '11' THEN 'WATR' WHEN \"DruhPozemk\" is '5' or \"DruhPozemk\" is '13' or \"DruhPozemk\" is '14' THEN 'URML' WHEN \"DruhPozemk\" is '10' THEN 'FRST' WHEN \"DruhPozemk\" is '3' or \"DruhPozemk\" is '4' or \"DruhPozemk\" is '6' THEN 'ORCD' WHEN \"DruhPozemk\" is '7' THEN 'RNGE' WHEN \"DruhPozemk\" is '2' THEN 'AGRL' END",
                'OUTPUT': output_path
            })
            layer.updateFields()

        result_layer = QgsVectorLayer(output_path, "result_layer", "ogr")
        field_names_to_keep = ['SWAT_LU']
        fields = result_layer.fields()
        field_indices_to_remove = []
        for i, field in enumerate(fields):
            if field.name() not in field_names_to_keep:
                field_indices_to_remove.append(i)

        # remove the fields from the layer
        result_layer.dataProvider().deleteAttributes(field_indices_to_remove, )
        result_layer.updateFields()
        result_layer.commitChanges()
        QMessageBox.information(None, "Gratulace", "Vrstva je připravena k dalšímu zpracování")


    def download_bpej(self):
        your_url = "https://www.spucr.cz/bpej/celostatni-databaze-bpej/aktualni-databaze-bpej-ke-stazeni.html"

        response = urllib.request.urlopen(your_url)
        html_code = response.read().decode()

        url_regex = re.compile(
            r'<a\s+target="_blank"\s+href="(/frontend/webroot/uploads/files/[\d/]+(bpej_[\d]+\.zip))"')
        url_match = url_regex.search(html_code)

        if url_match:
            url = "https://www.spucr.cz" + url_match.group(1)
            downloads_dir = os.path.join(os.path.expanduser("~"), "downloads")
            file_name = os.path.join(downloads_dir, url_match.group(2))  # Modify file_name to include downloads folder path

            try:
                urllib.request.urlretrieve(url, file_name,)
                QMessageBox.information(None, "Gratulace!", "Data BPEJ jsou stažená ve složce downloads/stažené soubory")



            except (urllib.error.URLError, urllib.error.HTTPError) as e:
                print("Error occurred while downloading the file:", e)
            except ConnectionError as e:
                print("Network connection error:", e)

        else:
            QMessageBox.critical(None, "Error", "URL nenalezeno")