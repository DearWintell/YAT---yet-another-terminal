import sys
from PyQt6.QtWidgets import QApplication, QWidget, QTabWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QLineEdit
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPainter, QColor, QFontMetrics, QClipboard
import pyte
from yat.backend import YATBackend

PALETTE = {
    'bg':             QColor('#090909'),
    'bg_elevated':    QColor('#0f0f0f'),
    'border':         QColor('#27272a'),
    'text_primary':   QColor('#fafafa'),
    'text_secondary': QColor('#a1a1aa'),
    'text_muted':     QColor('#52525b'),
    'accent':         QColor('#fafafa'),
    'terminal_bg':    QColor('#0a0a0a'),
    'terminal_fg':    QColor('#e4e4e7'),
    'scroll_indicator': QColor('#3b82f6'),
    'selection_bg':   QColor('#264f78'),  # Цвет выделения (как в VS Code)
}

ANSI_COLORS = {
    'black':   QColor('#27272a'),
    'red':     QColor('#ef4444'),
    'green':   QColor('#22c55e'),
    'yellow':  QColor('#eab308'),
    'blue':    QColor('#3b82f6'),
    'magenta': QColor('#a855f7'),
    'cyan':    QColor('#06b6d4'),
    'white':   QColor('#e4e4e7'),
    'default_fg': QColor('#e4e4e7'),
    'default_bg': QColor('#0a0a0a'),
}


class TerminalWorker(QThread):
    data_ready = pyqtSignal(str)

    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        self.running = True

    def run(self):
        while self.running and self.backend.is_alive():
            data = self.backend.read()
            if data:
                self.data_ready.emit(data)
            self.msleep(10)


class Separator(QFrame):
    def __init__(self, parent=None, vertical=False):
        super().__init__(parent)
        if vertical:
            self.setFixedWidth(1)
            self.setMinimumHeight(100)
            self.setStyleSheet(f"background-color: {PALETTE['border'].name()};")
        else:
            self.setFixedHeight(1)
            self.setStyleSheet(f"background-color: {PALETTE['border'].name()};")


class BlinkingCursor(QLabel):
    def __init__(self, parent=None):
        super().__init__("█", parent)
        self.setFont(QFont("JetBrains Mono", 28, QFont.Weight.Bold))
        self.setStyleSheet(f"color: {PALETTE['text_primary'].name()};")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.toggle)
        self.timer.start(600)
        self.visible = True
    
    def toggle(self):
        self.visible = not self.visible
        self.setVisible(self.visible)


