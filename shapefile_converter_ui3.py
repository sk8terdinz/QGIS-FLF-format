import sys
import shapefile
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QVBoxLayout, QPushButton, QMessageBox, QPlainTextEdit
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
        self.saved_message_box = None
        self.point_shapefile = None

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
            # Create an in-memory point shapefile
            self.point_shapefile = shapefile.Writer(shapeType=shapefile.POINT)
            self.point_shapefile.field('Name', 'C', 255)

            lines = self.file_content.split('\n')[129:]  # Adjust the index to start from row 129

            point_data = []

            for line in lines:
                line = line.strip()

                if line.startswith("Line.szName"):
                    # Process a new section of data
                    if point_data:
                        self.addPointsToShapefile(point_data)
                        point_data = []

                elif line.startswith("#") or not line:
                    continue

                else:
                    row = line.split(',')
                    if len(row) >= 6:
                        easting = float(row[0])
                        northing = float(row[1])
                        kp = float(row[3])
                        point_data.append((easting, northing, kp))

            if point_data:
                self.addPointsToShapefile(point_data)

            # Define the file paths for the polyline shapefile
            shp_file_path = 'output_polyline.shp'
            shx_file_path = 'output_polyline.shx'
            dbf_file_path = 'output_polyline.dbf'

            # Create an in-memory polyline shapefile
            polyline_shapefile = shapefile.Writer(shp=shp_file_path, shx=shx_file_path, dbf=dbf_file_path, shapeType=shapefile.POLYLINE)
            polyline_shapefile.field('Name', 'C', 255)

            # Use the point data to create polyline features
            for idx, point in enumerate(point_data):
                if idx < len(point_data) - 1:
                    x1, y1, _ = point
                    x2, y2, _ = point_data[idx + 1]
                    polyline_shapefile.line([[(x1, y1), (x2, y2)]])
                    polyline_shapefile.record(f'Line_{idx + 1}')

            # Save the polyline shapefile
            polyline_shapefile.close()

            # Show a message box to inform the user that the polyline shapefile has been saved
            self.saved_message_box = QMessageBox()
            self.saved_message_box.setWindowTitle("Polyline Shapefile Saved")
            self.saved_message_box.setText(f"Polyline shapefile saved as {shp_file_path}")
            self.saved_message_box.exec_()

        except Exception as e:
            print(f"Error converting to polyline shapefile: {str(e)}")

    def addPointsToShapefile(self, point_data):
        for easting, northing, kp in point_data:
            self.point_shapefile.point(easting, northing)
            self.point_shapefile.record(f'Point_{easting}_{northing}_{kp}')

def main():
    app = QApplication(sys.argv)
    ex = ShapefileConverter()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
