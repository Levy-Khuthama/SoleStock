
# ========The beginning of the class==========

class Shoe:

    def __init__(self, country, code, product, cost, quantity):
        '''
        In this function, you must initialise the following attributes:
            ● country,
            ● code,
            ● product,
            ● cost, and
            ● quantity.
        '''
        self.country = country
        self.code = code
        self.product = product
        self.cost = cost
        self.quantity = quantity

    def get_cost(self):
        '''
        Add the code to return the cost of the shoe in this method.
        '''
        return self.cost

    def get_quantity(self):
        '''
        Add the code to return the quantity of the shoes.
        '''
        return self.quantity

    def __str__(self):
        '''
        Add a code to returns a string representation of a class.
        '''
        return f"Country: {self.country}| Code: {self.code}| Product: {self.product}| Cost: {self.cost}| Quantity: {self.quantity}"


# =============Shoe list===========
'''
The list will be used to store a list of objects of shoes.
'''
shoe_list = []


# ==========Functions outside the class==============
def read_shoes_data():
    '''
    This function will open the file inventory.txt
    and read the data from this file, then create a shoes object with this data
    and append this object into the shoes list. One line in this file represents
    data to create one object of shoes. You must use the try-except in this function
    for error handling. Remember to skip the first line using your code.
    '''
    try:
        # open inventory file and read data
        with open('inventory.txt', 'r') as f:
            next(f)  # Skip the first line
            for line in f:
                data = line.strip().split(',')  # Split the line into components
                if len(data) == 5:  # Ensure there are exactly 5 components
                    country, code, product, cost, quantity = data
                    shoe = Shoe(country, code, product, float(cost),
                                int(quantity))  # Create a Shoe object
                    # Append the Shoe object to the shoe_list
                    shoe_list.append(shoe)
                    # Print the loaded shoe for confirmation
                    print(f"Loaded shoe: {shoe}")
                else:
                    # Handle lines that do not have exactly 5 components
                    print(
                        f"Warning: Skipping line due to incorrect format: {line.strip()}")
    except FileNotFoundError:
        # Handle the case where the file does not exist
        print("Error: File not found.")
    except Exception as e:
        print(f"Error: {e}")  # Handle any other exceptions that may occur


def capture_shoes():
    '''
    This function will allow a user to capture data
    about a shoe and use this data to create a shoe object
    and append this object inside the shoe list.
    '''
    # Get shoe details from user input
    country = input("Enter the country of the shoe: ")
    code = input("Enter the code of the shoe: ")
    product = input("Enter the product name: ")
    cost = float(input("Enter the cost of the shoe: "))
    quantity = int(input("Enter the quantity of the shoe: "))

    shoe = Shoe(country, code, product, cost, quantity)
    shoe_list.append(shoe)
    print(f"Captured shoe: {shoe}")  # Print the captured shoe for confirmation


def view_all():
    '''
    This function will iterate over the shoes list and
    print the details of the shoes returned from the __str__
    function. Optional: you can organise your data in a table format
    by using Python’s tabulate module.
    '''
    # Only display the tabular format, not the per-shoe string
    try:
        # Import the tabulate module to display data in a table format
        from tabulate import tabulate
        table = [[shoe.country, shoe.code, shoe.product, shoe.cost, shoe.quantity]
                 for shoe in shoe_list]  # Create a list of lists containing shoe details for tabulation
        headers = ["Country", "Code", "Product", "Cost",
                   "Quantity"]  # Define the headers for the table
        # Print the table using the tabulate function with a grid format
        print(tabulate(table, headers, tablefmt="grid"))
        print("=======================================================\n")
    except ImportError:
        # Handle the case where the tabulate module is not installed
        print(
            "Tabulate module not found. Please install it to view data in a table format.")


def re_stock():
    '''
    This function will find the shoe object with the lowest quantity,
    which is the shoes that need to be re-stocked. Ask the user if they
    want to add this quantity of shoes and then update it.
    This quantity should be updated on the file for this shoe.
    '''
    if not shoe_list:  # Check if the shoe_list is empty
        print("No shoes in inventory to restock.")
        return
    # Find the shoe with the lowest quantity using the min function and a lambda function as the key
    lowest_stock_shoe = min(shoe_list, key=lambda shoe: shoe.quantity)
    # Print the shoe with the lowest quantity
    print(f"The shoe with the lowest quantity is: {lowest_stock_shoe}")
    # Ask the user if they want to restock the shoe
    restock_decision = input(
        "Do you want to restock this shoe? (yes/no): ").strip().lower()
    if restock_decision == 'yes':  # If the user decides to restock
        try:
            # Get the additional quantity from user input
            additional_quantity = int(input("Enter the quantity to add: "))
            # Update the quantity of the shoe in the shoe_list
            lowest_stock_shoe.quantity += additional_quantity
            # Print the updated shoe details
            print(f"Updated shoe details: {lowest_stock_shoe}")
            # Update the inventory.txt file with the new quantity
            with open('inventory.txt', 'r') as f:
                lines = f.readlines()  # Read all lines from the inventory file
            with open('inventory.txt', 'w') as f:
                for line in lines:
                    # Check if the line corresponds to the shoe being restocked
                    if line.strip().split(',')[1] == lowest_stock_shoe.code:
                        # Write the updated shoe details to the file
                        f.write(
                            f"{lowest_stock_shoe.country},{lowest_stock_shoe.code},{lowest_stock_shoe.product},{lowest_stock_shoe.cost},{lowest_stock_shoe.quantity}\n")
                    else:
                        # Write the original line for other shoes
                        f.write(line)
        except ValueError:
            # Handle invalid input for quantity
            print("Invalid input for quantity. Please enter a valid number.")
    else:
        print("Restock cancelled.")  # If the user decides not to restock


