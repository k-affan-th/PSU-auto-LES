# Set path for configuration file
CONFIG_PATH = 'data/config.ini'

def print_welcome_screen():
    title = "PSU auto-LES by Kaff"
    box_width = len(title) + 4

    print("\n╔" + "═" * box_width + "╗")
    print("║  " + title + "  ║")
    print("╚" + "═" * box_width + "╝\n")
    print("Automated Lecturer Evaluation System")
    print("Powered by Python\n")
    input("Press Enter to continue...")

def main():

    # import library 
    import time
    import getpass
    from tqdm import trange
    from configparser import ConfigParser
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException

    # Call the function to print the welcome screen
    print_welcome_screen()

    def load_config(path: str = CONFIG_PATH):
        """
        Loads configuration values from a ConfigParser file and returns them as a dictionary.

        Args:
            path (str, optional): Path to the configuration file. Defaults to CONFIG_PATH.

        Returns:
            dict: A dictionary containing the configuration values with keys:
                - url (str): The URL to access.
                - score (int): The score value.
                - load_timeout (float): The timeout value for loading.

        Raises:
            FileNotFoundError: If the configuration file is not found at the specified path.
        """    
        config = ConfigParser()
        try:
            config.read(path)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Configuration file not found: {path}") from e

        return {
            "url": config.get("DEFAULT", "url"),
            "score": config.getint("DEFAULT", "score"),
            "mode": config.getint("DEFAULT", "mode"),
            "silent": config.getboolean("DEFAULT", "silent")
        }

    # Load the configuration into a dictionary
    config = load_config(CONFIG_PATH)

    URL, SCORE, STRATEGY, SILENT = config.values()

    # Define the function that drive to LES and access in
    def startDrive(mode:int=STRATEGY, headless:bool=SILENT):
        """
        Initializes a ChromeDriver instance with optional page loading strategies.

        Args:
            mode (int, optional): Controls the page loading strategy. Defaults to 0 (normal strategy).

                - 0 (normal): Performs full page load with all content.
                - 1 (eagle): A potential strategy for faster page loading (details may vary depending on ChromeDriver version).

        Returns:
            webdriver.Chrome: A newly created ChromeDriver instance.

        Raises:
            ValueError: If an invalid mode is provided.
        """
        option = Options()
        option.page_load_strategy = ['normal', 'eager'][mode]
        if headless: option.add_argument('--headless=new')
        return webdriver.Chrome(options=option)
    def get_user_choice():
        """Prompts the user for a choice and returns their input."""
        while True:
            choice = input("Error encountered. Try again (y/n)? ").lower()
            if choice in ("y", "n"):
                return choice
            else:
                print("Invalid input. Please enter 'y' or 'n'.")
    def access_website(driver:webdriver, url:str=URL, max_attempts:int=3):
        """Attempts to access the website with retries and user interaction."""
        attempt_count = 0
        while attempt_count < max_attempts:
            try:
                driver.get(url)
                return 1 # Success, exit the loop
            except TimeoutException as ex:
                print("Error: Timeout! The website may be unreachable.")

            # User interaction for retry or quit
            choice = get_user_choice()
            if choice == 'n':
                driver.close()
                return 0 # Indicate failure to user
            else:
                attempt_count += 1
                time.sleep(5)  # Introduce a delay between retries

        # All attempts failed
        driver.close()
        print("Failed to access the website after", max_attempts, "attempts.")
        return None # Indicate overall failure
    
    # Start drive
    Driver = startDrive()
    
    # Define function fot evaluation system
    def login():
        name = input("Enter username: ")
        pswd = getpass.getpass("Enter password: ")

        name_in = Driver.find_element(By.ID, 'userNameInput')
        pswd_in = Driver.find_element(By.ID, 'passwordInput')

        name_in.clear()
        name_in.send_keys(name)
        pswd_in.clear()
        pswd_in.send_keys(pswd)

        Driver.find_element(By.ID, "submitButton").click()
        return Driver.title != 'Sign In'
    def take_login_attempts(num_attempts):
        """
        Function to handle login attempts with a specified number of tries.

        Parameters:
            num_attempts (int): Number of login attempts allowed.

        Returns:
            None

        Notes:
            This function repeatedly calls the 'login' function until either
            the login is successful or the number of attempts is exhausted.
            It prints the remaining attempts after each failed attempt. If
            all attempts are exhausted, it prints a message and closes the driver.

        Example:
            take_login_attempts(3)  # Allow 3 login attempts
        """            
        while num_attempts > 0:
            print(f"\nYou have {num_attempts} attempts left.")
            if login():
                return  # Exit function if login successful
            num_attempts -= 1
        print("You have exhausted all attempts. Exiting...")
        Driver.close()
    def getfullInfo():
        name = Driver.find_element(By.CSS_SELECTOR, "li.nav-item").text
        total, evaluated, yet = [int(data.text) for data in Driver.find_elements(By.CSS_SELECTOR, "h2")]
        disabled = Driver.find_elements(By.CSS_SELECTOR, "a.disabled").__len__()

        term = Driver.find_element(By.CSS_SELECTOR, 'form > div > select[name = term] > option[selected]').text
        year = Driver.find_element(By.CSS_SELECTOR, 'form > div > input[name = year]').get_attribute('value')

        print("="*10)
        print("Welcome,", name, ' !\n')
        print(f"Semester: {term}/{year}")
        print('Evaluated:', f"{evaluated/(total-disabled):.2%}")
        print(f"Remain: {yet-disabled}/{total}")
        print("="*10)

        return (name, yet-disabled, total)

    def confirm_default_input(default, prompt, confirm_prompt='Do you want to use the default value ({})? (yes/no): ', invalid_prompt='Invalid input. Please enter "yes" or "no".'):
        while True:
            confirmation = input(confirm_prompt.format(default)).lower()
            if confirmation == '': return default
            if confirmation in ['yes', 'no']:
                if confirmation == 'yes':
                    return default
                else:
                    while True:
                        user_input = input(prompt)
                        try:
                            score = int(user_input)
                            if 0 <= score <= 4:
                                return score
                            else:
                                print("Invalid score. Score must be an integer between 0 and 4.")
                        except ValueError:
                            print("Invalid input. Please enter an integer.")
    def starter():
        start = Driver.find_element(By.CSS_SELECTOR, "div.gap-3.gap-lg-0 > div > div > div > a")
        Driver.execute_script('arguments[0].click()', start)
    def eval(score:int=SCORE):
        score += 1
        pos = [
            f".bg-white:nth-child(2) .form-check:nth-child({score}) > .btn",
            f".bg-white:nth-child(3) > .my-4:nth-child(4) .form-check:nth-child({score}) > .btn",
            f".bg-white:nth-child(3) > .my-4:nth-child(7) .form-check:nth-child({score}) > .btn",
            f".bg-white:nth-child(3) > .my-4:nth-child(10) .form-check:nth-child({score}) > .btn",
            f".bg-white:nth-child(4) .form-check:nth-child({score}) > .btn",
            f".bg-white:nth-child(5) > .my-4:nth-child(4) .form-check:nth-child({score}) > .btn",
            f".bg-white:nth-child(5) > .my-4:nth-child(7) .form-check:nth-child({score}) > .btn",
            f".bg-white:nth-child(5) > .my-4:nth-child(10) .form-check:nth-child({score}) > .btn",
            f"#eva > form > div.d-flex.justify-content-center > button"
        ]

        for x in pos:
            item = Driver.find_element(By.CSS_SELECTOR, x)
            Driver.execute_script('arguments[0].click()', item)

    # Check for accessable
    if not access_website(Driver, URL):
        print("Exiting program due to website access failure.")
        Driver.close()
    else:
        # Go to login and def the function for it
        Driver.find_element(By.CSS_SELECTOR, 'a.btn').click()
        
        # Try to sign in 
        take_login_attempts(3)

        # Set the times loop to take evaluations
        print()
        remain = getfullInfo()[1]
        print()

        while remain >= 0:
            score = confirm_default_input(SCORE, "CAUTION: Please enter the score for ALL Lecturer (or leave blank to keep the default): ")
            for sheet in trange(remain):
                starter()
                eval(score)
                remain -= 1
        else:
            print("ALL LETURER WAS EVALUATED ✅")
            print("Thank you for using `PSU auto evaluated`")
            Driver.close()

if __name__ == '__main__':
    main()