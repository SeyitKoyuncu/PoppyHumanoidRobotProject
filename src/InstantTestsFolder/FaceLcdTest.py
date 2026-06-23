""" import pygame
import sys
import math

print("Starting Face LCD Test...")
# Initialize Pygame
pygame.init()

print("Pygame initialized successfully.")
# Screen settings
width = 800
height = 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Dynamic Robot Face")
print("Display window created with size 800x480.")


# Colors (RGB format)
print("Setting up colors...")
BLACK = (0, 0, 0)
BLUE = (0, 200, 255) # A robotic light blue
print("Colors defined: BLACK and BLUE.")

print("Entering main loop. Use keys 1-4 to change expressions, Q to quit.")
# Initial state
expression = "neutral"
print("Initial expression set to neutral.")

running = True
while running:
    print("Processing events...")
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Keyboard controls for testing (keys 1, 2, 3, 4)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                expression = "neutral"
            elif event.key == pygame.K_2:
                expression = "happy"
            elif event.key == pygame.K_3:
                expression = "sad"
            elif event.key == pygame.K_4:
                expression = "confused"
            elif event.key == pygame.K_q:
                running = False

    # 1. Clear the screen (fill with black)
    screen.fill(BLACK)

    # 2. DRAW THE EYES (Static)
    # Left Eye: (X: 250, Y: 150), Radius: 40
    pygame.draw.circle(screen, BLUE, (250, 150), 40)
    # Right Eye: (X: 550, Y: 150), Radius: 40
    pygame.draw.circle(screen, BLUE, (550, 150), 40)

    # 3. DRAW THE MOUTH (Dynamic based on expression)
    # The imaginary bounding box for the mouth arc (X, Y, Width, Height)
    mouth_area = (250, 250, 300, 100) 
    thickness = 15

    if expression == "neutral":
        # A straight line (Start X,Y and End X,Y)
        pygame.draw.line(screen, BLUE, (250, 300), (550, 300), thickness)
        
    elif expression == "happy":
        # Downward arc (Smile) - Drawn from Pi to 2*Pi
        pygame.draw.arc(screen, BLUE, mouth_area, math.pi, 2 * math.pi, thickness)
        
    elif expression == "sad":
        # Upward arc (Sad) - Drawn from 0 to Pi
        # We increase the Y value slightly to shift the mouth down
        sad_mouth_area = (250, 300, 300, 100)
        pygame.draw.arc(screen, BLUE, sad_mouth_area, 0, math.pi, thickness)
        
    elif expression == "confused":
        # A diagonal / slanted line (Confused, skeptical)
        pygame.draw.line(screen, BLUE, (250, 330), (550, 270), thickness)

    # Update the display
    pygame.display.flip()

pygame.quit()
sys.exit() """

import pygame
import sys
import math
import threading

# Initialize Pygame
pygame.init()

# Screen settings
width = 800
height = 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Dynamic Robot Face")

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 200, 255)

# Shared variable for expression
expression = "neutral"
running = True

# Function to listen for commands via the terminal (SSH) in the background
def terminal_listener():
    global expression, running
    print("\n--- Poppy Control Panel ---")
    print("Type a number in the terminal and press ENTER:")
    print("1: Neutral | 2: Happy | 3: Sad | 4: Confused | q: Quit")
    
    while running:
        try:
            command = input("Command: ")
            if command == '1':
                expression = "neutral"
            elif command == '2':
                expression = "happy"
            elif command == '3':
                expression = "sad"
            elif command == '4':
                expression = "confused"
            elif command == 'q':
                running = False
                print("Shutting down...")
        except Exception:
            pass

# Start the background listener (Thread)
listener = threading.Thread(target=terminal_listener)
listener.daemon = True
listener.start()

# Main Pygame loop
while running:
    # Pygame needs to process events to prevent crashing/freezing
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. Clear the screen
    screen.fill(BLACK)

    # 2. Draw the eyes
    pygame.draw.circle(screen, BLUE, (250, 150), 40)
    pygame.draw.circle(screen, BLUE, (550, 150), 40)

    # 3. Draw the mouth
    mouth_area = (250, 250, 300, 100) 
    thickness = 15

    if expression == "neutral":
        pygame.draw.line(screen, BLUE, (250, 300), (550, 300), thickness)
        
    elif expression == "happy":
        pygame.draw.arc(screen, BLUE, mouth_area, math.pi, 2 * math.pi, thickness)
        
    elif expression == "sad":
        sad_mouth_area = (250, 300, 300, 100)
        pygame.draw.arc(screen, BLUE, sad_mouth_area, 0, math.pi, thickness)
        
    elif expression == "confused":
        pygame.draw.line(screen, BLUE, (250, 330), (550, 270), thickness)

    # Update the display
    pygame.display.flip()
    
    # A short delay to prevent high CPU usage (50 milliseconds)
    pygame.time.delay(50)

pygame.quit()
sys.exit()