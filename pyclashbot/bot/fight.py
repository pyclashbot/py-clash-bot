"""Fight logic for Clash Royale bot"""

import collections
import random
import time
from typing import Literal
from collections import deque

import cv2

from pyclashbot.bot.card_detection import (
    check_which_cards_are_available,
    create_default_bridge_iar,
    switch_side,
)
from pyclashbot.bot.nav import (
    check_for_in_battle_with_delay,
    check_for_trophy_reward_menu,
    check_if_in_battle,
    check_if_on_clash_main_menu,
    get_to_activity_log,
    handle_trophy_reward_menu,
    wait_for_battle_start,
    wait_for_clash_main_menu,
)
from pyclashbot.bot.recorder import save_image, save_play, save_win_loss
from pyclashbot.detection.image_rec import (
    check_line_for_color,
    find_image,
    pixel_is_equal,
)
from pyclashbot.utils.logger import Logger

# Simple hardcoded flags for fight vision
ENABLE_FIGHT_VISION = True
ENABLE_DEBUG_VISUALIZATION = True

# Timing and debug toggle flags
TIMING_INFERENCE = True         # Enable inference timing prints
TIMING_VISUALIZATION = True     # Enable visualization timing prints  
DEBUG_FIGHT_VISION = True       # Enable debug information for fight vision results

from pyclashbot.vision.interface import LocalInferenceProvider, InferenceManager
from pyclashbot.vision.simple_draw import draw_fight_results, get_fight_stats, draw_waiting


def get_inference_device(vision_system):
    """Detect what device is being used for inference across all models."""
    if not vision_system:
        return "None"
        
    try:
        # Try to access the inference provider's models
        if hasattr(vision_system, 'current_provider'):
            provider = vision_system.current_provider
            
            # Check if it's a LocalInferenceProvider with vision_system
            if hasattr(provider, 'vision_system'):
                vision = provider.vision_system
                
                # Check unit detector
                if hasattr(vision, 'unit_detector') and hasattr(vision.unit_detector, 'session'):
                    providers = vision.unit_detector.session.get_providers()
                    if 'CUDAExecutionProvider' in providers:
                        return 'CUDA'
                    elif 'DmlExecutionProvider' in providers:
                        return 'DirectML'
                    else:
                        return 'CPU'
        
        return "Unknown"
    except:
        return "Unknown"


def format_fight_vision_results(vision_results, logger_prefix="[1v1_fight]") -> str:
    """Format fight vision results for clean terminal display."""
    if not DEBUG_FIGHT_VISION or not hasattr(vision_results, 'units'):
        return ""
    
    lines = []
    lines.append(f"{logger_prefix} ===== FIGHT VISION ANALYSIS =====")
    
    # Summary statistics
    units = getattr(vision_results, 'units', [])
    hand_cards = getattr(vision_results, 'hand_cards', [])
    tower_health = getattr(vision_results, 'tower_health', {})
    elapsed_ms = getattr(vision_results, 'elapsed_ms', 0)
    
    lines.append(f"{logger_prefix} Summary: {len(units)} units, {len(hand_cards)} cards, {len(tower_health)} towers")
    lines.append(f"{logger_prefix} Analysis time: {elapsed_ms:.1f}ms")
    
    # Units breakdown by side
    if units:
        friendly_units = [u for u in units if u.get('side') == 'friendly']
        enemy_units = [u for u in units if u.get('side') == 'enemy']
        
        lines.append(f"{logger_prefix} Units: {len(friendly_units)} friendly, {len(enemy_units)} enemy")
        
        # Show unit details
        lines.append(f"{logger_prefix} Unit Details:")
        for i, unit in enumerate(units[:10]):  # Limit to first 10 units for readability
            track_id = unit.get('track_id', 'N/A')[:8] if unit.get('track_id') else 'N/A'
            cls_label = unit.get('cls_label', 'unknown')
            side = unit.get('side', 'unknown')[:1].upper()  # F/E/U
            x1, y1, x2, y2 = unit.get('xyxy', [0, 0, 0, 0])
            det_score = unit.get('det_score', 0) * 100
            
            track_age = unit.get('track_age', 0)
            time_alive = unit.get('time_alive', 0)
            
            lines.append(f"{logger_prefix}   {i+1:2d}. [{track_id}] {side}:{cls_label:15} pos:({x1:3d},{y1:3d}) conf:{det_score:4.1f}% age:{track_age:2d} alive:{time_alive:5.1f}s")
    
    # Hand cards
    if hand_cards:
        lines.append(f"{logger_prefix} Hand Cards:")
        for card in hand_cards:
            pos = card.get('position', '?')
            label = card.get('label', 'unknown')
            confidence = card.get('confidence', 0) * 100
            stability = card.get('stability', 0)
            
            lines.append(f"{logger_prefix}   Slot {pos}: {label:20} conf:{confidence:5.1f}% stability:{stability:2d}")
    
    # Tower health summary  
    if tower_health:
        lines.append(f"{logger_prefix} Tower Health:")
        tower_order = ['enemy_left_tower', 'enemy_main_tower', 'enemy_right_tower',
                      'friendly_left_tower', 'friendly_main_tower', 'friendly_right_tower']
        
        for tower_name in tower_order:
            if tower_name in tower_health:
                tower = tower_health[tower_name]
                label = tower.get('label', 'unknown')
                confidence = tower.get('confidence', 0) * 100
                
                tower_display = tower_name.replace('_', ' ').title()
                lines.append(f"{logger_prefix}   {tower_display:20}: {label:10} conf:{confidence:5.1f}%")
    
    lines.append(f"{logger_prefix} ===================================")
    
    return "\n".join(lines)

