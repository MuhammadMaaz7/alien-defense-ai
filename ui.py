import pygame
import pygame_gui

def create_ui_manager(window_size):
    return pygame_gui.UIManager(window_size)

def create_info_panel(manager):
    return pygame_gui.elements.UITextBox(
        relative_rect=pygame.Rect((20, 150), (180, 300)),
        html_text="Click a station",
        manager=manager
    )

def update_info_panel(panel, html_text):
    panel.set_text(html_text)
