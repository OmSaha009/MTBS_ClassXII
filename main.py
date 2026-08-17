import random
import mysql.connector
from mysql.connector import Error
from mysql.connector.cursor import MySQLCursor
from mysql.connector.connection import MySQLConnection

#Adjustable Parameters
show_times = ["09:00 AM", "11:30 AM", "02:00 PM", "04:30 PM", "07:00 PM", "09:30 PM"]
total_seats = 200


def init_db():

    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="omsaha123",
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS ticket_db")
            cursor.execute("USE ticket_db")

            cursor.execute("""CREATE TABLE IF NOT EXISTS MOVIE (
                MovieID INT AUTO_INCREMENT PRIMARY KEY,
                MovieName VARCHAR(50) NOT NULL,
                Genre VARCHAR(20),
                Duration INT COMMENT 'in minutes',
                TicketPrice FLOAT NOT NULL
            );""")

            cursor.execute("""CREATE TABLE IF NOT EXISTS `SHOW` (
                ShowID INT AUTO_INCREMENT PRIMARY KEY,
                MovieID INT,
                ShowTime VARCHAR(20),
                TotalSeats INT NOT NULL,
                AvailableSeats INT NOT NULL,
                FOREIGN KEY (MovieID) REFERENCES MOVIE(MovieID)
            );""")

            cursor.execute("""CREATE TABLE IF NOT EXISTS BOOKING (
                BookingID INT AUTO_INCREMENT PRIMARY KEY,
                CustomerName VARCHAR(50) NOT NULL,
                ShowID INT,
                NumTickets INT NOT NULL,
                TotalAmount FLOAT,
                Status VARCHAR(10) DEFAULT 'Booked',
                FOREIGN KEY (ShowID) REFERENCES `SHOW`(ShowID)
            );""")

            connection.commit()
            
            return connection, cursor
            
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")  
        return None, None

def show_table_struct(cursor: MySQLCursor):

    # Display tables after creation
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    
    print("\n📋 Tables in ticket_db:")
    print("-" * 40)
    for table in tables:
        print(f"  - {table[0]}")
    
    # For each table, show its structure
    for table in tables:
        table_name = table[0]
        print(f"\n📊 Table: {table_name}")
        print("=" * 80)
        
        # Get table structure with proper escaping for SHOW
        if table_name.lower() == 'show':
            cursor.execute(f"DESCRIBE `{table_name}`")
        else:
            cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        
        print(f"{'Field':<20} {'Type':<20} {'Null':<10} {'Key':<10} {'Default':<15} {'Extra':<15}")
        print("-" * 90)
        for col in columns:
            print(f"{col[0]:<20} {col[1]:<20} {col[2]:<10} {col[3]:<10} {str(col[4]):<15} {col[5]:<15}")
        
        # Get row count with proper escaping for SHOW
        try:
            if table_name.lower() == 'show':
                cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
            else:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"\nTotal rows: {count}")
        except:
            pass

def add_sample_data(connection: MySQLConnection, cursor: MySQLCursor):
    """Add 50 sample movies with multiple genres and shows (prices in rupees)"""
    try:
        # Sample movie data with multiple genres (prices in rupees)
        movies = [
            # Action Movies
            ("The Dark Knight", "Action", 152, 350.00),
            ("Mad Max: Fury Road", "Action", 120, 320.00),
            ("The Matrix", "Action", 136, 350.00),
            
            # Sci-Fi Movies
            ("Inception", "Sci-Fi", 148, 400.00),
            ("Interstellar", "Sci-Fi", 169, 450.00),
            ("The Martian", "Sci-Fi", 144, 350.00),
            
            # Drama Movies
            ("The Godfather", "Drama", 175, 320.00),
            ("The Shawshank Redemption", "Drama", 142, 350.00),
            ("Forrest Gump", "Drama", 142, 320.00),
            
            # Comedy Movies
            ("The Hangover", "Comedy", 100, 280.00),
            ("Bridesmaids", "Comedy", 125, 300.00),
            ("Superbad", "Comedy", 113, 280.00),
            
            # Horror Movies
            ("The Conjuring", "Horror", 112, 300.00),
            ("Get Out", "Horror", 104, 320.00),
            ("A Quiet Place", "Horror", 90, 300.00),
        ]

        #Adding movies to database
        for movie in movies:
            cursor.execute("""INSERT INTO MOVIE (MovieName, Genre, Duration, TicketPrice) VALUES (%s, %s, %s, %s)""", (movie[0], movie[1], movie[2], movie[3]))

        connection.commit()
        print("Added Sample Data")
        
    except Error as e:
        print(f"Operation Failed. Error: {e}")
        