# Battle UI coordinates
HAND_CARDS_COORDS = [(142, 561), (210, 563), (272, 561), (341, 563)]
EMOTE_BUTTON_COORD = (67, 521)
EMOTE_ICON_COORDS = [(124, 419), (182, 420), (255, 411), (312, 423), 
                     (133, 471), (188, 472), (243, 469), (308, 470)]
CLASH_MAIN_DEADSPACE_COORD = (20, 520)
CLOSE_BATTLE_LOG_BUTTON = (365, 72)

# Elixir detection
ELIXIR_COORDS = [[613, 149 + i * 25] for i in range(10)]  # Simplified elixir coord generation
ELIXIR_COLOR = [240, 137, 244]
ELIXER_WAIT_TIMEOUT = 40


def initialize_vision_system():
    """Initialize the vision system if enabled."""
    if not ENABLE_FIGHT_VISION:
        return None
    
    try:
        # Create local inference provider
        local_provider = LocalInferenceProvider()
        inference_manager = InferenceManager(local_provider)
        
        if inference_manager.initialize():
            print("Fight vision enabled")
            return inference_manager
        else:
            return None
    except Exception as e:
        print(f"Failed to initialize vision system: {e}")
        return None


def initialize_debug_visualizer():
    """Initialize the debug visualization system if enabled (simplified approach)."""
    if not ENABLE_DEBUG_VISUALIZATION:
        return None
    
    # Simple visualization is now handled directly in the fight loop
    # No complex visualizer object needed
    return True


def do_fight_state(
    emulator,
    logger: Logger,
    random_fight_mode,
    fight_mode_choosed,
    called_from_launching=False,
    recording_flag: bool = False,
    vision_system=None,
    debug_visualizer=None,
) -> bool:
    """Handle complete battle: wait for start, fight, log results."""
    
    # Auto-initialize vision systems if not provided
    if vision_system is None and ENABLE_FIGHT_VISION:
        vision_system = initialize_vision_system()
    
    if debug_visualizer is None and ENABLE_DEBUG_VISUALIZATION:
        debug_visualizer = initialize_debug_visualizer()
        if debug_visualizer:
            print("Simple debug visualization enabled - press ESC during fight to disable")
    
    logger.change_status("Waiting for battle to start")
    
    if not wait_for_battle_start(emulator, logger):
        logger.change_status("Failed to start battle")
        return False

    logger.change_status("Starting fight")
    
    # Choose fight strategy
    fight_success = (_random_fight_loop(emulator, logger) if random_fight_mode 
                    else _fight_loop(emulator, logger, recording_flag, vision_system, debug_visualizer))
    
    if not fight_success:
        logger.log("Fight failed")
        return False

    # Log fight statistics
    if not called_from_launching:
        _log_fight_stats(logger, fight_mode_choosed)

    time.sleep(10)
    return True

