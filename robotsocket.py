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

    # Define two sets of angles
    angle1 = "-167.06,-16.35,48.15,-122.25,-88.05,-77.05"
    angle2 = "-155.96,-38.27,79.28,-130,-88.23,-66"

    # Define the number of cycles and delay between movements
    cycles = int(input("Enter the number of cycles: "))  # Number of times to move back and forth
    delay = float(input("Enter the delay between movements (in seconds): "))  # Delay between movements

    # Loop to alternate between the two angles
    for i in range(cycles):
        print(f"Cycle {i + 1}/{cycles}")

        # Move to the first set of angles
        print("Moving to Angle 1...")
        message1 = f"set_angles({angle1}, {SPEED})"
        send_tcp_packet(SERVER_IP, SERVER_PORT, message1)

        # Wait for the specified delay
        time.sleep(delay)

        # Move to the second set of angles
        print("Moving to Angle 2...")
        message2 = f"set_angles({angle2}, {SPEED})"
        send_tcp_packet(SERVER_IP, SERVER_PORT, message2)

        # Wait for the specified delay
        time.sleep(delay)

    print("Motion completed!")