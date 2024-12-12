import socket
import time  # For adding delay between movements
import csv

def send_tcp_packet(server_ip, server_port, message):
    """
    Sends a TCP packet to the robot with the given message.
    """
    try:
        # Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the server
        client_socket.connect((server_ip, server_port))
        print(f"Connected to {server_ip}:{server_port}")

        # Send the message
        client_socket.sendall(message.encode('utf-8'))
        print(f"Sent: {message}")

        # Optionally receive a response (if server sends one)
        response = client_socket.recv(1024).decode('utf-8')
        print(f"Received: {response}")

    except socket.error as e:
        print(f"Error: {e}")

    finally:
        # Close the connection
        client_socket.close()
        print("Connection closed.")

if __name__ == "__main__":
    # Server details
    SERVER_IP = "192.168.1.159"  # Replace with your robot's server IP
    SERVER_PORT = 5001  # Replace with your robot's server port
    SPEED = 500  # Speed for the movements

    # Define the CSV file path here
    csv_file = "path/to/your/angles.csv"  # Replace with the actual path to your CSV file
    DELAY = 1.0  # Delay between movements in seconds

    try:
        with open(csv_file, 'r') as file:
            csv_reader = csv.reader(file)
            header = next(csv_reader, None)  # Skip the header row if present

            for row in csv_reader:
                angles = ','.join(row)  # Combine all joint angles into a single string
                print(f"Moving to angles: {angles}")
                message = f"set_angles({angles}, {SPEED})"
                send_tcp_packet(SERVER_IP, SERVER_PORT, message)

                # Wait for the specified delay
                time.sleep(DELAY)

        print("Motion completed!")

    except FileNotFoundError:
        print(f"Error: File {csv_file} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
