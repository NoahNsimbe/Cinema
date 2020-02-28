import re
import pandas as pd
import tabulate as table

total_sales = 0
total_tickets_sold = 0
seat_columns = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
seat_rows = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P"]
seats = pd.DataFrame()
seat_prices = pd.Series([])


def start_app():

    global seats
    global total_tickets_sold
    global total_sales

    seats = pd.DataFrame("*", seat_rows, seat_columns)

    read_prices()
    print_seating_chart()

    while True:

        option_selected = display_menu()

        # Movie schedule
        if option_selected == "1":
            schedule_movie()

        # Seat Assignment
        elif option_selected == "2":
            assign_seat()
            print_seating_chart()

        # Payments (for reserved seat)
        elif option_selected == "3":
            change_reserved_seats()

        # Reset Seating Plan
        elif option_selected == "4":
            reset_seating_plan()
            print_seating_chart()

        # Exit
        else:
            print("\n\t\t\tBye Bye \n")
            break

    return


# Movie Schedule
def schedule_movie():

    addition = input(
        f"Add a movie (Title, Genre, Rating, Release_date, Running_time, Showing Date and Time). "
        f"Enter * to cancel : ")

    if addition == "*":
        return

    with open('movies.txt', 'a') as movies_file:
        movies_file.write("\n{}".format(addition))

    df = pd.read_csv('movies.txt', sep=',', header=0)
    print(df)


# Reset seating plan
def reset_seating_plan():

    global total_tickets_sold
    global total_sales
    global seats
    global seat_rows
    global seat_columns

    confirmation = confirm_action()

    if confirmation:
        seats = pd.DataFrame("*", seat_rows, seat_columns)
        total_tickets_sold = 0
        total_sales = 0

    return


# Change reserved seats to available
def change_reserved_seats():
    global seats
    print("\n")
    if confirm_action():
        count = 0
        for row, columns in seats.iterrows():
            for index in range(1, columns.count() + 1):
                if seats.loc[row, index] == "o":
                    count += 1
                    print("{}{}".format(row, index))
                    seats.loc[row, index] = "*"

        if count > 0:
            print("\nThe above seats are now available")
            print_seating_chart()
        else:
            print("\nNo seats are yet reserved")
    return


# Confirm actions
def confirm_action():
    accepted_responses = {'y', 'n'}
    response = (input("Are you sure you want to perform this action (y/n) : ")).lower()

    while True:
        if response not in accepted_responses:
            print("Invalid Value")
            response = input("Type 'y' for yes and 'n' for no : ")
        else:
            break

    if response == 'y':
        return True
    else:
        return False