class WelcomeWidget(QWidget):
    def __init__(self, on_start_callback):
        super().__init__()
        self.on_start = on_start_callback
        self.setStyleSheet(f"background-color: {PALETTE['bg'].name()};")
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        header = QWidget()
        header.setStyleSheet(f"background-color: {PALETTE['bg'].name()};")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(40, 24, 40, 24)
        
        logo = QLabel("yat")
        logo.setFont(QFont("JetBrains Mono", 13, QFont.Weight.Bold))
        logo.setStyleSheet(f"color: {PALETTE['text_primary'].name()};")
        header_layout.addWidget(logo)
        
        header_layout.addStretch()
        
        status = QLabel("● ready")
        status.setFont(QFont("JetBrains Mono", 11))
        status.setStyleSheet(f"color: {PALETTE['text_muted'].name()};")
        header_layout.addWidget(status)
        
        header.setLayout(header_layout)
        main_layout.addWidget(header)
        main_layout.addWidget(Separator())
        
        content = QWidget()
        content.setStyleSheet(f"background-color: {PALETTE['bg'].name()};")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(40, 60, 40, 60)
        content_layout.setSpacing(0)
        
        title_row = QHBoxLayout()
        title_row.setSpacing(4)
        
        title = QLabel("yet another terminal")
        title.setFont(QFont("JetBrains Mono", 32, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {PALETTE['text_primary'].name()};")
        title_row.addWidget(title)
        
        cursor = BlinkingCursor()
        title_row.addWidget(cursor)
        
        title_row.addStretch()
        content_layout.addLayout(title_row)
        
        content_layout.addSpacing(16)
        
        subtitle = QLabel("минималистичный терминал для разработчиков")
        subtitle.setFont(QFont("JetBrains Mono", 13))
        subtitle.setStyleSheet(f"color: {PALETTE['text_secondary'].name()};")
        content_layout.addWidget(subtitle)
        
        content_layout.addSpacing(48)
        
        two_col = QHBoxLayout()
        two_col.setSpacing(60)
        
        left_col = QVBoxLayout()
        left_col.setSpacing(16)
        
        section_label = QLabel("// о проекте")
        section_label.setFont(QFont("JetBrains Mono", 10))
        section_label.setStyleSheet(f"color: {PALETTE['text_muted'].name()};")
        left_col.addWidget(section_label)
        
        desc_lines = [
            "• поддержка вкладок",
            "• ANSI-цвета",
            "• горячие клавиши",
            "• ресайз на лету",
            "• python 3.14",
        ]
        for line in desc_lines:
            lbl = QLabel(line)
            lbl.setFont(QFont("JetBrains Mono", 12))
            lbl.setStyleSheet(f"color: {PALETTE['text_secondary'].name()};")
            left_col.addWidget(lbl)
        
        left_col.addStretch()
        two_col.addLayout(left_col, 1)
        
        two_col.addWidget(Separator(vertical=True))
        
        right_col = QVBoxLayout()
        right_col.setSpacing(16)
        
        cmd_label = QLabel("// горячие клавиши")
        cmd_label.setFont(QFont("JetBrains Mono", 10))
        cmd_label.setStyleSheet(f"color: {PALETTE['text_muted'].name()};")
        right_col.addWidget(cmd_label)
        
        commands = [
            ("ctrl+t", "новая вкладка"),
            ("ctrl+w", "закрыть вкладку"),
            ("ctrl+l", "очистить экран"),
            ("↑↓", "история команд"),
        ]
        
        for key, desc_text in commands:
            cmd_row = QHBoxLayout()
            cmd_row.setSpacing(12)
            
            prompt = QLabel("›")
            prompt.setFont(QFont("JetBrains Mono", 12))
            prompt.setStyleSheet(f"color: {PALETTE['text_muted'].name()};")
            cmd_row.addWidget(prompt)
            
            key_lbl = QLabel(key)
            key_lbl.setFont(QFont("JetBrains Mono", 11, QFont.Weight.Bold))
            key_lbl.setStyleSheet(f"color: {PALETTE['text_primary'].name()};")
            cmd_row.addWidget(key_lbl)
            
            desc_lbl = QLabel(desc_text)
            desc_lbl.setFont(QFont("JetBrains Mono", 11))
            desc_lbl.setStyleSheet(f"color: {PALETTE['text_secondary'].name()};")
            cmd_row.addWidget(desc_lbl)
            
            cmd_row.addStretch()
            right_col.addLayout(cmd_row)
        
        right_col.addStretch()
        two_col.addLayout(right_col, 1)
        
        content_layout.addLayout(two_col)
        
        content_layout.addSpacing(48)
        content_layout.addWidget(Separator())
        content_layout.addSpacing(32)
        
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(16)
        
        start_btn = QPushButton("начать →")
        start_btn.setFont(QFont("JetBrains Mono", 13, QFont.Weight.Bold))
        start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {PALETTE['text_primary'].name()};
                border: none;
                padding: 8px 0;
            }}
            QPushButton:hover {{
                color: {PALETTE['text_secondary'].name()};
            }}
        """)
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.clicked.connect(self.on_start)
        bottom_row.addWidget(start_btn)
        
        bottom_row.addSpacing(24)
        
        hint = QLabel("или нажми любую клавишу")
        hint.setFont(QFont("JetBrains Mono", 11))
        hint.setStyleSheet(f"color: {PALETTE['text_muted'].name()};")
        bottom_row.addWidget(hint)
        
        bottom_row.addStretch()
        content_layout.addLayout(bottom_row)
        
        content.setLayout(content_layout)
        main_layout.addWidget(content)
        
        main_layout.addWidget(Separator())
        footer = QWidget()
        footer.setStyleSheet(f"background-color: {PALETTE['bg'].name()};")
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(40, 14, 40, 14)
        
        left_status = QLabel("⌘ yat v0.4.0")
        left_status.setFont(QFont("JetBrains Mono", 10))
        left_status.setStyleSheet(f"color: {PALETTE['text_muted'].name()};")
        footer_layout.addWidget(left_status)
        
        footer_layout.addStretch()
        
        right_status = QLabel("python 3.14.5  ·  pywinpty  ·  pyqt6")
        right_status.setFont(QFont("JetBrains Mono", 10))
        right_status.setStyleSheet(f"color: {PALETTE['text_muted'].name()};")
        footer_layout.addWidget(right_status)
        
        footer.setLayout(footer_layout)
        main_layout.addWidget(footer)
        
        self.setLayout(main_layout)
    
    def keyPressEvent(self, event):
        self.on_start()


class TerminalWidget(QWidget):
    def __init__(self, tab_index=0):
        super().__init__()
        self.tab_index = tab_index
        self.font = QFont("JetBrains Mono", 12)
        self.fm = QFontMetrics(self.font)
        self.char_w = self.fm.boundingRect("W").width()
        self.char_h = self.fm.height()
        
        self.screen = None
        self.stream = None
        self.backend = None
        self.worker = None
        self.cols = 0
        self.rows = 0
        
        # Скролл
        self.scroll_offset = 0
        self.max_scroll = 0
        self.is_scrolling = False
        
        # Выделение
        self.selection_start = None  # (row, col)
        self.selection_end = None    # (row, col)
        self.is_selecting = False
        self.last_click_time = 0
        self.last_click_pos = None
        
        self.shift_pressed = False
        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setStyleSheet(f"background-color: {PALETTE['terminal_bg'].name()};")
        self.setMinimumSize(400, 300)
        self.setMouseTracking(True)  # Для отслеживания перетаскивания

    def init_terminal(self, cols, rows):
        if self.backend is not None:
            return
        
        self.cols = cols
        self.rows = rows
        
        self.screen = pyte.HistoryScreen(self.cols, self.rows, history=10000)
        self.stream = pyte.Stream(self.screen)
        self.backend = YATBackend(self.cols, self.rows)
        
        self.worker = TerminalWorker(self.backend)
        self.worker.data_ready.connect(self.feed_data)
        self.worker.start()

    def update_terminal_size(self):
        width = self.width()
        height = self.height()
        
        if width > 0 and height > 0:
            new_cols = max(20, width // self.char_w)
            new_rows = max(10, height // self.char_h)
            
            if self.backend is None:
                self.init_terminal(new_cols, new_rows)
            elif new_cols != self.cols or new_rows != self.rows:
                self.cols = new_cols
                self.rows = new_rows
                self.screen.resize(self.cols, self.rows)
                self.backend.resize(self.cols, self.rows)

    def feed_data(self, data):
        self.stream.feed(data)
        if self.scroll_offset > 0:
            self.scroll_offset = 0
            self.is_scrolling = False
        self.update()

    def scroll_up(self, lines=1):
        if self.screen is None:
            return
        history_len = len(self.screen.history.top)
        if history_len > 0:
            self.scroll_offset = min(self.scroll_offset + lines, history_len)
            self.is_scrolling = self.scroll_offset > 0
            self.update()

    def scroll_down(self, lines=1):
        if self.scroll_offset > 0:
            self.scroll_offset = max(self.scroll_offset - lines, 0)
            self.is_scrolling = self.scroll_offset > 0
            self.update()

    def scroll_to_bottom(self):
        if self.scroll_offset > 0:
            self.scroll_offset = 0
            self.is_scrolling = False
            self.update()

    # === ВЫДЕЛЕНИЕ МЫШЬЮ ===
    
    def pixel_to_cell(self, x, y):
        """Переводит пиксельные координаты в координаты ячейки (row, col)."""
        col = x // self.char_w
        row = y // self.char_h
        return max(0, row), max(0, col)
    
    def get_cell_text(self, row, col):
        """Получает символ из буфера по координатам."""
        if self.screen is None:
            return ' '
        if row in self.screen.buffer:
            line = self.screen.buffer[row]
            if col in line:
                ch = line[col].data
                return ch if ch != '\x00' else ' '
        return ' '
    
    def is_word_char(self, ch):
        """Определяет, является ли символ частью слова."""
        return ch.isalnum() or ch == '_'
    
    def select_word(self, row, col):
        """Выделяет слово под курсором (двойной клик)."""
        if self.screen is None:
            return
        
        line = self.screen.buffer.get(row)
        if not line:
            return
        
        # Находим начало слова
        start_col = col
        while start_col > 0:
            ch = self.get_cell_text(row, start_col - 1)
            if not self.is_word_char(ch):
                break
            start_col -= 1
        
        # Находим конец слова
        end_col = col
        while end_col < self.cols - 1:
            ch = self.get_cell_text(row, end_col)
            if not self.is_word_char(ch):
                break
            end_col += 1
        
        self.selection_start = (row, start_col)
        self.selection_end = (row, end_col - 1)
        self.update()
    
    def select_line(self, row):
        """Выделяет всю строку (тройной клик)."""
        self.selection_start = (row, 0)
        self.selection_end = (row, self.cols - 1)
        self.update()
    
    def mousePressEvent(self, event):
        """Обработка клика мыши."""
        if self.backend is None:
            return
        
        x, y = event.position().x(), event.position().y()
        row, col = self.pixel_to_cell(x, y)
        
        # Проверяем двойной/тройной клик
        import time
        current_time = time.time()
        is_double = (current_time - self.last_click_time < 0.3 and 
                     self.last_click_pos == (row, col))
        is_triple = False
        
        if is_double and hasattr(self, '_last_double_time'):
            if current_time - self._last_double_time < 0.3:
                is_triple = True
        
        if is_triple:
            # Тройной клик - выделить строку
            self.select_line(row)
            self._last_double_time = 0
        elif is_double:
            # Двойной клик - выделить слово
            self.select_word(row, col)
            self._last_double_time = current_time
        else:
            # Одиночный клик - начать выделение или просто переместить курсор
            self.selection_start = (row, col)
            self.selection_end = (row, col)
            self.is_selecting = True
        
        self.last_click_time = current_time
        self.last_click_pos = (row, col)
        self.update()
    
    def mouseMoveEvent(self, event):
        """Обработка перетаскивания мыши для выделения."""
        if not self.is_selecting or self.backend is None:
            return
        
        x, y = event.position().x(), event.position().y()
        row, col = self.pixel_to_cell(x, y)
        
        self.selection_end = (row, col)
        self.update()
    
    def mouseReleaseEvent(self, event):
        """Завершение выделения."""
        self.is_selecting = False
    
    def get_selected_text(self):
        """Получает выделенный текст."""
        if not self.selection_start or not self.selection_end:
            return ""
        
        start_row, start_col = self.selection_start
        end_row, end_col = self.selection_end
        
        # Нормализуем (start должен быть перед end)
        if (start_row, start_col) > (end_row, end_col):
            start_row, start_col, end_row, end_col = end_row, end_col, start_row, start_col
        
        text = ""
        for row in range(start_row, end_row + 1):
            line_start = start_col if row == start_row else 0
            line_end = end_col if row == end_row else self.cols - 1
            
            for col in range(line_start, line_end + 1):
                text += self.get_cell_text(row, col)
            
            if row < end_row:
                text += "\n"
        
        return text
    
    def copy_selection(self):
        """Копирует выделенный текст в буфер обмена."""
        text = self.get_selected_text()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            # Сбрасываем выделение после копирования
            self.selection_start = None
            self.selection_end = None
            self.update()
    
    def paste_text(self):
        """Вставляет текст из буфера обмена."""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text and self.backend:
            self.backend.write(text)
    
    def wheelEvent(self, event):
        """Обработка колеса мыши."""
        if self.backend is None:
            return
        delta = event.angleDelta().y()
        if delta > 0:
            self.scroll_up(3)
        elif delta < 0:
            self.scroll_down(3)
        event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(100, self.update_terminal_size)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(200, self.update_terminal_size)

    def is_cell_selected(self, row, col):
        """Проверяет, выделена ли ячейка."""
        if not self.selection_start or not self.selection_end:
            return False
        
        start_row, start_col = self.selection_start
        end_row, end_col = self.selection_end
        
        # Нормализуем
        if (start_row, start_col) > (end_row, end_col):
            start_row, start_col, end_row, end_col = end_row, end_col, start_row, start_col
        
        if row < start_row or row > end_row:
            return False
        if row == start_row and col < start_col:
            return False
        if row == end_row and col > end_col:
            return False
        return True

    def paintEvent(self, event):
        if self.screen is None:
            painter = QPainter(self)
            painter.setFont(self.font)
            painter.fillRect(self.rect(), PALETTE['terminal_bg'])
            painter.setPen(PALETTE['terminal_fg'])
            painter.drawText(10, 30, "initializing...")
            return
        
        painter = QPainter(self)
        painter.setFont(self.font)
        painter.fillRect(self.rect(), PALETTE['terminal_bg'])
        
        if self.scroll_offset > 0 and hasattr(self.screen, 'history'):
            history_lines = list(self.screen.history.top)
            visible_history = history_lines[-self.scroll_offset:] if self.scroll_offset <= len(history_lines) else history_lines
            
            for i, line in enumerate(visible_history):
                y = i
                py = (y + 1) * self.char_h
                if py > self.height():
                    break
                
                for x, char in line.items():
                    if x >= self.cols:
                        continue
                    px = x * self.char_w
                    
                    selected = self.is_cell_selected(y, x)
                    
                    if selected:
                        painter.fillRect(px, py - self.char_h, self.char_w, self.char_h, PALETTE['selection_bg'])
                    elif char.bg != 'default':
                        bg_color = ANSI_COLORS.get(char.bg, PALETTE['terminal_bg'])
                        painter.fillRect(px, py - self.char_h, self.char_w, self.char_h, bg_color)
                    
                    fg_color = ANSI_COLORS.get(char.fg, PALETTE['terminal_fg'])
                    painter.setPen(fg_color)
                    
                    ch = char.data if char.data != '\x00' else ' '
                    painter.drawText(px, py, ch)
            
            buffer_start_y = len(visible_history)
            for y, line in self.screen.buffer.items():
                actual_y = buffer_start_y + y
                py = (actual_y + 1) * self.char_h
                if py > self.height():
                    break
                
                for x, char in line.items():
                    if x >= self.cols:
                        continue
                    px = x * self.char_w
                    
                    selected = self.is_cell_selected(actual_y, x)
                    
                    if selected:
                        painter.fillRect(px, py - self.char_h, self.char_w, self.char_h, PALETTE['selection_bg'])
                    elif char.bg != 'default':
                        bg_color = ANSI_COLORS.get(char.bg, PALETTE['terminal_bg'])
                        painter.fillRect(px, py - self.char_h, self.char_w, self.char_h, bg_color)
                    
                    fg_color = ANSI_COLORS.get(char.fg, PALETTE['terminal_fg'])
                    painter.setPen(fg_color)
                    
                    ch = char.data if char.data != '\x00' else ' '
                    painter.drawText(px, py, ch)
        else:
            for y, line in self.screen.buffer.items():
                if y >= self.rows:
                    continue
                py = (y + 1) * self.char_h
                
                for x, char in line.items():
                    if x >= self.cols:
                        continue
                    px = x * self.char_w
                    
                    selected = self.is_cell_selected(y, x)
                    
                    if selected:
                        painter.fillRect(px, py - self.char_h, self.char_w, self.char_h, PALETTE['selection_bg'])
                    elif char.bg != 'default':
                        bg_color = ANSI_COLORS.get(char.bg, PALETTE['terminal_bg'])
                        painter.fillRect(px, py - self.char_h, self.char_w, self.char_h, bg_color)
                    
                    fg_color = ANSI_COLORS.get(char.fg, PALETTE['terminal_fg'])
                    painter.setPen(fg_color)
                    
                    ch = char.data if char.data != '\x00' else ' '
                    painter.drawText(px, py, ch)
        
        if self.is_scrolling and hasattr(self.screen, 'history'):
            history_len = len(self.screen.history.top)
            if history_len > 0:
                scroll_percent = self.scroll_offset / history_len
                bar_height = max(20, int(self.height() * 0.3))
                bar_y = int((self.height() - bar_height) * (1 - scroll_percent))
                bar_x = self.width() - 6
                painter.fillRect(bar_x, bar_y, 3, bar_height, PALETTE['scroll_indicator'])

    def keyPressEvent(self, event):
        if self.backend is None:
            return
        
        if event.key() == Qt.Key.Key_Shift:
            self.shift_pressed = True
            return
        
        modifiers = event.modifiers()
        is_shift = bool(modifiers & Qt.KeyboardModifier.ShiftModifier)
        is_ctrl = bool(modifiers & Qt.KeyboardModifier.ControlModifier)
        
        # Ctrl+C - копирование или прерывание
        if is_ctrl and event.key() == Qt.Key.Key_C:
            if self.selection_start and self.selection_end:
                self.copy_selection()
            else:
                # Отправляем Ctrl+C в терминал (прерывание)
                self.backend.write('\x03')
            event.accept()
            return
        
        # Ctrl+V - вставка
        if is_ctrl and event.key() == Qt.Key.Key_V:
            self.paste_text()
            event.accept()
            return
        
        # Ctrl+Shift+C/V - альтернативное копирование/вставка
        if is_ctrl and is_shift:
            if event.key() == Qt.Key.Key_C:
                self.copy_selection()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_V:
                self.paste_text()
                event.accept()
                return
        
        # Глобальные горячие клавиши (только Ctrl, без Shift)
        if modifiers == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_T:
                self.window().add_new_tab()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_W:
                self.window().close_current_tab()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_L:
                self.clear_screen()
                event.accept()
                return
        
        # Page Up / Page Down - скролл
        if event.key() == Qt.Key.Key_PageUp:
            self.scroll_up(self.rows)
            event.accept()
            return
        elif event.key() == Qt.Key.Key_PageDown:
            self.scroll_down(self.rows)
            event.accept()
            return
        
        if is_shift:
            if event.key() == Qt.Key.Key_PageUp:
                self.scroll_up(self.rows)
                event.accept()
                return
            elif event.key() == Qt.Key.Key_PageDown:
                self.scroll_down(self.rows)
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Up:
                self.scroll_up(1)
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Down:
                self.scroll_down(1)
                event.accept()
                return
        
        if modifiers == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_Up:
                self.scroll_up(1)
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Down:
                self.scroll_down(1)
                event.accept()
                return
        
        if self.is_scrolling and event.key() not in (
            Qt.Key.Key_PageUp, Qt.Key.Key_PageDown,
            Qt.Key.Key_Up, Qt.Key.Key_Down,
            Qt.Key.Key_Home, Qt.Key.Key_End,
        ):
            self.scroll_to_bottom()
        
        special_keys = {
            Qt.Key.Key_Up: '\x1b[A',
            Qt.Key.Key_Down: '\x1b[B',
            Qt.Key.Key_Right: '\x1b[C',
            Qt.Key.Key_Left: '\x1b[D',
            Qt.Key.Key_Home: '\x1b[H',
            Qt.Key.Key_End: '\x1b[F',
            Qt.Key.Key_Delete: '\x1b[3~',
            Qt.Key.Key_Backspace: '\x7f',
            Qt.Key.Key_Enter: '\r',
            Qt.Key.Key_Return: '\r',
            Qt.Key.Key_Tab: '\t',
            Qt.Key.Key_Escape: '\x1b',
        }
        
        if event.key() in special_keys:
            self.backend.write(special_keys[event.key()])
            event.accept()
            return
        
        text = event.text()
        if text and len(text) == 1 and text.isprintable():
            self.backend.write(text)
            event.accept()
            return
        
        char = self.qt_key_to_char(event.key(), is_shift)
        if char:
            self.backend.write(char)
            event.accept()
            return
        
        event.accept()

    def qt_key_to_char(self, key, shift=False):
        if Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
            letter = chr(key - Qt.Key.Key_A + ord('a'))
            return letter.upper() if shift else letter
        
        digit_map = {
            Qt.Key.Key_0: ('0', ')'),
            Qt.Key.Key_1: ('1', '!'),
            Qt.Key.Key_2: ('2', '@'),
            Qt.Key.Key_3: ('3', '#'),
            Qt.Key.Key_4: ('4', '$'),
            Qt.Key.Key_5: ('5', '%'),
            Qt.Key.Key_6: ('6', '^'),
            Qt.Key.Key_7: ('7', '&'),
            Qt.Key.Key_8: ('8', '*'),
            Qt.Key.Key_9: ('9', '('),
        }
        if key in digit_map:
            normal, shifted = digit_map[key]
            return shifted if shift else normal
        
        symbol_map = {
            Qt.Key.Key_Minus: ('-', '_'),
            Qt.Key.Key_Plus: ('+', '+'),
            Qt.Key.Key_Equal: ('=', '+'),
            Qt.Key.Key_BracketLeft: ('[', '{'),
            Qt.Key.Key_BracketRight: (']', '}'),
            Qt.Key.Key_Semicolon: (';', ':'),
            Qt.Key.Key_Apostrophe: ("'", '"'),
            Qt.Key.Key_Comma: (',', '<'),
            Qt.Key.Key_Period: ('.', '>'),
            Qt.Key.Key_Slash: ('/', '?'),
            Qt.Key.Key_Backslash: ('\\', '|'),
            Qt.Key.Key_Space: (' ', ' '),
            Qt.Key.Key_QuoteDbl: ('"', '"'),
        }
        
        if key in symbol_map:
            normal, shifted = symbol_map[key]
            return shifted if shift else normal
        
        return None

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Shift:
            self.shift_pressed = False

    def clear_screen(self):
        self.backend.write('\x1b[2J\x1b[H')
        self.scroll_to_bottom()

    def closeEvent(self, event):
        if self.worker:
            self.worker.running = False
            self.worker.wait()
        if self.backend:
            self.backend.close()
        super().closeEvent(event)


class YATMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.tab_counter = 0
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("yat")
        self.resize(1100, 750)
        self.setStyleSheet(f"background-color: {PALETTE['bg'].name()};")
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.welcome_widget = WelcomeWidget(self.show_terminal)
        self.main_layout.addWidget(self.welcome_widget)
        
        self.terminal_container = QWidget()
        self.terminal_container.setStyleSheet(f"background-color: {PALETTE['bg'].name()};")
        terminal_layout = QVBoxLayout()
        terminal_layout.setContentsMargins(0, 0, 0, 0)
        terminal_layout.setSpacing(0)
        
        tabs_header = QWidget()
        tabs_header.setStyleSheet(f"""
            QWidget {{
                background-color: {PALETTE['bg_elevated'].name()};
                border-bottom: 1px solid {PALETTE['border'].name()};
            }}
        """)
        tabs_layout = QHBoxLayout()
        tabs_layout.setContentsMargins(16, 8, 16, 8)
        tabs_layout.setSpacing(8)
        
        self.btn_new_tab = QPushButton("+")
        self.btn_new_tab.setFont(QFont("JetBrains Mono", 11))
        self.btn_new_tab.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {PALETTE['text_muted'].name()};
                border: 1px solid {PALETTE['border'].name()};
                padding: 4px 12px;
            }}
            QPushButton:hover {{
                color: {PALETTE['text_primary'].name()};
                border-color: {PALETTE['text_muted'].name()};
            }}
        """)
        self.btn_new_tab.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new_tab.clicked.connect(self.add_new_tab)
        tabs_layout.addWidget(self.btn_new_tab)
        
        tabs_layout.addStretch()
        
        mode_label = QLabel("terminal")
        mode_label.setFont(QFont("JetBrains Mono", 10))
        mode_label.setStyleSheet(f"color: {PALETTE['text_muted'].name()};")
        tabs_layout.addWidget(mode_label)
        
        tabs_header.setLayout(tabs_layout)
        terminal_layout.addWidget(tabs_header)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: {PALETTE['terminal_bg'].name()};
            }}
            QTabBar::tab {{
                background-color: {PALETTE['bg'].name()};
                color: {PALETTE['text_muted'].name()};
                padding: 8px 16px;
                margin-right: 1px;
                border: none;
                border-bottom: 2px solid transparent;
                font-family: 'JetBrains Mono';
                font-size: 11px;
            }}
            QTabBar::tab:selected {{
                color: {PALETTE['text_primary'].name()};
                border-bottom: 2px solid {PALETTE['accent'].name()};
            }}
            QTabBar::tab:hover {{
                color: {PALETTE['text_secondary'].name()};
            }}
        """)
        
        terminal_layout.addWidget(self.tab_widget)
        
        status_bar = QWidget()
        status_bar.setStyleSheet(f"""
            QWidget {{
                background-color: {PALETTE['bg_elevated'].name()};
                border-top: 1px solid {PALETTE['border'].name()};
            }}
        """)
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(16, 6, 16, 6)
        
        self.status_left = QLabel(" yat")
        self.status_left.setFont(QFont("JetBrains Mono", 10))
        self.status_left.setStyleSheet(f"color: {PALETTE['text_muted'].name()};")
        status_layout.addWidget(self.status_left)
        
        status_layout.addStretch()
        
        self.status_right = QLabel("powershell")
        self.status_right.setFont(QFont("JetBrains Mono", 10))
        self.status_right.setStyleSheet(f"color: {PALETTE['text_muted'].name()};")
        status_layout.addWidget(self.status_right)
        
        status_bar.setLayout(status_layout)
        terminal_layout.addWidget(status_bar)
        
        self.terminal_container.setLayout(terminal_layout)
        self.terminal_container.hide()
        self.main_layout.addWidget(self.terminal_container)
        
        self.setLayout(self.main_layout)

    def show_terminal(self):
        self.welcome_widget.hide()
        self.terminal_container.show()
        
        if self.tab_widget.count() == 0:
            self.add_new_tab()

    def add_new_tab(self):
        self.tab_counter += 1
        terminal = TerminalWidget(self.tab_counter)
        tab_name = f"shell {self.tab_counter}"
        index = self.tab_widget.addTab(terminal, tab_name)
        self.tab_widget.setCurrentIndex(index)
        terminal.setFocus()

    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            widget = self.tab_widget.widget(index)
            self.tab_widget.removeTab(index)
            widget.close()
        else:
            self.close()

    def close_current_tab(self):
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            self.close_tab(current_index)

    def closeEvent(self, event):
        while self.tab_widget.count() > 0:
            widget = self.tab_widget.widget(0)
            self.tab_widget.removeTab(0)
            widget.close()
        super().closeEvent(event)


def run():
    app = QApplication(sys.argv)
    app.setApplicationName("yat")
    app.setFont(QFont("JetBrains Mono", 11))
    
    window = YATMainWindow()
    window.show()
    
    sys.exit(app.exec())