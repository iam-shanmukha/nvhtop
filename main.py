from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Label, ProgressBar, Static, Button
from textual.containers import Container, Grid, VerticalScroll, Vertical
from textual.binding import Binding
from textual.screen import ModalScreen
from textual import work
from monitor import GPUMonitor
import time
import os
import signal
import psutil

def format_bytes(size):
    power = 2**10
    n = size
    power_labels = {0 : '', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    count = 0
    while n > power:
        n /= power
        count += 1
    return f"{n:.2f} {power_labels.get(count, '')}B"

class KillConfirmModal(ModalScreen):
    def __init__(self, pid, name):
        super().__init__()
        self.pid = pid
        self.process_name = name

    def compose(self) -> ComposeResult:
        with Grid(id="dialog"):
            yield Label(f"Are you sure you want to kill process?\n\n{self.process_name} (PID: {self.pid})", id="question")
            yield Button("Cancel", variant="primary", id="cancel")
            yield Button("Kill", variant="error", id="kill")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "kill":
            self.dismiss(True)
        else:
            self.dismiss(False)

from textual.containers import Horizontal
# ... (imports)

class GPUCard(Static):
    def __init__(self, index, initial_stats, **kwargs):
        super().__init__(**kwargs)
        self.gpu_index = index
        self.stats = initial_stats
        self.classes = "gpu-card"
        self.border_title = f"GPU {index}"

    def compose(self) -> ComposeResult:
        # Header Row
        with Horizontal(classes="gpu-header-row"):
             yield Label(self.stats['name'], classes="gpu-name")
             with Horizontal(classes="header-stats"):
                 yield Label(f"{self.stats['temperature']}C", id=f"temp_{self.gpu_index}", classes="header-stat")
                 yield Label(f"{self.stats['fan_speed']}% Fan", id=f"fan_{self.gpu_index}", classes="header-stat")
                 yield Label(f"{self.stats['power_usage']:.1f}W", id=f"power_{self.gpu_index}", classes="header-stat")
        
        # GPU Util Row
        with Grid(classes="stat-row"):
            yield Label("GPU", classes="stat-label")
            yield ProgressBar(total=100, show_eta=False, show_percentage=False, id=f"gpu_util_{self.gpu_index}", classes="bar-container")
            yield Label(f"{self.stats['gpu_util']}%", id=f"gpu_val_{self.gpu_index}", classes="stat-value")
        
        # Memory Util Row
        with Grid(classes="stat-row"):
            yield Label("Mem", classes="stat-label")
            yield ProgressBar(total=self.stats['memory_total'], show_eta=False, show_percentage=False, id=f"mem_util_{self.gpu_index}", classes="bar-container")
            yield Label(f"{format_bytes(self.stats['memory_used'])}/{format_bytes(self.stats['memory_total'])}", id=f"mem_val_{self.gpu_index}", classes="stat-value")

    def update_stats(self, stats):
        # Update Bars
        self.query_one(f"#gpu_util_{self.gpu_index}", ProgressBar).update(progress=stats['gpu_util'])
        self.query_one(f"#mem_util_{self.gpu_index}", ProgressBar).update(progress=stats['memory_used'])
        
        # Update Text Values
        self.query_one(f"#gpu_val_{self.gpu_index}", Label).update(f"{stats['gpu_util']}%")
        self.query_one(f"#mem_val_{self.gpu_index}", Label).update(f"{format_bytes(stats['memory_used'])}/{format_bytes(stats['memory_total'])}")

        # Update Header Stats
        self.query_one(f"#temp_{self.gpu_index}", Label).update(f"{stats['temperature']}C")
        self.query_one(f"#fan_{self.gpu_index}", Label).update(f"{stats['fan_speed']}% Fan")
        self.query_one(f"#power_{self.gpu_index}", Label).update(f"{stats['power_usage']:.1f}W")

class SystemStats(Static):
    def compose(self) -> ComposeResult:
        self.cpu_count = psutil.cpu_count()
        mid_point = self.cpu_count // 2 + (self.cpu_count % 2)

        # Left Column
        with Vertical(classes="cpu-column"):
            for i in range(mid_point):
                with Grid(classes="cpu-row"):
                    yield Label(f"{i+1}", classes="cpu-label")
                    yield ProgressBar(total=100, show_eta=False, id=f"cpu_{i}", classes="bar-container")

            # Mem & Swap in left column
            with Grid(classes="mem-swp-row"):
                yield Label("Mem", classes="cpu-label")
                yield ProgressBar(total=100, show_eta=False, id="mem_bar", classes="bar-container")
            
            with Grid(classes="mem-swp-row"):
                yield Label("Swp", classes="cpu-label")
                yield ProgressBar(total=100, show_eta=False, id="swap_bar", classes="bar-container")

        # Right Column
        with Vertical(classes="cpu-column"):
            for i in range(mid_point, self.cpu_count):
                with Grid(classes="cpu-row"):
                    yield Label(f"{i+1}", classes="cpu-label")
                    yield ProgressBar(total=100, show_eta=False, id=f"cpu_{i}", classes="bar-container")

    def update_stats(self, stats):
        # Update CPU
        for i, usage in enumerate(stats['cpu_percent']):
             try:
                 bar = self.query_one(f"#cpu_{i}", ProgressBar)
                 bar.update(progress=usage)
             except:
                 pass
        
        # Update Mem
        try:
            self.query_one("#mem_bar", ProgressBar).update(progress=stats['memory']['percent'])
        except:
             pass
        
        # Update Swap
        try:
            self.query_one("#swap_bar", ProgressBar).update(progress=stats['swap']['percent'])
        except:
             pass

class NVHTopApp(App):
    CSS_PATH = "styles.tcss"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("k", "kill_process", "Kill Process"),
    ]

    def __init__(self):
        super().__init__()
        self.monitor = GPUMonitor()
        self.gpu_cards = {}
        self.system_stats = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        # System Stats
        self.system_stats = SystemStats(id="system-stats")
        yield self.system_stats
        
        gpu_stats = self.monitor.get_gpu_stats()
        
        # GPU Section
        with VerticalScroll(id="gpu-container"):
            for stats in gpu_stats:
                gpu_card = GPUCard(stats['index'], stats)
                self.gpu_cards[stats['index']] = gpu_card
                yield gpu_card

        # Process Section
        with Vertical():
            yield Label("Processes (Select row and press 'k' to kill)", id="process-title")
            yield DataTable()
        
        yield Footer()

    def on_mount(self) -> None:
        self.update_interval = self.set_interval(1.0, self.update_data)
        
        table = self.query_one(DataTable)
        table.add_columns("PID", "GPU", "Process Name", "Memory Usage")
        table.cursor_type = "row"

    def update_data(self) -> None:
        # Update System Stats
        sys_stats = self.monitor.get_system_stats()
        if self.system_stats:
            self.system_stats.update_stats(sys_stats)

        # Update GPU Stats
        stats_list = self.monitor.get_gpu_stats()
        for stats in stats_list:
            if stats['index'] in self.gpu_cards:
                self.gpu_cards[stats['index']].update_stats(stats)

        # Update Processes
        table = self.query_one(DataTable)
        procs = self.monitor.get_processes()
        
        # Update logic: Clear and re-populate
        # Preserving selection would be nice, but row indices might change.
        # For a simple 'htop' clone, full refresh is often acceptable if sort order is stable.
        
        current_row = table.cursor_row
        table.clear()
        
        for p in procs:
            table.add_row(
                str(p['pid']),
                str(p['gpu_index']),
                p['name'],
                format_bytes(p['memory_used'])
            )
            
        # Attempt to restore cursor roughly if possible, but for now just let it reset or stay at index
        if current_row is not None and current_row < table.row_count:
            table.move_cursor(row=current_row)

    def action_kill_process(self):
        table = self.query_one(DataTable)
        try:
            row_index = table.cursor_row
            if row_index is None:
                self.notify("No process selected", severity="warning")
                return

            row_values = table.get_row_at(row_index)
            pid = int(row_values[0])
            name = row_values[2]
            
            def check_kill(should_kill):
                if should_kill:
                    try:
                        os.kill(pid, signal.SIGKILL)
                        self.notify(f"Killed {name} ({pid})")
                        # Immediate update
                        self.update_data()
                    except Exception as e:
                        self.notify(f"Error killing {pid}: {e}", severity="error")

            self.push_screen(KillConfirmModal(pid, name), check_kill)
        except Exception as e:
            self.notify(f"Error selecting process: {e}", severity="error")

    def on_unmount(self) -> None:
        self.monitor.close()

if __name__ == "__main__":
    app = NVHTopApp()
    app.run()
