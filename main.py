"""
Movie Ticket Booking System
---------------------------
A console-based Python + MySQL application to manage movies, shows,
ticket bookings, cancellations and show-wise revenue reports.
"""
import random
import mysql.connector
from mysql.connector import Error
from mysql.connector.cursor import MySQLCursor
from mysql.connector.connection import MySQLConnection
# Adjustable parameters
show_times = ["09:00 AM", "11:30 AM", "02:00 PM", "04:30 PM", "07:00 PM", "09:30 PM"]
total_seats = 200
MENU = [
    "1. Add a movie", "2. Search movies", "3. Display shows for a movie",
    "4. Book a ticket ", "5. Search a booking", "6. Cancel a ticket",
    "7. Display all booking details", "8. Display show-wise revenue ", "9. Exit",
]
def init_db():
    """Connect to MySQL, create the database and tables, return (connection, cursor)."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="pass78902",
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
            # SHOW is a reserved word in MySQL, so it is backtick-quoted everywhere
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
    # Reached if connection fails or is_connected() is False
    return None, None
def print_table(headers, widths, rows, length):
    """Print a left-aligned table with a header row and a dashed separator."""
    def format_row(row):
        return " ".join(f"{str(v):<{w}}" for v, w in zip(row, widths))
    print(format_row(headers))
    print("-" * length)
    for row in rows:
        print(format_row(row))
def add_shows(movie_id: int, cursor: MySQLCursor, connection: MySQLConnection):
    """Create 2-5 shows at random time slots for a movie."""
    selected_times = random.sample(show_times, random.randint(2, 5))
    for show_time in selected_times:
        cursor.execute(
            "INSERT INTO `SHOW` (MovieID, ShowTime, TotalSeats, AvailableSeats) VALUES (%s, %s, %s, %s)",
            (movie_id, show_time, total_seats, total_seats))
    connection.commit()
    print(f'Added {len(selected_times)} shows')
if __name__ == "__main__":
    print('==============MOVIE TICKET BOOKING SYSTEM==============\n')
    print("\n".join(MENU) + "\n")
    connection, cursor = init_db()
    if connection is None or cursor is None:
        print("Failed to connect. Exiting...")
        exit()
    while True:
        try:
            choice = int(input("> Enter your choice: "))
        except ValueError:
            print("❌ Please enter a valid number.\n")
            continue
        print('')
        match choice:
            case 1:
                print('ADD A MOVIE:\n')
                movie_name = input("Movie name: ")
                movie_genre = input("Genre: ")
                movie_duration = int(input("Movie Duration (in mins): "))
                movie_ticket_price = float(input("Ticket Price: "))
                try:
                    cursor.execute("""
                        INSERT INTO MOVIE (MovieName, Genre, Duration, TicketPrice)
                        VALUES (%s, %s, %s, %s)
                    """, (movie_name, movie_genre, movie_duration, movie_ticket_price))
                    movie_id = cursor.lastrowid
                    connection.commit()
                    print("\nMovie created with ID: ", movie_id)
                    add_shows(movie_id, cursor, connection)  # every new movie gets shows automatically
                except Error as e:
                    print(f"Operation Failed. Error: {e}")
                    connection.rollback()
                print('')
            case 2:
                print('SEARCH A MOVIE (by genre or name):\n')
                search_term = input("Enter Genre/Movie name to search: ")
                try:
                    cursor.execute("""
                        SELECT * FROM MOVIE
                        WHERE MovieName LIKE %s OR Genre LIKE %s
                    """, (f"%{search_term}%", f"%{search_term}%"))
                    search_results = cursor.fetchall()
                    if search_results:
                        print('\nSearch Results: \n')
                        for movie in search_results:
                            print(f'ID: {movie[0]}, Name: {movie[1]}, Genre: {movie[2]}, '
                                  f'Duration: {movie[3]} mins, Price: {movie[4]}')
                    else:
                        print(f"\nNo movies found matching '{search_term}'.\n")
                except Error as e:
                    print(f"Operation Failed. Error: {e}")
                    connection.rollback()
                print('')
            case 3:
                cursor.execute("SELECT MovieID, MovieName FROM MOVIE")
                movies = cursor.fetchall()
                if not movies:
                    print("No movies found.\n")
                    continue
                print("Available Movies:\n")
                for movie in movies:
                    print(f"ID: {movie[0]}, Name: {movie[1]}")
                movie_id = int(input("\nEnter Movie ID to display shows for: "))
                cursor.execute("""
                    SELECT s.ShowID, m.MovieName, s.ShowTime, s.TotalSeats, s.AvailableSeats
                    FROM `SHOW` s
                    JOIN MOVIE m ON s.MovieID = m.MovieID
                    WHERE s.MovieID = %s
                    ORDER BY s.ShowTime
                """, (movie_id,))
                shows = cursor.fetchall()
                if shows:
                    print(f"\nShows for '{shows[0][1]}':")
                    print("=" * 90)
                    print_table(['Show ID', 'Movie Name', 'Show Time', 'Total Seats', 'Available'],
                                [10, 20, 20, 15, 15], shows, 90)
                    print("=" * 90)
                    # Renamed to avoid shadowing the global total_seats used by add_shows
                    seats_total = sum(show[3] for show in shows)
                    seats_available = sum(show[4] for show in shows)
                    print(f"\nSummary for '{shows[0][1]}':")
                    print(f"  Total Shows: {len(shows)}")
                    print(f"  Total Seats: {seats_total}")
                    print(f"  Booked Seats: {seats_total - seats_available}")
                    print(f"  Available Seats: {seats_available}\n")
                else:
                    print(f"\nNo shows found for Movie ID: {movie_id}")
                    print("   Please add shows for this movie first.\n")
            case 4:
                print("\nShows available for booking: \n")
                cursor.execute("""
                    SELECT s.ShowID, m.MovieName, s.ShowTime, s.TotalSeats, s.AvailableSeats, m.TicketPrice
                    FROM `SHOW` s
                    JOIN MOVIE m ON s.MovieID = m.MovieID
                """)
                shows = cursor.fetchall()
                print("=" * 99)
                print_table(['Show ID', 'Movie Name', 'Show Time', 'Total Seats', 'Available Seats', 'Ticket Price'],
                            [10, 20, 20, 15, 15, 15], shows, 99)
                print("=" * 99 + "\n")
                show_id = int(input("Enter Show ID to book in: "))
                print("")
                # Find the selected show in the fetched list
                show_booking = None
                for show in shows:
                    if show[0] == show_id:
                        show_booking = show
                if show_booking is None:
                    print("Invalid Show ID.\n")
                    continue
                print("Booking a ticket for: ")
                print("  Show ID: ", show_booking[0])
                print("  Movie Name: ", show_booking[1])
                print("  Show Time: ", show_booking[2])
                consent = input("\nAre you sure? (y/n): ")
                print("")
                if consent == "y":
                    seat_num = int(input("Enter number of seats to book: "))
                    print("")
                    if seat_num > show_booking[4]:
                        print(f"{seat_num} exceeds the number of available seats.")
                        print("Returning to Menu. \n")
                        continue  # stop here so no booking is saved without seats
                    customer_name = input("Enter customer name: ")
                    total_amount = seat_num * show_booking[5]
                    print("\nTotal amount to be paid: ", total_amount)
                    print("\nBooking tickets... \n")
                    try:
                        cursor.execute(
                            "INSERT INTO BOOKING (CustomerName, ShowID, NumTickets, TotalAmount) "
                            "VALUES (%s, %s, %s, %s)",
                            (customer_name, show_booking[0], seat_num, total_amount))
                        # Capture Booking ID right after INSERT — an UPDATE would reset lastrowid
                        new_booking_id = cursor.lastrowid
                        # Seat check in WHERE guards against overbooking
                        cursor.execute(
                            "UPDATE `SHOW` SET AvailableSeats = AvailableSeats - %s "
                            "WHERE ShowID = %s AND AvailableSeats >= %s",
                            (seat_num, show_booking[0], seat_num))
                        connection.commit()
                        print(f"Booking done with Booking ID: {new_booking_id}\n")
                    except Error as e:
                        connection.rollback()
                        print(f"Operation Failed. Error: {e}\n")
                elif consent == "n":
                    print("Returning to Menu. \n")
                else:
                    print("Invalid Choice, please type 'y' or 'n'. \n")
            case 5:
                customer_name = input("Enter customer name: ")
                cursor.execute("""
                    SELECT b.BookingID, b.ShowID, b.NumTickets, b.TotalAmount,
                           m.MovieID, m.MovieName, s.ShowTime
                    FROM BOOKING b
                    JOIN `SHOW` s ON b.ShowID = s.ShowID
                    JOIN MOVIE m ON s.MovieID = m.MovieID
                    WHERE b.CustomerName = %s AND b.Status = 'Booked'
                """, (customer_name,))
                bookings = cursor.fetchall()
                if not bookings:
                    print(f"\nNo active bookings found for '{customer_name}'.\n")
                    continue
                print(f"\nBookings by {customer_name}: \n")
                rows = [(b[0], b[5], b[6], b[2], b[3]) for b in bookings]
                print_table(['Booking ID', 'Movie', 'Show Time', 'Seats', 'Total Amount'],
                            [10, 15, 15, 10, 15], rows, 65)
                print("=" * 65 + "\n")
            case 6:
                booking_id = int(input("Enter Booking ID: "))
                print("")
                # Only fetch active bookings — prevents double refunds
                cursor.execute("""
                    SELECT b.CustomerName, b.ShowID, b.NumTickets, b.TotalAmount, m.MovieName
                    FROM BOOKING b
                    JOIN `SHOW` s ON s.ShowID = b.ShowID
                    JOIN MOVIE m ON m.MovieID = s.MovieID
                    WHERE b.BookingID = %s AND b.Status = 'Booked'
                """, (booking_id,))
                booking = cursor.fetchone()
                if booking is None:
                    print("Booking not found or already cancelled.\n")
                    continue
                print("\nBooking Details: \n")
                print(" Customer Name:", booking[0])
                print(" Booking ID:", booking_id)
                print(" Show ID:", booking[1])
                print(" Movie Name:", booking[4])
                print(" Number of Seats:", booking[2])
                print(" Total Amount:", booking[3], "\n")
                consent = input("Are you sure you want to cancel this booking? (y/n): ")
                print("")
                if consent == "y":
                    # Soft-cancel (keeps the record) and give the seats back to the show
                    cursor.execute(
                        "UPDATE BOOKING SET Status = 'Cancelled' WHERE BookingID = %s",
                        (booking_id,))
                    cursor.execute(
                        "UPDATE `SHOW` SET AvailableSeats = AvailableSeats + %s WHERE ShowID = %s",
                        (booking[2], booking[1]))
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
                    rows = [(*b[:5], f"₹{b[5]:.2f}", b[6]) for b in all_bookings]
                    print_table(['ID', 'Customer', 'Movie', 'Time', 'Tickets', 'Amount', 'Status'],
                                [6, 20, 30, 15, 10, 12, 10], rows, 110)
                    print("=" * 110)
                    total = len(all_bookings)
                    active = sum(1 for b in all_bookings if b[6] == 'Booked')
                    print(f"\nTotal: {total} | Active: {active} | Cancelled: {total - active}")
                else:
                    print("No bookings found.")
                print("")
            case 8:
                print('Show-wise Revenue Report: \n')
                print('=' * 93)
                try:
                    # LEFT JOIN keeps shows with no bookings; cancelled bookings are excluded
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
                        print("No revenue data available.\n")
                        continue
                    # SUM() returns None for shows without bookings, so default to 0
                    rows = [(sid, name[:28], time, bk or 0, tk or 0, f"₹{(rev or 0.0):.2f}")
                            for sid, name, time, bk, tk, rev in results]
                    print_table(['Show ID', 'Movie', 'Time', 'Bookings', 'Tickets', 'Revenue'],
                                [10, 30, 15, 12, 12, 12], rows, 93)
                    total_bookings = sum(r[3] for r in rows)
                    total_tickets = sum(r[4] for r in rows)
                    total_revenue = sum((rev or 0.0) for *_, rev in results)
                    print("-" * 93)
                    print(f"{'TOTALS':<57} {total_bookings:<12} {total_tickets:<12} "
                          f"₹{total_revenue:<11.2f}")
                    print("=" * 93 + "\n")
                except Error as e:
                    print(f"Error generating revenue report: {e}\n")
            case 9:
                print('Exiting...')
                break
            case _:
                print("Invalid choice. Please choose from 1 to 9 according to the menu")
