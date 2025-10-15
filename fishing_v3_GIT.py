import cv2
import numpy as np
import pyautogui
import threading
import mss
import time
from pynput.keyboard import Controller, Key
import pygetwindow as gw
import random


# Ustawienia
x1_game, y1_game, x2_game, y2_game = 654, 247, 900, 443
x1_eq, y1_eq, x2_eq, y2_eq = 2402, 679, 2559, 975
color_to_track = (125, 92, 58) 
pink_to_track = np.array([199, 173, 255])
tolerance = 10

templates = [
            cv2.imread('X', cv2.IMREAD_UNCHANGED),
            cv2.imread('X', cv2.IMREAD_UNCHANGED)]

# Inicjalizacja kontrolera klawiatury
keyboard_controller = Controller()

click_flag = threading.Event()
shared_screenshot = None
shared_screenshot_eq = None
screenshot_lock = threading.Lock()

def grab_screenshot(x1, y1, x2, y2):
    with mss.mss() as sct:
        monitor = {"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1}
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        img_np = img[:, :, :3]
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        return img_np, img_bgr

def activate_window(window_title):
    window = gw.getWindowsWithTitle(window_title)
    if window:
        window[0].activate()
        time.sleep(1)
    else:
        print(f"Nie znaleziono okna o nazwie: {window_title}")

def is_pink_present(img):
    pink_lower_bound = np.array([pink_to_track[0] - tolerance, pink_to_track[1] - tolerance, pink_to_track[2] - tolerance])
    pink_upper_bound = np.array([pink_to_track[0] + tolerance, pink_to_track[1] + tolerance, pink_to_track[2] + tolerance])
    mask_pink = cv2.inRange(img, pink_lower_bound, pink_upper_bound)
    return np.any(mask_pink)

def template_matching(img, templates):
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)  # Konwertuje obraz RGBA na BGR
    best_match = None
    best_position = None
    best_img_with_template = None
    best_score = 0

    for template in templates:
        template_bgr = cv2.cvtColor(template, cv2.COLOR_RGBA2BGR)  # Konwertuje szablon RGBA na BGR

        # Dopasowanie szablonu
        result = cv2.matchTemplate(img_bgr, template_bgr, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        threshold = 0.8
        if max_val >= threshold:
            top_left = max_loc
            h, w, _ = template_bgr.shape
            bottom_right = (top_left[0] + w, top_left[1] + h)
            img_with_template = img_bgr.copy()
            cv2.rectangle(img_with_template, top_left, bottom_right, (0, 255, 0), 2)  # Zielony kontur

            # Sprawdź, czy znalezione dopasowanie jest najlepsze
            if max_val > best_score:
                best_match = (top_left, bottom_right)
                best_position = top_left
                best_img_with_template = img_with_template
                best_score = max_val

    if best_match:
        return True, best_position, best_img_with_template
    return False, None, img_bgr


def monitor_color():
    global shared_screenshot
    while True:
        with screenshot_lock:
            if shared_screenshot is None:
                continue
            img = shared_screenshot.copy()

        if is_pink_present(img):
            click_flag.set()
        else:
            click_flag.clear()

def move_mouse(cx, cy):
    pyautogui.moveTo(cx, cy)
    if click_flag.is_set():
        pyautogui.click(clicks=2)

def find_color_in_screen():
    global shared_screenshot
    lower_bound = np.array([color_to_track[0] - tolerance, color_to_track[1] - tolerance, color_to_track[2] - tolerance])
    upper_bound = np.array([color_to_track[0] + tolerance, color_to_track[1] + tolerance, color_to_track[2] + tolerance])

    previous_position = None

    while True:
        img_np, img_gbr = grab_screenshot(x1_game, y1_game, x2_game, y2_game)
        with screenshot_lock:
            shared_screenshot = img_np.copy()

        # if not isinstance(img_gbr, np.ndarray) or img.ndim != 3 or img.shape[2] != 3:
        #     print("Obraz wejściowy ma nieprawidłowy format.")
        #     continue
        #  # Sprawdź rozmiary lower_bound i upper_bound
        # if lower_bound.shape[0] != img.shape[2] or upper_bound.shape[0] != img.shape[2]:
        #     print("Rozmiary lower_bound i upper_bound są niezgodne z obrazem.")
        #     continue

        mask = cv2.inRange(img_np, lower_bound, upper_bound)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]  # Przetwarzaj tylko największy kontur

        if contours:
            contour = contours[0]
            if cv2.contourArea(contour) > 100:
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"]) + x1_game
                    cy = int(M["m01"] / M["m00"]) + y1_game

                    if previous_position:
                        predicted_cx = 2 * cx - previous_position[0]
                        predicted_cy = 2 * cy - previous_position[1]
                        move_mouse(predicted_cx, predicted_cy)
                    else:
                        move_mouse(cx, cy)

                    previous_position = (cx, cy)

        time.sleep(0.01)  # Kontrolowanie prędkości pętli

def click_and_drag():
    # Pobieranie rozmiarów ekranu
    screen_width, screen_height = pyautogui.size()
    
    # Środek ekranu
    center_x, center_y = screen_width // 2, screen_height // 2
    
    # Kliknięcie w środek i przeciągnięcie w lewo z prawym przyciskiem myszy
    pyautogui.moveTo(center_x, center_y)
    pyautogui.mouseDown(button='right')
    pyautogui.moveTo(center_x - 50, center_y, duration=0.5)  # Przeciąganie w lewo o 200 pikseli
    pyautogui.mouseUp(button='right')