def _log_fight_stats(logger: Logger, mode: str):
    """Log fight statistics based on mode."""
    if mode in ["Classic 1v1", "Trophy Road"]:
        logger.add_1v1_fight()
    elif mode == "Classic 2v2":
        logger.increment_2v2_fights()
    
    # Mode-specific logging
    mode_map = {
        "Trophy Road": logger.increment_trophy_road_fights,
        "Classic 1v1": logger.increment_classic_1v1_fights,
        "Classic 2v2": logger.increment_classic_2v2_fights,
    }
    if mode in mode_map:
        mode_map[mode]()


def do_2v2_fight_state(emulator, logger: Logger, random_fight_mode, recording_flag: bool = False) -> bool:
    """Handle 2v2 battle - wrapper for do_fight_state."""
    return do_fight_state(emulator, logger, random_fight_mode, "Classic 2v2", 
                         called_from_launching=False, recording_flag=recording_flag)


def start_fight(emulator, logger, mode) -> bool:
    """Start a fight with the specified mode."""
    valid_modes = ["Classic 1v1", "Classic 2v2", "Trophy Road"]
    if mode not in valid_modes or not check_if_on_clash_main_menu(emulator):
        logger.log(f"Cannot start fight - invalid mode '{mode}' or not on main menu")
        return False

    logger.change_status(f"Starting {mode} fight")
    emulator.click(203, 487)  # Start button

    # Handle 2v2 quickmatch popup
    if mode == "Classic 2v2":
        time.sleep(3)
        emulator.click(280, 350)  # Quickmatch button

    return True


def send_emote(emulator, logger: Logger):
    """Send a random emote during battle."""
    logger.change_status("Sending emote")
    emulator.click(*EMOTE_BUTTON_COORD)
    time.sleep(0.33)
    emote_coord = random.choice(EMOTE_ICON_COORDS)
    emulator.click(*emote_coord)


def mag_dump(emulator, logger):
    """Play 3 random cards at random locations (for random mode)."""
    logger.log("Playing random cards...")
    for i in range(3):
        card_coord = random.choice(HAND_CARDS_COORDS)
        play_coord = (random.randint(101, 440), random.randint(50, 526))
        
        emulator.click(*card_coord)
        time.sleep(0.1)
        emulator.click(*play_coord)
        time.sleep(0.1)

def count_elixer(emulator, elixer_count) -> bool:
    """Check if we have the required elixir amount."""
    if elixer_count < 1 or elixer_count > 10:
        return False
    
    screenshot = emulator.screenshot()
    pixel_coord = ELIXIR_COORDS[elixer_count - 1]
    pixel = screenshot[pixel_coord[0], pixel_coord[1]]
    
    return pixel_is_equal(pixel, ELIXIR_COLOR, tol=65)


def end_fight_state(
    emulator,
    logger: Logger,
    recording_flag,
    disable_win_tracker_toggle=True,
):
    """Handle post-fight cleanup: return to main, check win/loss."""
    logger.log("Returning to main menu")
    if not get_to_main_after_fight(emulator, logger):
        logger.log("Failed to return to main menu")
        return False

    time.sleep(3)
    
    # Track win/loss if enabled
    if not disable_win_tracker_toggle:
        win_result = check_if_previous_game_was_win(emulator, logger)
        
        if win_result == "restart":
            logger.log("Failed to check previous game result")
            return False
        
        # Log result
        if win_result:
            logger.add_win()
            if recording_flag:
                save_win_loss("win")
        else:
            logger.add_loss()
            if recording_flag:
                save_win_loss("loss")

    return True


def check_if_previous_game_was_win(emulator, logger: Logger) -> bool | Literal["restart"]:
    """Check if the previous game was a win by examining battle log."""
    logger.change_status("Checking previous game result")

    if not wait_for_clash_main_menu(emulator, logger, deadspace_click=True):
        return "restart"

    if get_to_activity_log(emulator, logger, printmode=False) == "restart":
        return "restart"

    is_win = check_pixels_for_win_in_battle_log(emulator)
    logger.change_status(f"Previous game result: {'Win' if is_win else 'Loss'}")

    # Return to main menu
    emulator.click(*CLOSE_BATTLE_LOG_BUTTON)
    if not wait_for_clash_main_menu(emulator, logger):
        return "restart"
    
    time.sleep(2)
    return is_win


