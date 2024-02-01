# CDCL SAT Solver with CNF Conversion

## Overview

This project implements a Conflict-Driven Clause Learning (CDCL) SAT solver in Python using the Glucose4 solver from the PySAT library, capable of solving SAT problems, generating proofs for UNSAT problems, converting non-CNF formulas to CNF format, and incorporating subsumption and selective forgetting techniques for enhanced efficiency.

## Introduction

The CDCL solver implements the following features:
- Conflict-driven clause learning
- Two-literal watching scheme
- CNF transformation
- Subsumption and forgetting of learned clauses
- Graphical user interface for input (file or text) and result display
  
## Features

- **Efficient SAT Solving**: Utilizes the Glucose4 solver for efficient SAT problem resolution.
  ```python
  from pysat.solvers import Glucose4
  
  solver = Glucose4()
  result = solver.solve()
  ```
- **CNF Transformation**: Automatically converts non-CNF input formulas to CNF for compatibility.
  ```python
  def convert_to_cnf(input_formula):
    # Conversion code here
    return cnf_formula
  ```
- **Clause Subsumption**: Implements clause subsumption techniques to enhance solving efficiency.
- **Clause Forgetting**: Offers clause forgetting mechanisms to manage memory consumption during solving.
```python
   def apply_forgetting(learned_clauses):
    # Forgetting logic here
    return forgotten_clauses
```
- **Graphical User Interface (GUI)**: Provides an intuitive GUI interface for both file and text input methods using PyQt5.
```python
   from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton

     app = QApplication([]) ...
     window.show()
     app.exec_()
```
- **Proof Generation**: Capable of generating proofs for unsatisfiable instances, aiding in debugging and analysis.
  ```python
  def generate_proof(unsat_instance):
    # Proof generation logic here
    return proof
  ```


## Installation

1. Ensure you have Python 3.x installed on your system.
2. Install project dependencies using pip:

## Libraries Used
- **PySAT**: PySAT is a Python library for Boolean satisfiability (SAT) solving. It provides interfaces to various SAT solvers, including Glucose4, which is used in this project.
- **PyQt5**: PyQt5 is a set of Python bindings for the Qt application framework. It is used for creating the graphical user interface (GUI) for interacting with the SAT solver.

## CDCLSolver Class

The `CDCLSolver` class implements the CDCL algorithm for SAT solving. It utilizes the Glucose4 solver for the underlying SAT solving process. Key functionalities of this class include:
```python
class CDCLSolver:
    def __init__(self, enable_cnf_transformation=False, enable_subsumption=False, enable_forgetting=False):
        self.solver = Glucose4()
```
- Adding clauses to the solver.
- Propagating watched literals to detect conflicts.
- Making decisions based on variable activity.
- Generating proofs for encountered conflicts.
- Subsuming learned clauses and selectively forgetting clauses.

## Functions for CNF Conversion
The `parse_cnf_file()` function parses CNF files and extracts the clauses. The `to_cnf()` function converts non-CNF formulas to CNF format by applying distribution. These functions are used to preprocess input formulas before solving.
 ```python
  def convert_to_cnf(input_formula):
```

## User Interaction

The `solve_sat()` function provides an interface for users to interact with the SAT solver. It prompts the user to choose the input method (File or Text) and then invokes the corresponding solving function (`solve_sat_from_file()` or `solve_sat_from_text()`).
```bash
#Example
To solve a SAT problem, provide a CNF file or CNF text input through the GUI.
The solver will output whether the formula is satisfiable along with the model or the proof if unsatisfiable.
```
## GUI Integration
The `main()` function creates a graphical user interface using PyQt5. It presents options for inputting CNF formulas via file selection or text input. The solver then processes the input and displays the result in message boxes. The GUI remains active until the user closes the input dialog.

## Running the Program
To run the program, execute the script. The GUI will prompt you to choose the input method and provide the necessary input. The solver will then process the input and display the result accordingly.
## Contributing
Contributions are welcome! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request.

---
By Kidus D. Bellete
