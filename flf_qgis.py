# -*- coding: utf-8 -*-
"""
Created on Mon Sep 4 12:06:28 2023

@author: diens
"""

import sys
import shapefile
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QTextEdit, QFileDialog
from shapefile_converter_ui import Ui_MainWindow  # Import the generated UI

class ShapefileConverter(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.button.clicked.connect(self.convertToShapefile)

    def convertToShapefile(self):
        text = self.text_edit.toPlainText()
        if not text:
            return

        try:
            lines = text.split('\n')
            # Assuming your columns are separated by commas
            rows = [line.split(',') for line in lines[130:]]  # Skip the first 130 lines

            shp_filename, _ = QFileDialog.getSaveFileName(self, 'Save Shapefile', '', 'Shapefiles (*.shp)')

            if shp_filename:
                w = shapefile.Writer(shp_filename, shapefile.POLYLINE)
                w.field('Easting', 'N', 10)
                w.field('Northing', 'N', 10)
                w.field('Kp', 'N', 10)

                for row in rows:
                    if len(row) >= 3:
                        easting = float(row[0])
                        northing = float(row[1])
                        kp = float(row[3])
                        w.line([[(easting, northing)]])
                        w.record(easting, northing, kp)

                w.save(shp_filename)
                print(f"Shapefile saved as {shp_filename}")

        except Exception as e:
            print(f"Error converting to shapefile: {str(e)}")

def main():
    app = QApplication(sys.argv)
    ex = ShapefileConverter()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
