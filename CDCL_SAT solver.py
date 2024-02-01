from pysat.solvers import Glucose4
from collections import defaultdict
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox, QInputDialog, QTextEdit

class CDCLSolver:
    def __init__(self, enable_cnf_transformation=False, enable_subsumption=False, enable_forgetting=False):
        self.solver = Glucose4()
        self.watches = defaultdict(list)  # Dictionary to store watched literals
        self.activity = defaultdict(int)  # Dictionary to store variable activity
        self.conflicts = []  # List to store encountered conflicts
        self.enable_cnf_transformation = enable_cnf_transformation
        self.enable_subsumption = enable_subsumption
        self.enable_forgetting = enable_forgetting
        self.learned_clauses = []  # List to store learned clauses
        self.unsat_proof = []  # List to store unsatisfiability proof


    def add_clause(self, clause):
        self.solver.add_clause(clause)
        # Initialize watched literals for each variable
        for lit in clause:
            self.watches[lit].append(clause)

    def solve(self):
        while True:
            result = self.solver.solve()
            if result == True:
                return True, self.solver.get_model()
            elif result == False:
                return False, self.unsat_proof  # Return the unsatisfiability proof
            else:
                conflict = self.propagate_watched_literals()
                if conflict:
                    self.conflicts.append(conflict)
                    if self.enable_subsumption:
                        self.subsume_learned_clauses(conflict)
                    if self.enable_forgetting:
                        self.forget_clauses()
                self.decide_variable()

    def propagate_watched_literals(self):
        for clause in self.solver.clauses:
            if clause[0] in self.solver.model or clause[1] in self.solver.model:
                # At least one watched literal is satisfied
                continue
            
            unassigned_literals = [lit for lit in clause if -lit not in self.solver.model]
            if len(unassigned_literals) == 0:
                # All literals are false, conflict detected
                return clause
            
            if len(unassigned_literals) == 1:
                # Unit clause, propagate
                self.solver.add_clause([unassigned_literals[0]])
                break
            
            # Find new watched literal
            for lit in unassigned_literals[2:]:
                if lit in self.watches[-lit]:
                    # Found unassigned literal to watch
                    self.watches[-lit].remove(lit)
                    self.watches[-lit].append(unassigned_literals[1])
                    self.watches[unassigned_literals[1]].append(-lit)
                    break
        return None

    def decide_variable(self):
        # Choose variable with highest activity score
        max_activity = 0
        selected_var = None
        for var in range(1, self.solver.nof_vars() + 1):
            if var not in self.solver.model and -var not in self.solver.model:
                # Variable is unassigned
                if self.activity[var] > max_activity:
                    max_activity = self.activity[var]
                    selected_var = var
        return selected_var

    def generate_proof(self):
        # Trace back conflicts to construct the proof
        proof = []
        for conflict_clause in self.conflicts:
            resolution_clause = []
            for lit in conflict_clause:
                if lit > 0 and self.solver.level(abs(lit)) > 0:
                    # Variable was involved in conflict and was assigned at decision level > 0
                    resolution_clause.append(-lit)
            proof.append(resolution_clause)
        return proof

    def subsume_learned_clauses(self, conflict):
        # Subsume learned clauses if possible
        learned_clauses_to_remove = []
        for learned_clause in self.learned_clauses:
            if set(learned_clause).issubset(set(conflict)):
                learned_clauses_to_remove.append(learned_clause)
        for clause in learned_clauses_to_remove:
            self.solver.remove_clause(clause)
            self.learned_clauses.remove(clause)

    def forget_clauses(self):
        # Forget selectively learned clauses
        if len(self.learned_clauses) > 100:  # For example, forget if learned clauses exceed 100
            self.learned_clauses = self.learned_clauses[-50:]  # Keep only the last 50 learned clauses


def parse_cnf_file(file_path):
    clauses = []
    with open(file_path, 'r') as cnf_file:
        for line in cnf_file:
            line = line.strip()
            if not line or line.startswith('c') or line.startswith('p') or line.startswith('%') or line == '0':
                continue  # Skip comments, problem descriptions, empty lines, and lines with only '0'
            else:
                clause = list(map(int, line.split()))
                if clause[-1] == 0:
                    clause.pop()  # Remove the trailing 0
                    clauses.append(clause)
                else:
                    raise ValueError("Invalid CNF format: Each clause should end with 0.")
    return clauses

def to_cnf(clauses):
    cnf_clauses = []
    for clause in clauses:
        if len(clause) > 2:
            # Apply distribution to convert to CNF
            new_clauses = []
            for i in range(len(clause) - 1):
                new_clause = [clause[i]]
                for j in range(i + 1, len(clause)):
                    new_clause.append(clause[j])
                    new_clauses.append(new_clause.copy())
            cnf_clauses.extend(new_clauses)
        else:
            cnf_clauses.append(clause)
    return cnf_clauses

