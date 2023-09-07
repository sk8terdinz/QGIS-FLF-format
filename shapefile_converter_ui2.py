# -*- coding: utf-8 -*-
"""
Created on Mon Sep 4 12:06:28 2023

@author: diens
"""

import sys
import shapefile
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QPlainTextEdit, QVBoxLayout, QPushButton, QMessageBox
from PyQt5.uic import loadUi

class ShapefileConverter(QDialog):
    def __init__(self):
        super().__init__()
        loadUi('shapefile_converter.ui', self)

        self.load_button = QPushButton("Load *.FLF File")
        self.convert_button = QPushButton("Convert to Shapefile")
        self.text_edit = QPlainTextEdit()

        layout = QVBoxLayout()
        layout.addWidget(self.load_button)
        layout.addWidget(self.convert_button)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

        self.load_button.clicked.connect(self.loadFileAndDisplay)
        self.convert_button.clicked.connect(self.convertToShapefile)

        self.file_content = None
        self.saved_message_box = None  # Added to store the message box

    def loadFileAndDisplay(self):
        try:
            flf_filename, _ = QFileDialog.getOpenFileName(self, 'Open .flf File', '', 'FLF Files (*.flf)')

            if not flf_filename:
                return

            with open(flf_filename, 'r') as file:
                self.file_content = file.read()

            self.text_edit.setPlainText(self.file_content)

        except Exception as e:
            print(f"Error loading and displaying the file: {str(e)}")

    def convertToShapefile(self):
        if self.file_content is None:
            return

        try:
            lines = self.file_content.split('\n')[129:]

            shp_filename, _ = QFileDialog.getSaveFileName(self, 'Save Shapefile', '', 'Shapefiles (*.shp)')

            if shp_filename:
                w = shapefile.Writer(shp_filename, shapefile.POINT)
                w.field('Easting', 'N', 10)
                w.field('Northing', 'N', 10)
                w.field('Kp', 'N', 10)

                for line in lines:
                    row = line.strip().split(',')
                    if len(row) >= 3:
                        easting = float(row[0])
                        northing = float(row[1])
                        kp = float(row[3])
                        w.point(easting, northing)
                        w.record(easting, northing, kp)

                w.close()
                print(f"Point shapefile saved as {shp_filename}")

                # Show a message box to inform the user that the file has been saved
                self.saved_message_box = QMessageBox()
                self.saved_message_box.setWindowTitle("File Saved")
                self.saved_message_box.setText(f"Shapefile saved as {shp_filename}")
                self.saved_message_box.exec_()

        except Exception as e:
            print(f"Error converting to point shapefile: {str(e)}")

def main():
    app = QApplication(sys.argv)
    ex = ShapefileConverter()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
