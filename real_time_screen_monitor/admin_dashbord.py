# import sys
# from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
# from PyQt5.QtCore import pyqtSlot
# import requests

# class AdminDashboard(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.title = 'Real-Time Screen Monitor Dashboard'
#         self.initUI()
    
#     def initUI(self):
#         self.setWindowTitle(self.title)
#         self.setGeometry(10, 10, 640, 480)
#         widget = QWidget(self)
#         self.setCentralWidget(widget)
#         layout = QVBoxLayout()

#         self.update_user_buttons()

#         widget.setLayout(layout)
#         self.show()

#     def update_user_buttons(self):
#         response = requests.get('http://localhost:5000/get_users')
#         users = response.json().get('users', {})
#         for username, details in users.items():
#             if details['online']:
#                 button = QPushButton(f"View {username}", self)
#                 button.clicked.connect(self.on_click)

#     @pyqtSlot()
#     def on_click(self):
#         button = self.sender()
#         username = button.text().split()[-1]
#         # Handle screen viewing logic here

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = AdminDashboard()
#     sys.exit(app.exec_())
