# Auto Lecturer Evaluation Program for PSU

## Overview
This program is designed to automate the process of evaluating lecturers on [PSU LES](https://les.psu.ac.th)).
Aim to improve and increase the efficiency of the teacher evaluation process by reducing the steps to complete all teacher evaluation forms within a short period of time.

The program developers suggest that some interesting lecturer be selected in the "Evaluate individually" is a better approach.

## Features
- **Automated Evaluation**: The program automates the process of evaluation the lecturers's performance.
- **Customizable Score**: It allows customization of evaluation score in config file and before evaluation process.
- **Secure Data Handling**: No login information is stored.

## Installation
1. Clone the repository:
    ```
    git clone https://github.com/k-affan-th/PSU-autoLES
    ```
2. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

## Usage
1. **Running the Program**:
    ```
    python main.py
    ```
2. **Read the step**:
    - Login through the command-line program
    - Confirm the score and wait ☕

## Configuration
- The default score is 3 but you can change in config file (`config.ini`) in `data` folder
- Nevermind if you did not change in the config file, You can also change the score before evaluation process too.

## Contributing
Contributions are welcome! If you have any suggestions, feature requests, or bug reports, please open an issue or submit a pull request.

## Acknowledgements
- Acknowledge any individuals or organizations whose work or contributions have inspired or supported the development of this program.

## Contact
For questions, support, or inquiries, contact [AffanK](mailto:k.affan.th@gmail.com).