def search_shoe():
    '''
     This function will search for a shoe from the list
     using the shoe code and return this object so that it will be printed.
    '''
    search_code = input(
        "Enter the shoe code to search: ")  # Get the shoe code to search from user input
    # Search for the shoe in the shoe_list using a generator expression and the next function
    found_shoe = next(
        (shoe for shoe in shoe_list if shoe.code == search_code), None)
    if found_shoe:  # If the shoe is found
        # Print the details of the found shoe
        print(f"Shoe found: {found_shoe}")
    else:
        print("Shoe not found.")  # If the shoe is not found in the inventory


def value_per_item():
    '''
    This function will calculate the total value for each item.
    Please keep the formula for value in mind: value = cost * quantity.
    Print this information on the console for all the shoes.
    '''
    for shoe in shoe_list:  # Iterate through each shoe in the shoe_list
        value = shoe.cost * shoe.quantity  # Calculate the total value for the shoe
        # Print the product name and its total value
        print(f"Product: {shoe.product} | Total Value: {value}")


def highest_qty():
    '''
    Write code to determine the product with the highest quantity and
    print this shoe as being for sale.
    '''
    if not shoe_list:  # Check if the shoe_list is empty
        print("No shoes in inventory to determine highest quantity.")
        return
    # Find the shoe with the highest quantity using the max function and a lambda function as the key
    highest_qty_shoe = max(shoe_list, key=lambda shoe: shoe.quantity)
    # Print the shoe with the highest quantity
    print(f"The shoe with the highest quantity is: {highest_qty_shoe}")
    # Print a message indicating that the product with the highest quantity is on sale
    print(f"{highest_qty_shoe.product} is now on sale!")


# ==========Main Menu=============
'''
Create a menu that executes each function above.
This menu should be inside the while loop. Be creative!
'''


def main_menu():
    while True:  # Start an infinite loop to display the menu until the user decides to exit
        # Print the menu header
        print("\n---------------Shoe Inventory Management System---------------")
        # Option to read shoe data from the inventory file
        print("1. Read shoe data from file")
        # Option to capture new shoe data from user input
        print("2. Capture new shoe data")
        print("3. View all shoes")  # Option to view all shoes in the inventory
        # Option to restock the shoe with the lowest quantity
        print("4. Restock shoe with lowest quantity")
        # Option to search for a shoe by its code
        print("5. Search for a shoe by code")
        # Option to calculate and display the total value for each item
        print("6. Calculate value per item")
        # Option to display the shoe with the highest quantity and indicate it is on sale
        print("7. Display shoe with highest quantity on sale")
        print("8. Exit")  # Option to exit the program

        # Get the user's choice from input
        choice = input("Enter your choice (1-8): ")

        if choice == '1':
            # Print a header for reading shoe data from the file
            print("--------------Reading Shoe Data from File--------------------:")
            read_shoes_data()  # Call the function to read shoe data from the file
            # Print a footer after reading shoe data from the file
            print("---------------Done reading shoe data from file------------------")
        elif choice == '2':
            # Print a header for capturing new shoe details
            print("--------------Capture New Shoe Details--------------------:")
            capture_shoes()  # Call the function to capture new shoe data from user input
            # Print a footer after capturing new shoe details
            print("---------------Done capturing new shoe details------------------")
        elif choice == '3':
            # Print a header for viewing all shoes
            print("--------------View All Shoes--------------------:")
            view_all()  # Call the function to view all shoes in the inventory
            # Print a footer after viewing all shoes
            print("---------------Done viewing all shoes------------------")
        elif choice == '4':
            # Print a header for restocking the shoe with the lowest quantity
            print("--------------Restock Shoe with Lowest Quantity--------------------:")
            re_stock()  # Call the function to restock the shoe with the lowest quantity
            # Print a footer after restocking the shoe
            print("---------------Done restocking shoe------------------")
        elif choice == '5':
            # Print a header for searching for a shoe by its code
            print("--------------Search for a Shoe by Code--------------------:")
            search_shoe()  # Call the function to search for a shoe by its code
            # Print a footer after searching for a shoe
            print("---------------Done searching for shoe------------------")
        elif choice == '6':
            # Print a header for calculating the total value for each item
            print("--------------Calculate Value per Item--------------------:")
            value_per_item()  # Call the function to calculate and display the total value for each item
            # Print a footer after calculating the total value for each item
            print("---------------Done calculating value per item------------------")
        elif choice == '7':
            # Print a header for displaying the shoe with the highest quantity and indicating it is on sale
            print(
                "--------------Display Shoe with Highest Quantity on Sale--------------------:")
            highest_qty()  # Call the function to display the shoe with the highest quantity and indicate it is on sale
            # Print a footer after displaying the shoe with the highest quantity
            print(
                "---------------Done displaying shoe with highest quantity------------------")
        elif choice == '8':
            # Print a goodbye message before exiting
            print("Exiting program. Goodbye!")
            break  # Exit the loop and end the program
        else:
            # Handle invalid menu choices
            print("Invalid choice. Please enter a number between 1 and 8.")
        # Print a separator after each menu action for better readability
        print("\n-------------------------------------------------------------")


# Call the main_menu function to start the program
if __name__ == "__main__":
    main_menu()
