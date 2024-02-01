import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QMessageBox
from CDCL_SAT_solver import solve_sat_from_file

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

        generate_button = QPushButton("Generate Pigeons CNF Clauses")
        generate_button.clicked.connect(self.generate_clauses)
        layout.addWidget(generate_button)

        self.setLayout(layout)
        self.setWindowTitle("Pigeonhole Problem Generator")

    def generate_clauses(self):
        pigeonhole_text = self.pigeonhole_entry.text()
        pigeons_text = self.pigeons_entry.text()

        # Validate input to ensure it's an integer
        try:
            n_pigeonholes = int(pigeonhole_text)
            n_pigeons = int(pigeons_text)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid integer values for the number of pigeonholes and pigeons.")
            return

        # Ensure positive values
        if n_pigeonholes <= 0 or n_pigeons <= 0:
            QMessageBox.warning(self, "Invalid Input", "Please enter positive integer values for the number of pigeonholes and pigeons.")
            return

        cnf_clauses = generate_pigeonhole_clauses(n_pigeonholes, n_pigeons)

        file_path, _ = QFileDialog.getSaveFileName(self, "Save CNF File", "", "CNF Files (*.cnf)")

        if file_path:
            save_cnf_file(cnf_clauses, file_path)
            QMessageBox.information(self, "Generated", "Pigeons CNF Clauses Generated.")
            
            # Call CDCL solver to solve the generated CNF file
            result, model_or_proof = solve_sat_from_file(file_path)
            if result == "SAT":
                QMessageBox.information(self, "Satisfiable with model", str(model_or_proof))
            else:
                QMessageBox.information(self, "Unsatisfiable", str(model_or_proof))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PigeonholeGenerator()
    window.show()
    sys.exit(app.exec_())