def check_pixels_for_win_in_battle_log(emulator) -> bool:
    """Check for red defeat indicators in battle log. If found = loss, otherwise = win."""
    defeat_color = (255, 51, 102)
    
    # Check three lines that form the defeat indicator
    defeat_lines = [
        check_line_for_color(emulator, 47, 135, 109, 154, defeat_color),
        check_line_for_color(emulator, 46, 152, 115, 137, defeat_color),
        check_line_for_color(emulator, 47, 144, 110, 147, defeat_color),
    ]
    
    # If all defeat lines are present, it's a loss
    return not all(defeat_lines)


def find_post_battle_button(emulator):
    """Find post-battle button using pixel detection or image recognition."""
    screenshot = emulator.screenshot()

    # Try pixel-based detection first (fastest)
    test_pixels = [(545, 178), (547, 239), (553, 214), (554, 201)]
    expected_colors = [[255, 187, 104], [255, 187, 104], [255, 255, 255], [255, 255, 255]]
    
    if all(pixel_is_equal(screenshot[y][x], expected_colors[i], tol=20) 
           for i, (y, x) in enumerate(test_pixels)):
        return (200, 550)

    # Try image recognition fallbacks
    for button_type, tolerance in [("ok_post_battle_button", 0.85), ("exit_battle_button", 0.9)]:
        coord = find_image(screenshot, button_type, tolerance=tolerance)
        if coord:
            return coord

    return None


def get_to_main_after_fight(emulator, logger):
    """Navigate back to main menu after a fight, handling popups."""
    start_time = time.time()
    clicked_ok_or_exit = False
    timeout = 120

    logger.change_status("Returning to main menu...")

    while time.time() - start_time < timeout:
        # Check if we're on main menu
        if check_if_on_clash_main_menu(emulator):
            time.sleep(3)  # Wait for potential trophy rewards
            
            if check_for_trophy_reward_menu(emulator):
                handle_trophy_reward_menu(emulator, logger, printmode=False)
                time.sleep(2)
            
            return True

        # Handle trophy rewards
        if check_for_trophy_reward_menu(emulator):
            handle_trophy_reward_menu(emulator, logger, printmode=False)
            time.sleep(3)
            continue

        # Click post-battle button if found
        if not clicked_ok_or_exit:
            button_coord = find_post_battle_button(emulator)
            if button_coord:
                emulator.click(*button_coord)
                clicked_ok_or_exit = True
                continue

        # Click deadspace to close popups
        time.sleep(1)
        emulator.click(*CLASH_MAIN_DEADSPACE_COORD)

    return False


# main fight loops

# Track recently played cards to avoid repetition
last_three_cards = collections.deque(maxlen=3)

def select_card_index(card_indices, recent_cards):
    """Select a card index, avoiding recently played cards when possible."""
    if not card_indices:
        raise ValueError("No cards available")

    # Try to avoid recently played cards (priority order)
    for avoid_count in [len(recent_cards), 2, 1, 0]:  # Avoid all recent, then last 2, then last 1, then none
        avoid_set = set(list(recent_cards)[-avoid_count:] if avoid_count > 0 else [])
        candidates = [idx for idx in card_indices if idx not in avoid_set]
        if candidates:
            return random.choice(candidates)
    
    # Fallback: any available card
    return random.choice(card_indices)


def play_a_card(emulator, logger, recording_flag: bool, battle_strategy: "BattleStrategy", vision_results=None) -> bool:
    """Play a random card at a random location, optionally using vision data for future decisions."""
    
    # For now, keep random play logic - vision_results can be used later for smart decisions
    if vision_results and DEBUG_FIGHT_VISION:
        # Optional: print simplified vision summary for card play decisions
        units = getattr(vision_results, 'units', []) if vision_results else []
        if units:
            friendly_count = sum(1 for u in units if u.get('side') == 'friendly')
            enemy_count = sum(1 for u in units if u.get('side') == 'enemy')
            logger.change_status(f"Vision context: F:{friendly_count} E:{enemy_count} units")
    
    # Pick a random card (0-3)
    card_index = random.randint(0, 3)
    
    # Play it at random coords (x:200-300, y:300-400)
    play_coord = (random.randint(200, 300), random.randint(300, 400))
    
    logger.change_status(f"Playing random card {card_index} at {play_coord}")
    
    # Execute the play
    emulator.click(*HAND_CARDS_COORDS[card_index])
    emulator.click(*play_coord)
    
    # Record and log
    if recording_flag:
        save_play(play_coord, card_index)
    
    logger.add_card_played()
    
    return True


