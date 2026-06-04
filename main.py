import cv2
import pygame
import sys
import numpy as np
from vision_engine import VisionEngine
from audio_engine import AudioEngine

# Configuration
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
TOTAL_SEGMENTS = 12
KEY_ZONE_THRESHOLD = 0.6 # Bottom 40%

def main():
    # Initialize Pygame
    pygame.init()
    try:
        pygame.font.init()
    except:
        print("Warning: Font module failed to initialize")

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Virtuoso Piano (Python)")
    clock = pygame.time.Clock()

    # Initialize Engines
    print("Initialize Audio...")
    audio = AudioEngine()
    print("Initialize Vision...")
    try:
        vision = VisionEngine(WINDOW_WIDTH, WINDOW_HEIGHT)
    except Exception as e:
        print(f"Failed to init vision: {e}")
        return

    # Webcam Setup
    cap = cv2.VideoCapture(0)
    # Increase buffer size or wait?
    
    if not cap.isOpened():
        print("Error: Could not open camera (Index 0). Trying Index 1...")
        cap = cv2.VideoCapture(1)
        if not cap.isOpened():
            print("Error: Could not open camera (Index 1). Exiting.")
            return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WINDOW_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WINDOW_HEIGHT)
    print(f"Camera opened successfully: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    # State
    segment_state = [False] * TOTAL_SEGMENTS
    running = True

    # SCALES CONFIGURATION
    # 0 = Ishq Jalakar Mode
    # 1 = Never Gonna Give You Up Mode
    # 2 = Na De Dil Pardesi Nu Mode
    # 3 = Shape of You Mode
    # 4 = Blinding Lights Mode
    current_scale_mode = 0 
    
    # Octave Offset
    octave_shift = 1 
    
    # Game State: 0 = Homepage Menu, 1 = Playing Piano
    game_state = 0 
    
    def get_note_index(segment_i, mode, shift):
        base_index = shift * 12
        
        if mode == 0: # Ishq Jalakar (Harmonic Minor)
            sufi_offsets = [0, 2, 3, 5, 7, 8, 11, 12, 14, 15, 17, 19]
            if segment_i < len(sufi_offsets):
                return base_index + sufi_offsets[segment_i]
            return base_index
        elif mode == 1: # Never Gonna Give You Up (Major Diatonic)
            major_offsets = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19]
            if segment_i < len(major_offsets):
                return base_index + major_offsets[segment_i]
            return base_index
        elif mode == 2: # Na De Dil Pardesi Nu (Natural Minor)
            minor_offsets = [0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19]
            if segment_i < len(minor_offsets):
                return base_index + minor_offsets[segment_i]
            return base_index
        elif mode == 3: # Shape of You (Minor Pentatonic)
            penta_offsets = [0, 3, 5, 7, 10, 12, 15, 17, 19, 22, 24, 27]
            if segment_i < len(penta_offsets):
                return base_index + penta_offsets[segment_i]
            return base_index
        elif mode == 4: # Blinding Lights (Dorian/Minor)
            dorian_offsets = [0, 2, 3, 5, 7, 9, 10, 12, 14, 15, 17, 19]
            if segment_i < len(dorian_offsets):
                return base_index + dorian_offsets[segment_i]
            return base_index
        return 0
        
    def get_scale_name(mode, shift):
        base_note = f"C{shift + 3}"
        if mode == 0: return f"Ishq Jalakar ({base_note})"
        if mode == 1: return f"Never Gonna Give You Up ({base_note})"
        if mode == 2: return f"Na De Dil Pardesi Nu ({base_note})"
        if mode == 3: return f"Shape of You ({base_note})"
        if mode == 4: return f"Blinding Lights ({base_note})"
        return "Unknown"

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif game_state == 0:
                    # In Homepage Menu
                    if event.key == pygame.K_1: current_scale_mode = 0; game_state = 1
                    if event.key == pygame.K_2: current_scale_mode = 1; game_state = 1
                    if event.key == pygame.K_3: current_scale_mode = 2; game_state = 1
                    if event.key == pygame.K_4: current_scale_mode = 3; game_state = 1
                    if event.key == pygame.K_5: current_scale_mode = 4; game_state = 1
                elif game_state == 1:
                    # In Game
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                        game_state = 0 # Return to Homepage
                    elif event.key == pygame.K_s:
                        current_scale_mode = (current_scale_mode + 1) % 5
                        print(f"Switched to {get_scale_name(current_scale_mode, octave_shift)}")
                    elif event.key == pygame.K_UP:
                        octave_shift = min(octave_shift + 1, 2)
                        print(f"Octave Up: {get_scale_name(current_scale_mode, octave_shift)}")
                    elif event.key == pygame.K_DOWN:
                        octave_shift = max(octave_shift - 1, 0)
                        print(f"Octave Down: {get_scale_name(current_scale_mode, octave_shift)}")

        if game_state == 0:
            # Draw Homepage Menu
            screen.fill((10, 10, 20)) # Dark Blue background
            try:
                # Big Title
                font_title = pygame.font.SysFont("Arial", 64, bold=True)
                title_surf = font_title.render("Virtual Air Piano", True, (0, 255, 204))
                screen.blit(title_surf, (WINDOW_WIDTH//2 - title_surf.get_width()//2, 80))
                
                # Instruction
                font_sub = pygame.font.SysFont("Arial", 32)
                sub_surf = font_sub.render("Press a number (1-5) to choose your song & start:", True, (255, 255, 255))
                screen.blit(sub_surf, (WINDOW_WIDTH//2 - sub_surf.get_width()//2, 180))
                
                # Song Options
                font_opt = pygame.font.SysFont("Arial", 28)
                options = [
                    "1. Ishq Jalakar (Dhurandar)",
                    "2. Never Gonna Give You Up",
                    "3. Na De Dil Pardesi Nu (Dhurandar)",
                    "4. Shape of You (Ed Sheeran)",
                    "5. Blinding Lights (Weeknd)"
                ]
                
                start_y = 260
                for opt in options:
                    opt_surf = font_opt.render(opt, True, (200, 200, 255))
                    screen.blit(opt_surf, (WINDOW_WIDTH//2 - 200, start_y))
                    start_y += 50
                    
                # Footer
                font_footer = pygame.font.SysFont("Arial", 24, bold=True)
                footer_surf = font_footer.render("By IETE-SF MPSTME, For U'lectro 2026!", True, (112, 0, 255))
                screen.blit(footer_surf, (WINDOW_WIDTH//2 - footer_surf.get_width()//2, WINDOW_HEIGHT - 60))
                
            except Exception as e:
                pass
                
            pygame.display.flip()
            clock.tick(60)
            continue

        # 1. Capture Frame (Only runs if game_state == 1)
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Flip frame horizontally for mirror effect
        frame_flipped = cv2.flip(frame, 1)

        # 2. Vision Processing
        results, fingertips = vision.process_frame(frame_flipped)

        # 3. Logic: Check Triggers
        current_active_segments = set()
        
        if fingertips:
            for (x, y) in fingertips:
                if y > KEY_ZONE_THRESHOLD:
                    segment_index = int(x * TOTAL_SEGMENTS)
                    if 0 <= segment_index < TOTAL_SEGMENTS:
                        current_active_segments.add(segment_index)

        # Trigger Sounds
        for i in range(TOTAL_SEGMENTS):
            is_active = i in current_active_segments
            
            if is_active and not segment_state[i]:
                # On Press
                mapped_note = get_note_index(i, current_scale_mode, octave_shift)
                audio.play_note(mapped_note)
                segment_state[i] = True
            elif not is_active and segment_state[i]:
                # On Release
                segment_state[i] = False

        # 4. Rendering
        frame_rgb = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2RGB)
        frame_rgb = np.rot90(frame_rgb)
        frame_rgb = np.flipud(frame_rgb)
        
        pygame_frame = pygame.surfarray.make_surface(frame_rgb)
        screen.blit(pygame_frame, (0, 0))

        # Draw Grid & UI
        segment_width = WINDOW_WIDTH / TOTAL_SEGMENTS
        
        # Transparent overlay surface
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        
        for i in range(TOTAL_SEGMENTS):
            x = i * segment_width
            
            # Vertical Line
            pygame.draw.line(overlay, (255, 255, 255, 50), (x, 0), (x, WINDOW_HEIGHT), 2)
            
            # Key Zone Highlight
            rect_color = (255, 255, 255, 20)
            if segment_state[i]:
                rect_color = (100, 255, 100, 100)
            
            zone_height = WINDOW_HEIGHT * (1 - KEY_ZONE_THRESHOLD)
            zone_y = WINDOW_HEIGHT * KEY_ZONE_THRESHOLD
            
            pygame.draw.rect(overlay, rect_color, (x, zone_y, segment_width, zone_height))
            
            # Optional: Draw Note Name in Segment
            # (Requires font init)

        # "Key Zone" Line
        pygame.draw.line(overlay, (200, 200, 200), (0, WINDOW_HEIGHT * KEY_ZONE_THRESHOLD), (WINDOW_WIDTH, WINDOW_HEIGHT * KEY_ZONE_THRESHOLD), 2)

        screen.blit(overlay, (0, 0))
        
        # Draw fingertips debugging
        for (x, y) in fingertips:
            px, py = int(x * WINDOW_WIDTH), int(y * WINDOW_HEIGHT)
            pygame.draw.circle(screen, (255, 0, 0), (px, py), 12)
            
        # UI Text: Scale Mode
        try:
            if pygame.font.get_init():
                font = pygame.font.SysFont("Arial", 24)
                label = font.render(f"Playing: {get_scale_name(current_scale_mode, octave_shift)} | [ESC] Homepage | [Q] Quit", True, (255, 255, 255))
                # Add a black background rect behind text for visibility
                pygame.draw.rect(screen, (0,0,0), (5, 5, label.get_width()+10, label.get_height()+10))
                screen.blit(label, (10, 10))
                
                # Footer text in-game
                font_footer = pygame.font.SysFont("Arial", 20, bold=True)
                footer_surf = font_footer.render("By IETE-SF MPSTME, For U'lectro 2026!", True, (112, 0, 255))
                screen.blit(footer_surf, (WINDOW_WIDTH - footer_surf.get_width() - 10, WINDOW_HEIGHT - 30))
        except Exception as e:
            # If font fails, just ignore it so app doesn't crash
            pass

        pygame.display.flip()

        clock.tick(60)

    cap.release()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
