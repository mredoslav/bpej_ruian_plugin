# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BPEJRUIANSWAT
                                 A QGIS plugin
 Plugin stahuje a upravuje data BPEJ a upravuje data RÚIAN pro model SWAT
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-03-26
        copyright            : (C) 2023 by Tomáš Hájek
        email                : tomas.hajek123@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load BPEJRUIANSWAT class from file BPEJRUIANSWAT.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .BPEJ_RUIAN_SWAT import BPEJRUIANSWAT
    return BPEJRUIANSWAT(iface)