class BattleStrategy:
    """Manages battle timing and elixir selection based on battle phase."""

    def __init__(self):
        self.start_time = None
        
        # Elixir strategy: [3, 4, 5, 6, 7, 8, 9] with phase-based weights
        self.strategies = {
            "early": ([7, 8, 9], (6000, 9000)),      # 0-7s: Wait for high elixir, conservative thresholds
            "single": ([4, 5, 6, 7, 8], (6000, 9000)),  # 7-90s: Balanced play
            "double": ([5, 6, 7, 8], (7000, 10000)),    # 90-200s: Favor higher elixir
            "triple": ([6, 7, 8], (8000, 11000)),       # 200s+: High elixir only, aggressive thresholds
        }

    def start_battle(self):
        self.start_time = time.time()

    def get_elapsed_time(self):
        return time.time() - self.start_time if self.start_time else 0

    def get_battle_phase(self):
        elapsed = self.get_elapsed_time()
        if elapsed < 7: return "early"
        elif elapsed < 90: return "single" 
        elif elapsed < 200: return "double"
        else: return "triple"

    def select_elixir_amount(self):
        phase = self.get_battle_phase()
        elixir_options, _ = self.strategies[phase]
        return random.choice(elixir_options)

    def get_thresholds(self):
        phase = self.get_battle_phase()
        _, thresholds = self.strategies[phase]
        return thresholds