# Assign seats
def assign_seat():

    global seats

    twin_seats_columns = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    twin_seats_rows = ['A', 'B']

    very_vip_seats1 = seats.loc[['A', 'B'], [1, 2, 3, 4, 16, 17, 18, 19, 20]]
    very_vip_seats2 = seats.loc[['C', 'D', 'E', 'F'], seat_columns]

    twin_seats = seats.loc[twin_seats_rows, twin_seats_columns]
    very_vip_seats = pd.concat([very_vip_seats1, very_vip_seats2])
    vip_seats = seats.loc[['G', 'H', 'I', 'J', 'K', 'L'], seat_columns]
    economy_seats = seats.loc[['M', 'N', 'O', 'P'], seat_columns]

    def select_option(category):
        acceptable_row_values = list(category.index.values)
        acceptable_column_values = list(category.columns.values)

        acceptable_twin_column_values = list()

        global total_tickets_sold
        global total_sales
        global seat_prices
        nonlocal no_of_seats

        seats_available = 0
        twin_seat = False

        print("Available seats : ")

        for each_row in acceptable_row_values:
            for each_column in acceptable_column_values:
                if category.loc[each_row, each_column] == "*":

                    seats_available += 1
                    if each_row in twin_seats_rows and each_column in twin_seats_columns:

                        twin_seat = True

                        if each_column == 15:
                            if each_row != "B":
                                second_seat_row = "B"
                                acceptable_twin_column_values.append(each_column)
                                print(
                                    f"{each_row}{each_column}:{second_seat_row}{each_column} , {seat_prices['TwinSeats']} ")
                        else:
                            if each_column % 2 == 1:
                                second_seat_col = each_column + 1
                                acceptable_twin_column_values.append(each_column)

                                print(
                                    f"{each_row}{each_column}:{each_row}{second_seat_col} , {seat_prices['TwinSeats']} ")

                    else:
                        print("{}{} , {}".format(each_row, each_column, seat_prices[each_row]))

        if seats_available < 1:
            print("Sorry, no seat is available for this category")
            return

        if seats_available < no_of_seats:
            no_of_seats = int(seats_available)

        input_row_value = ""
        input_column_value = 0
        seat_array = list()

        if twin_seat:
            acceptable_column_values = acceptable_twin_column_values

        if no_of_seats > 1:
            request = "Choose seats separated by commas (Enter * to cancel operation) : "
        else:
            request = "Choose seat (Enter * to cancel operation) : "

        response = input(request)

        while True:
            operation_valid = False

            def validate_input(ans):

                nonlocal input_column_value
                nonlocal input_row_value
                nonlocal acceptable_column_values
                nonlocal acceptable_row_values

                ans_array = re.split(r'(\d+)', ans)

                if len(ans_array) > 1:
                    input_row_value = str(ans_array[0]).upper()
                    input_column_value = int(ans_array[1])

                if input_column_value not in acceptable_column_values:
                    print("Invalid column value")
                    return False

                elif input_row_value not in acceptable_row_values:
                    print("Invalid row value")
                    return False

                else:
                    return True

            if response == "*":
                break

            if no_of_seats > 1:
                if "," in response:

                    response = response.split(",")

                    if len(response) == no_of_seats:

                        for each_seat in response:
                            each_seat = each_seat.strip()
                            operation_valid = validate_input(each_seat)
                            if not operation_valid:
                                print("Seat {} is invalid".format(each_seat))
                                seat_array.clear()
                                break
                            seat_array.append(each_seat)

                        if operation_valid:
                            break
                        else:
                            response = input("Please try again : ")
                    else:
                        response = input("You did not enter all the {} seats. Please try again : ".format(no_of_seats))

                else:
                    response = input("Please try again while separating the seats using commas : ")

            else:
                operation_valid = validate_input(response)
                if operation_valid:
                    break
                else:
                    response = (input("Please try again : ")).strip()

        if operation_valid:

            print("\t ======= Available actions ========")
            print("\t 1 . Mark as paid")
            print("\t 2 . Mark as booked")
            print("\t 3 . Mark as available")
            print("\t 4 . Cancel")
            print("\t ==================================")

            while True:
                action = input("Select action : ")

                if action == '1':

                    if no_of_seats > 1:
                        for each_value in seat_array:

                            values = re.split(r'(\d+)', each_value)
                            input_row_value = str(values[0]).upper()
                            input_column_value = int(values[1])

                            if twin_seat:
                                assign_twin_seat(input_row_value, input_column_value, "#")
                                total_tickets_sold += 2
                                total_sales += int(seat_prices["TwinSeats"])

                            else:

                                seats.loc[input_row_value, input_column_value] = "#"
                                total_tickets_sold += 1
                                total_sales += int(seat_prices[input_row_value])

                    else:
                        if twin_seat:
                            assign_twin_seat(input_row_value, input_column_value, "#")
                            total_tickets_sold += 2
                            total_sales += int(seat_prices["TwinSeats"])
                        else:
                            seats.loc[input_row_value, input_column_value] = "#"
                            total_tickets_sold += 1
                            total_sales += int(seat_prices[input_row_value])

                    break

                elif action == '2':

                    if no_of_seats > 1:
                        for each_value in seat_array:
                            values = re.split(r'(\d+)', each_value)
                            input_row_value = str(values[0]).upper()
                            input_column_value = int(values[1])

                            if twin_seat:
                                assign_twin_seat(input_row_value, input_column_value, "o")
                            else:
                                seats.loc[input_row_value, input_column_value] = "o"

                    else:
                        if twin_seat:
                            assign_twin_seat(input_row_value, input_column_value, "o")
                        else:
                            seats.loc[input_row_value, input_column_value] = "o"

                    break

                elif action == '3':

                    if no_of_seats > 1:
                        for each_value in seat_array:
                            values = re.split(r'(\d+)', each_value)
                            input_row_value = str(values[0]).upper()
                            input_column_value = int(values[1])

                            if twin_seat:
                                assign_twin_seat(input_row_value, input_column_value, "*")
                                total_tickets_sold -= 2
                                total_sales -= int(seat_prices["TwinSeats"])
                            else:

                                seats.loc[input_row_value, input_column_value] = "*"
                                total_tickets_sold -= 1
                                total_sales -= int(seat_prices[input_row_value])

                    else:
                        if twin_seat:
                            assign_twin_seat(input_row_value, input_column_value, "*")
                            total_tickets_sold -= 2
                            total_sales -= int(seat_prices["TwinSeats"])
                        else:
                            seats.loc[input_row_value, input_column_value] = "*"
                            total_tickets_sold -= 1
                            total_sales -= int(seat_prices[input_row_value])

                    break

                elif action == '4':
                    break

                else:
                    print("Invalid response")

        return

    while True:
        try:
            no_of_seats = int(input("Enter number of seats required : "))
            if no_of_seats < 1:
                no_of_seats = int(input("Enter number of seats required as a counting number: "))
            break
        except ValueError:
            print("Please enter a number")

    print("\t ========= Seat Categories =========")
    print("\t 1 . Twin Seats")
    print("\t 2 . Very VIP")
    print("\t 3 . VIP")
    print("\t 4 . Economy")
    print("\t 5 . Cancel operation")
    print("\t ==================================")

    while True:
        desired_category = input("Desired seat category : ")
        acceptable_categories = {'1', '2', '3', '4', '5'}

        if desired_category not in acceptable_categories:
            print("Choose any of the numbers 1, 2, 3, 4 or 5")
        else:
            break

    if desired_category == '1':
        select_option(twin_seats)

    elif desired_category == '2':
        select_option(very_vip_seats)

    elif desired_category == '3':
        select_option(vip_seats)

    elif desired_category == '4':
        select_option(economy_seats)

    else:
        return

    return