def perform_periodic_action():
    """Wykonuje akcję co 17-20 sekund, sprawdzając przedmiot brązowy przed naciśnięciem klawisza."""
    i = 1
    
    while True:
        if i <= 1600:
            random_duration = random.uniform(17, 20)
            time.sleep(random_duration)  # Czekaj losowo od 17 do 20 sekund

            _, img_eq = grab_screenshot(x1_eq, y1_eq, x2_eq, y2_eq)
            template_found, template_position, _ = template_matching(img_eq, templates)

            click_and_drag()

            if template_found:
                print(f"Szablon znaleziony na pozycji: {template_position}")
                # Przemieszczenie myszy i kliknięcie w znaleziony obiekt
                pyautogui.moveTo(template_position[0] + x1_eq+5, template_position[1] + y1_eq+5)
                pyautogui.click(button='right')
                keyboard_controller.release('1')
                time.sleep(0.2)  # Krótkie opóźnienie
                keyboard_controller.press(Key.space)
                time.sleep(0.5)
                keyboard_controller.release(Key.space)
                time.sleep(0.2)  # Krótkie opóźnienie
            else:
                # Jeśli brązowy przedmiot nie został znaleziony, kontynuuj z normalną akcją klawiszy
                if i <= 200:
                    keyboard_controller.press('1')
                    time.sleep(0.5)
                    keyboard_controller.release('1')
                    time.sleep(0.2)  # Krótkie opóźnienie
                    keyboard_controller.press(Key.space)
                    time.sleep(0.5)
                    keyboard_controller.release(Key.space)
                    time.sleep(0.2)  # Krótkie opóźnienie
                    i += 1
                    print(i)
                elif i > 200 and i <= 400:
                    keyboard_controller.press('2')
                    time.sleep(0.5)
                    keyboard_controller.release('2')
                    time.sleep(0.2)  # Krótkie opóźnienie
                    keyboard_controller.press(Key.space)
                    time.sleep(0.5)
                    keyboard_controller.release(Key.space)
                    time.sleep(0.2)  # Krótkie opóźnienie
                    i += 1
                    print(i)
                elif i > 400 and i <= 600:
                    keyboard_controller.press('3')
                    time.sleep(0.5)
                    keyboard_controller.release('3')
                    time.sleep(0.2)  # Krótkie opóźnienie
                    keyboard_controller.press(Key.space)
                    time.sleep(0.5)
                    keyboard_controller.release(Key.space)
                    time.sleep(0.2)  # Krótkie opóźnienie
                    i += 1
                    print(i)
                elif i > 600 and i <= 800:
                    keyboard_controller.press('4')
                    time.sleep(0.5)
                    keyboard_controller.release('4')
                    time.sleep(0.2)  # Krótkie opóźnienie
                    keyboard_controller.press(Key.space)
                    time.sleep(0.5)
                    keyboard_controller.release(Key.space)
                    time.sleep(0.2)  # Krótkie opóźnienie
                    i += 1
                    print(i)
                elif i > 800 and i <= 1000:
                    keyboard_controller.press(Key.f1)
                    time.sleep(0.5)
                    keyboard_controller.release(Key.f1)
                    time.sleep(0.2)  # Krótkie opóźnienie
                    keyboard_controller.press(Key.space)
                    time.sleep(0.5)
                    keyboard_controller.release(Key.space)
                    time.sleep(0.2)  # Krótkie opóźnienie
                    i += 1
                    print(i)
                elif i > 1000 and i <= 1200:
                    keyboard_controller.press(Key.f2)
                    time.sleep(0.5)
                    keyboard_controller.release(Key.f2)
                    time.sleep(0.2)  # Krótkie opóźnienie
                    keyboard_controller.press(Key.space)
                    time.sleep(0.5)
                    keyboard_controller.release(Key.space)
                    time.sleep(0.2)  # Krótkie opóźnienie
                    i += 1
                    print(i)
                elif i > 1200 and i <= 1400:
                    keyboard_controller.press(Key.f3)
                    time.sleep(0.5)
                    keyboard_controller.release(Key.f3)
                    time.sleep(0.2)  # Krótkie opóźnienie
                    keyboard_controller.press(Key.space)
                    time.sleep(0.5)
                    keyboard_controller.release(Key.space)
                    time.sleep(0.2)  # Krótkie opóźnienie
                    i += 1
                    print(i)
                else:
                    keyboard_controller.press(Key.f4)
                    time.sleep(0.5)
                    keyboard_controller.release(Key.f4)
                    time.sleep(0.2)  # Krótkie opóźnienie
                    keyboard_controller.press(Key.space)
                    time.sleep(0.5)
                    keyboard_controller.release(Key.space)
                    time.sleep(0.2)  # Krótkie opóźnienie
                    i += 1
                    print(i)
        else:
            break



if __name__ == "__main__":
    window_title = "GAME"
    activate_window(window_title)
    
    # Uruchomienie wątku do monitorowania koloru
    color_thread = threading.Thread(target=monitor_color, daemon=True)
    color_thread.start()

    # Uruchomienie wątku do wykonywania okresowych akcji
    periodic_action_thread = threading.Thread(target=perform_periodic_action, daemon=True)
    periodic_action_thread.start()

    # Główna funkcja do śledzenia koloru i sterowania myszą
    find_color_in_screen()