def _fight_loop(emulator, logger: Logger, recording_flag: bool, vision_system=None, debug_visualizer=None) -> bool:
    """Main strategic fight loop with streamlined vision integration."""
    create_default_bridge_iar(emulator)
    cards_at_start = logger.get_cards_played()
    
    battle_strategy = BattleStrategy()
    battle_strategy.start_battle()
    
    # FPS tracking for performance monitoring
    fps_history = deque(maxlen=30)
    frame_count = 0
    last_fps_time = time.perf_counter()
    
    # Vision results storage (to avoid double inference)
    current_vision_results = None
    current_stats = None
    
    # Simple visualization setup
    if vision_system and (debug_visualizer or ENABLE_DEBUG_VISUALIZATION):
        cv2.namedWindow("Fight Vision", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Fight Vision", 419, 633)
        logger.change_status("Fight vision window enabled - press ESC to disable")

    # Get initial battle phase strategy
    elixir_amount = battle_strategy.select_elixir_amount()
    wait_threshold, play_threshold = battle_strategy.get_thresholds()
    logger.change_status(f"Target elixir: {elixir_amount}, thresholds: wait={wait_threshold}, play={play_threshold}")

    print(f'Beginning fight loop')
    while check_for_in_battle_with_delay(emulator):
        if recording_flag:
            save_image(emulator.screenshot())

        # Single inference call per frame (if vision is enabled)
        print(f'Capturing image...')
        screenshot = emulator.screenshot()
        print(f'Captured image!')
        
        if vision_system:
            print(f'Using vision system...')
            # Run inference with timing
            inference_start = time.perf_counter()
            vision_results = vision_system.run_inference(screenshot, screenshot)
            inference_time = (time.perf_counter() - inference_start) * 1000
            print(f'Vision system inference in {inference_time:.2f}ms : {vision_results}')

            # Store results for battle decisions and visualization
            current_vision_results = vision_results
            
            # Calculate FPS
            current_time = time.perf_counter()
            frame_time = current_time - last_fps_time
            fps_history.append(frame_time)
            last_fps_time = current_time
            frame_count += 1
            
            avg_fps = 1.0 / (sum(fps_history) / len(fps_history)) if fps_history else 0
            print(f'Calculated fps as {avg_fps}')
            # Create stats for visualization
            current_stats = get_fight_stats(
                vision_results=vision_results,
                fps=avg_fps,
                inference_time=inference_time,
                tracking_time=getattr(vision_results, 'tracking_time_ms', 0),
                device=get_inference_device(vision_system)
            )

            print(f'These are the current stats: {current_stats}')
            
            # Print formatted output for terminal
            if DEBUG_FIGHT_VISION:
                print(f'Printing debug fight vision results (parsed)')
                formatted_output = format_fight_vision_results(vision_results, "[1v1_fight]")
                if formatted_output:
                    print(formatted_output)
            
            # Simple visualization (single window, efficient)
            if debug_visualizer or ENABLE_DEBUG_VISUALIZATION:
                print(f'Using visualizer for these inference results...')
                viz_frame = draw_fight_results(screenshot, vision_results, current_stats)
                cv2.imshow("Fight Vision", viz_frame)
                

        # Check if we have enough elixir to play
        has_enough_elixir = count_elixer(emulator, elixir_amount)
        
        # Play a card if we have enough elixir OR emergency conditions
        if has_enough_elixir:
            print(f'We have enough elixir for the play')
            if recording_flag:
                save_image(emulator.screenshot())
                
            play_start = time.time()
            if not play_a_card(emulator, logger, recording_flag, battle_strategy, current_vision_results):
                logger.change_status("Card play failed, continuing...")
            else:
                play_time = time.time() - play_start
                logger.change_status(f"Card played in {play_time:.2f}s")
            
            # Select new elixir target for next play
            elixir_amount = battle_strategy.select_elixir_amount()
            wait_threshold, play_threshold = battle_strategy.get_thresholds()
        else:
            print(f'We do not have enough elixir for the play')
        # Safety checks
        if not check_for_in_battle_with_delay(emulator):
            break

    # Cleanup
    try:
        cv2.destroyWindow("Fight Vision")
    except:
        pass
    
    # Simple debug visualizer doesn't need complex cleanup
    
    time.sleep(2)
    cards_played_this_fight = logger.get_cards_played() - cards_at_start
    logger.change_status(f"Fight ended - played {cards_played_this_fight} cards")
    return True


def _random_fight_loop(emulator, logger) -> bool:
    """Simple random card playing for testing/random mode."""
    logger.change_status("Starting random battle")
    start_time = time.time()
    timeout = 300  # 5 minutes

    while check_if_in_battle(emulator) and (time.time() - start_time < timeout):
        mag_dump(emulator, logger)
        
        # Log random number of cards played (1-3)
        for _ in range(random.randint(1, 3)):
            logger.add_card_played()

        time.sleep(8)

    if time.time() - start_time >= timeout:
        logger.change_status("Random fight timed out")
        return False
    
    logger.change_status("Random fight completed")
    return True


def create_enhanced_fight_system():
    """Create a streamlined enhanced fight system with vision and simple debug visualization."""
    vision_system = initialize_vision_system()
    debug_visualizer = initialize_debug_visualizer()
    
    if debug_visualizer:
        print("Streamlined debug visualization enabled - press ESC during fight to disable")
    
    def enhanced_do_fight_state(emulator, logger, random_fight_mode, fight_mode_choosed, 
                               called_from_launching=False, recording_flag=False):
        return do_fight_state(emulator, logger, random_fight_mode, fight_mode_choosed,
                            called_from_launching, recording_flag, vision_system, debug_visualizer)
    
    return enhanced_do_fight_state, vision_system, debug_visualizer


if __name__ == "__main__":
    # Simple integration test
    print("Testing fight vision integration...")
    
    print(f"Configuration:")
    print(f"   Fight vision: {'YES' if ENABLE_FIGHT_VISION else 'NO'}")
    print(f"   Debug visualization: {'YES' if ENABLE_DEBUG_VISUALIZATION else 'NO'}")
    
    # Test vision system
    vision_system = initialize_vision_system()
    if vision_system:
        print("Vision system initialized successfully")
    else:
        print("Vision system failed to initialize")
    
    # Test simple debug visualizer
    debug_visualizer = initialize_debug_visualizer()
    if debug_visualizer:
        print("Simple debug visualizer initialized successfully")
    else:
        print("Debug visualizer disabled")
    
    # Test complete system
    try:
        enhanced_fight, vision, visualizer = create_enhanced_fight_system()
        print("Enhanced fight system created successfully")
        
        # Simple visualizer doesn't need cleanup
            
    except Exception as e:
        print(f"Enhanced system creation failed: {e}")
    
    print("Integration test complete.")
