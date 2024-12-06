import socket
import csv
import time

def send_tcp_packet(server_ip, server_port, message):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))
        print(f"Connected to {server_ip}:{server_port}")
        client_socket.sendall(message.encode('utf-8'))
        print(f"Sent: {message}")
        response = client_socket.recv(1024).decode('utf-8')
        print(f"Received: {response}")
    except socket.error as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        print("Connection closed.")

def read_angles_from_csv(filename):
    angles = []
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            angle = f"{row['Joint1']},{row['Joint2']},{row['Joint3']},{row['Joint4']},{row['Joint5']},{row['Joint6']}"
            angles.append(angle)
    return angles

if __name__ == "__main__":
    SERVER_IP = "192.168.1.159"  # Replace with your robot's server IP
    SERVER_PORT = 5001  # Replace with your robot's server port
    SPEED = 500  # Constant speed for the movements

    # Read angles from CSV file
    angles = read_angles_from_csv('mazeangles.csv')

    # Move through all angles
    print("Moving through angles...")
    for i, angle in enumerate(angles):
        print(f"Moving to position {i+1}/{len(angles)}")
        message = f"set_angles({angle}, {SPEED})"
        send_tcp_packet(SERVER_IP, SERVER_PORT, message)
        time.sleep(0.1)  # Small delay to ensure command is processed

    # Ask if user wants to go in reverse
    reverse = input("Do you want to go in reverse? (yes/no): ").lower().strip()

    if reverse == 'yes':
        print("Moving in reverse...")
        for i, angle in enumerate(reversed(angles)):
            print(f"Moving to position {len(angles)-i}/{len(angles)}")
            message = f"set_angles({angle}, {SPEED})"
            send_tcp_packet(SERVER_IP, SERVER_PORT, message)
            time.sleep(0.1)  # Small delay to ensure command is processed

    print("Motion completed!")