def add_shows(movie_id: int, cursor: MySQLCursor, connection: MySQLConnection):
    show_num = random.randint(2,5)
    selected_times = random.sample(show_times, show_num)
    show_count = 0
    for show_time in selected_times:
        available_seats = total_seats
        cursor.execute("INSERT INTO `SHOW` (MovieID, ShowTime, TotalSeats, AvailableSeats) VALUES (%s, %s, %s, %s)", (movie_id, show_time, total_seats, available_seats))
        show_count+=1

    connection.commit()
    print(f'Added {show_count} shows')


if __name__ == "__main__":

    print('==============MOVIE TICKET BOOKING SYSTEM==============')
    print('')
    print('1. Add a movie')
    print('2. Search movies')
    print('3. Display shows for a movie')
    print('4. Book a ticket ')
    print('5. Search a booking')
    print('6. Cancel a ticket')
    print('7. Display all booking details')
    print('8. Display show-wise revenue ')
    print('9. Exit')

    print('')
    
    connection, cursor = init_db()

    if connection is None or cursor is None:
        print("Failed to connect. Exiting...")
        exit()

    #Uncomment the following lines only when hardcoded sample data(movies) needs to be added

    # add_sample_data(connection, cursor)

    # cursor.execute("SELECT COUNT(*) FROM MOVIE")
    # rows = cursor.fetchone()[0]
    # print("Number of movies in database: ", rows)

    while True:

        choice = int(input("> Enter your choice: "))
        print('')

        match choice:
            case 1:
                
                print('ADD A MOVIE:')
                print('')
                movie_name = input("Movie name: ")
                movie_genre = input("Genre: ")
                movie_duration = int(input("Movie Duration (in mins):"))
                movie_ticket_price = float(input("Ticket Price: "))

                try:
                    cursor.execute("""
                        INSERT INTO MOVIE (MovieName, Genre, Duration, TicketPrice)
                        VALUES (%s, %s, %s, %s)
                    """, (movie_name, movie_genre, movie_duration, movie_ticket_price))

                    movie_id = cursor.lastrowid
                    connection.commit()

                    #Adding random(2-5) shows for the added movie
                    print("")
                    print("Movie created with ID: ", movie_id)
                    add_shows(movie_id, cursor, connection)

                except Error as e:
                    print(f"Operation Failed. Error: {e}")
                    connection.rollback()

                print('')

            case 2:
                print('SEARCH A MOVIE (by genre or name):')
                print('')

                search_term = input("Enter Genre/Movie name to search: ")

                try:

                    cursor.execute("""
                        SELECT * FROM MOVIE
                        WHERE MovieName LIKE %s OR Genre LIKE %s
                    """, (f"%{search_term}%", f"%{search_term}%"))

                    search_results = cursor.fetchall()

                    if search_results:
                        print('')
                        print('Search Results: ')
                        print('')
                        for movie in search_results:
                            print(f'ID: {movie[0]}, Name: {movie[1]}, Genre: {movie[2]}, Duration: {movie[3]} mins, Price: {movie[4]}')

                except Error as e:
                    print(f"Operation Failed. Error: {e}")
                    connection.rollback()

                print('') 

            case 3:
                cursor.execute("SELECT MovieID, MovieName FROM MOVIE")
                movies = cursor.fetchall()

                if not movies:
                    print("No movies found.")
                else:
                    print("Available Movies:")
                    print("")
                    for movie in movies:
                        print(f"ID: {movie[0]}, Name: {movie[1]}")

                print("")
                movie_id = int(input("Enter Movie ID to display shows for: "))
                cursor.execute("""
                    SELECT s.ShowID, m.MovieName, s.ShowTime, s.TotalSeats, s.AvailableSeats
                    FROM `SHOW` s
                    JOIN MOVIE m ON s.MovieID = m.MovieID
                    WHERE s.MovieID = %s
                    ORDER BY s.ShowTime
                """, (movie_id,))
                
                shows = cursor.fetchall()
                
                if shows:
                    print("")
                    print(f"Shows for '{shows[0][1]}':")
                    print("=" * 90)
                    print(f"{'Show ID':<10} {'Movie Name':<20} {'Show Time':<20} {'Total Seats':<15} {'Available':<15}")
                    print("-" * 90)
                    for show in shows:
                        print(f"{show[0]:<10} {show[1]:<20} {show[2]:<20} {show[3]:<15} {show[4]:<15}")
                    print("=" * 90)
                    
                    # Show summary
                    total_seats = sum(show[3] for show in shows)
                    total_available = sum(show[4] for show in shows)
                    total_booked = total_seats - total_available

                    print("")
                    print(f"Summary for '{shows[0][1]}':")
                    print(f"  Total Shows: {len(shows)}")
                    print(f"  Total Seats: {total_seats}")
                    print(f"  Booked Seats: {total_booked}")
                    print(f"  Available Seats: {total_available}")
                    print("")
                    
                else:
                    print("")
                    print(f"No shows found for Movie ID: {movie_id}")
                    print("   Please add shows for this movie first.")
                    print("")
                    
            case 4:
                print("")
                print("Shows available for booking: ")
                print("")

                cursor.execute("""
                    SELECT s.ShowID, m.MovieName, s.ShowTime, s.TotalSeats, s.AvailableSeats, m.TicketPrice
                    FROM `SHOW` s
                    JOIN MOVIE m ON s.MovieID = m.MovieID
                """)

                shows = cursor.fetchall()

                print("=" * 99)
                print(f"{'Show ID':<10} {'Movie Name':<20} {'Show Time':<20} {'Total Seats':<15} {'Available Seats':<15} {'Ticket Price':<15}")
                print("-" * 99)
                for show in shows:
                    print(f"{show[0]:<10} {show[1]:<20} {show[2]:<20} {show[3]:<15} {show[4]:<15} {show[5]:<15}")
                print("=" * 99)
                print("")

                show_id = int(input("Enter Show ID to book in: "))
                print("")

                show_booking = None
                for show in shows:
                    if show[0] == show_id:
                        show_booking = show

                print("Booking a ticket for: ")
                print("  Show ID: ", show_booking[0])
                print("  Movie Name: ", show_booking[1])
                print("  Show Time: ", show_booking[2])
                print("")
                consent = input("Are you sure? (y/n): ")
                print("")

                if consent == "y":

                    seat_num = int(input("Enter number of seats to book: "))
                    print("")
                    if seat_num > show_booking[4]:
                        print(f"{seat_num} exceeds the number of available seats.")
                        print("Returning to Menu. \n")

                    customer_name = input("Enter customer name: ")
                    print("")
                    total_amount = seat_num * show_booking[5]
                    print("Total amount to be paid: ", total_amount)
                    print("\nBooking tickets... \n")

                    try:

                        cursor.execute("INSERT INTO BOOKING (CustomerName, ShowID, NumTickets, TotalAmount) VALUES (%s, %s, %s, %s)", (customer_name, show_booking[0], seat_num, total_amount))

                        print(f"Booking done with Booking ID: {cursor.lastrowid}\n")

                        cursor.execute("UPDATE `SHOW` SET AvailableSeats = AvailableSeats - %s WHERE ShowID = %s AND AvailableSeats >= %s", (seat_num, show_booking[0], seat_num))

                        connection.commit()
                    except Error as e:
                        connection.rollback()
                        print(f"Operation Failed. Error: {e}\n")
                    
                elif consent == "n":
                    print("Returning to Menu. \n")
                else:
                    print("Invalid Choice, please type 'y' or 'n'. \n")

            case 5:

                customer_name = input("Enter customer name: ")
                print(f"\nBookings by {customer_name}: \n")
                cursor.execute("""
                    SELECT b.BookingID, b.ShowID, b.NumTickets, b.TotalAmount, m.MovieID, m.MovieName, s.ShowTime
                    FROM BOOKING b
                    JOIN `SHOW` s ON b.ShowID = s.ShowID
                    JOIN MOVIE m ON s.MovieID = m.MovieID
                    WHERE b.CustomerName = %s AND b.Status = 'Booked'
                """, (customer_name,))
                bookings = cursor.fetchall()
                print(f"{'Booking ID':<10} {'Movie':<15} {'Show Time':<15} {'Seats':<10} {'Ticket Price':<15}")
                print("-" * 65)
                for booking in bookings:
                    print(f"{booking[0]:<10} {booking[5]:<15} {booking[6]:<15} {booking[2]:<10} {booking[3]:<15}")
                print("=" * 65)
                print("")

            case 6:

                booking_id = int(input("Enter Booking ID: "))
                print("\nBooking Details: \n")

                cursor.execute("""SELECT b.CustomerName, b.ShowID, b.NumTickets, b.TotalAmount, m.MovieName
                FROM BOOKING b
                JOIN `SHOW` s ON s.ShowID = b.ShowID
                JOIN MOVIE m ON m.MovieID = s.MovieID
                WHERE BookingID = %s""", (booking_id,))
                booking = cursor.fetchone()

                print(" Customer Name:", booking[0])
                print(" Booking ID:", booking_id)
                print(" Show ID:", booking[1])
                print(" Movie Name:", booking[4])
                print(" Number of Seats:", booking[2])
                print(" Total Amount:", booking[3], "\n")
                consent = input("Are you sure you want to cancel this booking? (y/n): ")
                print("")
                if consent == "y":
                    cursor.execute("UPDATE BOOKING SET Status = 'Cancelled' WHERE BookingID = %s", (booking_id,))
                    cursor.execute("UPDATE `SHOW` SET AvailableSeats = AvailableSeats + %s WHERE ShowID = %s", (booking[2], booking[1]))
                    connection.commit()
                    print("Booking cancelled successfully. \n")
                elif consent == "n":
                    print("Returning to Menu. \n")
                else:
                    print("Invalid Choice, please type 'y' or 'n'. \n")

            case 7:
                    cursor.execute("""
                        SELECT b.BookingID, b.CustomerName, m.MovieName, s.ShowTime, 
                            b.NumTickets, b.TotalAmount, b.Status
                        FROM BOOKING b
                        JOIN `SHOW` s ON b.ShowID = s.ShowID
                        JOIN MOVIE m ON s.MovieID = m.MovieID
                        ORDER BY b.BookingID DESC
                    """)
                    
                    all_bookings = cursor.fetchall()
                    
                    if all_bookings:
                        print("All Bookings (Including Cancelled): \n")
                        print("=" * 110)
                        print(f"{'ID':<6} {'Customer':<20} {'Movie':<30} {'Time':<15} {'Tickets':<10} {'Amount':<12} {'Status':<10}")
                        print("-" * 110)
                        for booking in all_bookings:
                            print(f"{booking[0]:<6} {booking[1]:<20} {booking[2]:<30} "
                                f"{booking[3]:<15} {booking[4]:<10} ₹{booking[5]:<11.2f} {booking[6]:<10}")
                        print("=" * 110)
                        
                        # Summary
                        total = len(all_bookings)
                        active = sum(1 for b in all_bookings if b[6] == 'Booked')
                        cancelled = total - active
                        print(f"\nTotal: {total} | Active: {active} | Cancelled: {cancelled}")
                    else:
                        print("No bookings found.")
                    print("")

            case 8:

                print('Show-wise Revenue Report: \n')
                print('=' * 93)
                
                try:
                    cursor.execute("""
                        SELECT 
                            s.ShowID,
                            m.MovieName,
                            s.ShowTime,
                            COUNT(b.BookingID) AS TotalBookings,
                            SUM(b.NumTickets) AS TotalTicketsSold,
                            SUM(b.TotalAmount) AS TotalRevenue
                        FROM `SHOW` s
                        JOIN MOVIE m ON s.MovieID = m.MovieID
                        LEFT JOIN BOOKING b ON s.ShowID = b.ShowID AND b.Status = 'Booked'
                        GROUP BY s.ShowID, m.MovieName, s.ShowTime
                        ORDER BY TotalRevenue DESC
                    """)
                    
                    results = cursor.fetchall()
                    
                    if not results:
                        print("No revenue data available.")
                    
                    # Display header
                    print(f"{'Show ID':<10} {'Movie':<30} {'Time':<15} {'Bookings':<12} {'Tickets':<12} {'Revenue':<12}")
                    print("-" * 93)
                    
                    # Display each row
                    total_revenue = 0
                    total_bookings = 0
                    total_tickets = 0
                    
                    for row in results:
                        show_id, movie_name, show_time, bookings, tickets, revenue = row
                        bookings = bookings or 0
                        tickets = tickets or 0
                        revenue = revenue or 0.0
                        
                        total_bookings += bookings
                        total_tickets += tickets
                        total_revenue += revenue
                        
                        print(f"{show_id:<10} {movie_name[:28]:<30} {show_time:<15} "
                            f"{bookings:<12} {tickets:<12} ₹{revenue:<11.2f}")
                    
                    # Display totals
                    print("-" * 93)
                    print(f"{'TOTALS':<57} {total_bookings:<12} {total_tickets:<12} ₹{total_revenue:<11.2f}")
                    print("=" * 93)

                    print("")
                    
                except Error as e:
                    print(f"Error generating revenue report: {e}\n")

            case 9:
                print('Exiting...')
                break

            case _:
                print("Invalid choice. Please choose from 1 to 9 according to the menu")