def solve_sat_from_file(cnf_file_path, enable_cnf_transformation=False, enable_subsumption=False, enable_forgetting=False):
    cnf_clauses = parse_cnf_file(cnf_file_path)
    solver = CDCLSolver(enable_cnf_transformation, enable_subsumption, enable_forgetting)
    for clause in cnf_clauses:
        solver.add_clause(clause)
    solved, model_or_proof = solver.solve()
    if solved:
        return "SAT", model_or_proof
    else:
        return "UNSAT", model_or_proof

def solve_sat_from_text(cnf_text, enable_cnf_transformation=False, enable_subsumption=False, enable_forgetting=False):
    # Check if the input contains non-integer values
    try:
        cnf_clauses = [list(map(int, line.split())) for line in cnf_text.split('\n') if line.strip()]
    except ValueError:
        QMessageBox.warning(None, "Invalid Input", "Please enter only integer values separated by spaces or newlines.")
        return None, None

    # Filter out clauses that contain only zeros
    cnf_clauses = [clause for clause in cnf_clauses if any(lit != 0 for lit in clause)]

    # Check if the input is in CNF form
    if not all(len(clause) == 1 or (len(clause) > 1 and clause[-1] == 0) for clause in cnf_clauses):
        # Input is not in CNF form, convert to CNF
        cnf_clauses = to_cnf(cnf_clauses)
        # Show the converted CNF in a message box
        converted_text = '\n'.join(' '.join(map(str, clause)) for clause in cnf_clauses)
        QMessageBox.information(None, "Converted to CNF", "The input has been converted to CNF:\n\n" + converted_text)

    solver = CDCLSolver(enable_cnf_transformation, enable_subsumption, enable_forgetting)
    for clause in cnf_clauses:
        solver.add_clause(clause)
    solved, model_or_proof = solver.solve()
    if solved:
        return "SAT", model_or_proof
    else:
        return "UNSAT", model_or_proof


def solve_sat(enable_cnf_transformation=False, enable_subsumption=False, enable_forgetting=False):
    app = QApplication([])

    # Ask the user for the input method
    input_method, ok = QInputDialog.getItem(None, "Input Method", "Choose input method:", ["File", "Text"], 0, False)
    if not ok:
        app.quit()
        return None, None

    if input_method == "File":
        file_dialog = QFileDialog()
        cnf_file_path, _ = file_dialog.getOpenFileName(None, "Select a CNF file")
        app.quit()
        if cnf_file_path:
            return solve_sat_from_file(cnf_file_path, enable_cnf_transformation, enable_subsumption, enable_forgetting)
        else:
            return None, None
    elif input_method == "Text":
        cnf_text, ok = QInputDialog.getMultiLineText(None, "Enter CNF Formula", "Enter CNF formula:")
        app.quit()
        if ok:
            return solve_sat_from_text(cnf_text, enable_cnf_transformation, enable_subsumption, enable_forgetting)
        else:
            return None, None
    else:
        return None, None

def convert_to_cnf(text_edit):
    text = text_edit.toPlainText()
    result, _ = solve_sat_from_text(text, enable_cnf_transformation=True)
    if result == "SAT":
        QMessageBox.information(None, "Satisfiable", "The formula is already in CNF.")
    else:
        QMessageBox.information(None, "Converted to CNF", "The formula has been converted to CNF.")

def main():
    app = QApplication([])

    while True:
        # Ask the user for the input method
        input_method, ok = QInputDialog.getItem(None, "Input Method", "Choose input method:", ["File", "Text"], 0, False)
        if not ok:
            break  # Exit loop if the user closes the dialog

        if input_method == "File":
            file_dialog = QFileDialog()
            cnf_file_path, _ = file_dialog.getOpenFileName(None, "Select a CNF file")
            if cnf_file_path:
                result, model_or_proof = solve_sat_from_file(cnf_file_path, enable_cnf_transformation=True)
                if result == "SAT":
                    QMessageBox.information(None, "Satisfiable with model", str(model_or_proof))
                else:
                    QMessageBox.information(None, "Unsatisfiable", str(model_or_proof))
            else:
                QMessageBox.information(None, "Error", "No file selected.")
        elif input_method == "Text":
            cnf_text, ok = QInputDialog.getMultiLineText(None, "Enter CNF Formula", "Enter CNF formula to convert:")
            if ok:
                if not cnf_text.strip():  # Check if input is empty
                    QMessageBox.warning(None, "Warning", "Please input a clause to convert or there is no input.")
                else:
                    result, model_or_proof = solve_sat_from_text(cnf_text, enable_cnf_transformation=True)
                    if result == "SAT":
                        QMessageBox.information(None, "Satisfiable with model", str(model_or_proof))
                    elif result == "UNSAT":
                        QMessageBox.information(None, "The CNF is Unsatisfiable", str(model_or_proof))
            else:
                QMessageBox.information(None, "Error", "No CNF formula entered.")

    app.exec_()


if __name__ == "__main__":
    main()