# Assign twin seats
def assign_twin_seat(row_value, column_value, value):

    global seats

    if column_value == 15:
        if row_value != "B":

            twin_row_value = "B"

            seats.loc[row_value, column_value] = value
            seats.loc[twin_row_value, column_value] = value

    else:
        if int(column_value) % 2 == 1:
            twin_column_value = column_value + 1

            seats.loc[row_value, column_value] = value
            seats.loc[row_value, twin_column_value] = value


# Display seats
def print_seating_chart():
    global seat_columns
    global seats
    global total_sales
    global total_tickets_sold

    table_format = 'grid'

    table_headers = seat_columns
    available_seats, taken_seats, reserved_seats = count_seats()

    print("\n")
    print(table.tabulate(seats, table_headers, table_format))
    print("\n")
    print("Number of seats available : {}".format(available_seats))
    print("Number of seats taken : {}".format(taken_seats))
    print("Total Tickets sold : {}".format(total_tickets_sold))
    print("Number of seats booked : {}".format(reserved_seats))
    print("Total Sales : Shs {}".format(total_sales))


# Count number of available, booked and paid seats
def count_seats():
    global seats
    available = 0
    paid = 0
    booked = 0

    for row, columns in seats.iterrows():
        for value in columns:
            if value == "*":
                available += 1
            if value == "#":
                paid += 1
            if value == "o":
                booked += 1

    return available, paid, booked


# display main menu
def display_menu():

    accepted_responses = {'1', '2', '3', '4', '5'}

    print("\n")
    print("\t\t\t <<<<<<<< Cinemax Theatre >>>>>>>>>")
    print("\t\t\t ============== Menu ==============")
    print("\n")
    print("\t\t\t 1 . Movie schedule")
    print("\t\t\t 2 . Seat Assignment")
    print("\t\t\t 3 . Payments (for reserved seat)")
    print("\t\t\t 4 . Reset Seating Plan")
    print("\t\t\t 5 . Exit")
    print("\n")
    print("\t\t\t ==================================")
    print("\n")

    response = input("Enter the number corresponding with the action you want : ")

    while True:
        if response not in accepted_responses:
            print("Invalid Value")
            response = input("Enter the number corresponding with the action you want : ")
        else:
            break

    return response


# Read ticket prices
def read_prices():

    global seat_prices

    txt_file = pd.read_csv('prices', sep=" ", header=None)
    rows = []
    price = []
    for row, amount in txt_file.values:
        rows.append(row)
        price.append(amount)

    seat_prices = pd.Series(data=price, index=rows)


if __name__ == '__main__':
    start_app()

