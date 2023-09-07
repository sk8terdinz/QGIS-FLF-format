# -*- coding: utf-8 -*-
"""
Created on Mon Sep 4 12:06:28 2023

@author: diens
"""


import sys
import shapefile
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QPlainTextEdit, QVBoxLayout, QPushButton, QMessageBox
from PyQt5.uic import loadUi
import io

class ShapefileConverter(QDialog):
    def __init__(self):
        super().__init__()
        loadUi('shapefile_converter.ui', self)

        self.load_button = QPushButton("Load *.FLF File")
        self.convert_button = QPushButton("Convert to Polyline Shapefile")
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
            lines = self.file_content.split('\n')[126:]
            recording = False
            point_list = []
            line_groups = []
            line_name = None  # To store the attribute name
    
            # In-memory storage for point shapefile
            point_shp_file = io.BytesIO()
            point_shx_file = io.BytesIO()
            point_dbf_file = io.BytesIO()
    
            w_point = shapefile.Writer(shp=point_shp_file, shx=point_shx_file, dbf=point_dbf_file, shapeType=shapefile.POINT)
            w_point.field('Name', 'C', 255)
    
            for line in lines:
                if line.startswith("Line.szName"):
                    recording = True
                    line_name = line[41:].strip()  # Extract the attribute name from column 42 to the end
                    if point_list:
                        line_groups.append((line_name, point_list))
                        point_list = []
                elif line.startswith("#"):
                    recording = False
    
                if recording:
                    row = line.strip().split(',')
                    if len(row) >= 3:
                        easting = float(row[0])
                        northing = float(row[1])
                        w_point.point(easting, northing)
                        w_point.record(f'Point_{easting}_{northing}')
                        point_list.append((easting, northing))
    
            if point_list:
                line_groups.append((line_name, point_list))
    
            w_point.close()
            print("Point shapefile created in memory")
    
            # Create polyline shapefile in memory
            polyline_shp_file = io.BytesIO()
            polyline_shx_file = io.BytesIO()
            polyline_dbf_file = io.BytesIO()
    
            w_polyline = shapefile.Writer(shp=polyline_shp_file, shx=polyline_shx_file, dbf=polyline_dbf_file, shapeType=shapefile.POLYLINE)
            w_polyline.field('Name', 'C', 255)
    
            for line_name, points in line_groups:
                w_polyline.line([points])
                w_polyline.record(line_name)
    
            w_polyline.close()
    
            # Save shapefiles
            shp_filename, _ = QFileDialog.getSaveFileName(self, 'Save Polyline Shapefile', '', 'Shapefiles (*.shp)')
            if shp_filename:
                shx_filename = shp_filename.replace('.shp', '.shx')
                dbf_filename = shp_filename.replace('.shp', '.dbf')
    
                with open(shp_filename, 'wb') as shp_file:
                    shp_file.write(polyline_shp_file.getvalue())
                with open(shx_filename, 'wb') as shx_file:
                    shx_file.write(polyline_shx_file.getvalue())
                with open(dbf_filename, 'wb') as dbf_file:
                    dbf_file.write(polyline_dbf_file.getvalue())
    
                print(f"Polyline shapefile saved as {shp_filename}")
                print(f"Polyline .shx file saved as {shx_filename}")
                print(f"Polyline .dbf file saved as {dbf_filename}")
    
                # Show a message box to inform the user that the polyline shapefile has been saved
                self.saved_message_box = QMessageBox()
                self.saved_message_box.setWindowTitle("Polyline Shapefile Saved")
                self.saved_message_box.setText(f"Polyline shapefile saved as {shp_filename}\n"
                                               f".shx file saved as {shx_filename}\n"
                                               f".dbf file saved as {dbf_filename}")
                self.saved_message_box.exec_()
    
        except Exception as e:
            print(f"Error converting to polyline shapefile: {str(e)}")



def main():
    app = QApplication(sys.argv)
    ex = ShapefileConverter()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
