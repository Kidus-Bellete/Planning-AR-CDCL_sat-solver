import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog

def generate_pigeonhole_clauses(n_pigeonholes, n_pigeons):
    clauses = []

    # Variables
    variables = [[i * n_pigeonholes + j + 1 for j in range(n_pigeonholes)] for i in range(n_pigeons + 1)]

    # Each pigeon is placed in some hole
    for i in range(1, n_pigeons + 1):
        clause = [variables[i][j] for j in range(n_pigeonholes)]
        clauses.append(clause)

    # Only one pigeon in each hole
    for j in range(n_pigeonholes):
        for i in range(1, n_pigeons + 1):
            for k in range(i + 1, n_pigeons + 1):
                clause = [-variables[i][j], -variables[k][j]]
                clauses.append(clause)

    return clauses

def save_cnf_file(cnf_clauses, file_path):
    with open(file_path, 'w') as cnf_file:
        cnf_file.write("p cnf {} {}\n".format(len(cnf_clauses[0]), len(cnf_clauses)))
        for clause in cnf_clauses:
            cnf_file.write(" ".join(map(str, clause)) + " 0\n")

class PigeonholeGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.pigeonhole_label = QLabel("Number of pigeonholes:")
        self.pigeonhole_entry = QLineEdit()
        layout.addWidget(self.pigeonhole_label)
        layout.addWidget(self.pigeonhole_entry)

        self.pigeons_label = QLabel("Number of pigeons:")
        self.pigeons_entry = QLineEdit()
        layout.addWidget(self.pigeons_label)
        layout.addWidget(self.pigeons_entry)

        generate_button = QPushButton("Generate CNF Clauses")
        generate_button.clicked.connect(self.generate_clauses)
        layout.addWidget(generate_button)

        self.setLayout(layout)
        self.setWindowTitle("Pigeonhole Problem Generator")

    def generate_clauses(self):
        n_pigeonholes = int(self.pigeonhole_entry.text())
        n_pigeons = int(self.pigeons_entry.text())

        cnf_clauses = generate_pigeonhole_clauses(n_pigeonholes, n_pigeons)

        file_path, _ = QFileDialog.getSaveFileName(self, "Save CNF File", "", "CNF Files (*.cnf)")

        if file_path:
            save_cnf_file(cnf_clauses, file_path)
            print(f"Pigeonhole clauses generated and saved to '{file_path}'.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PigeonholeGenerator()
    window.show()
    sys.exit(app.exec_())
