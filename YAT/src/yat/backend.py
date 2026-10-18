from winpty import PtyProcess

class YATBackend:
    def __init__(self, cols: int, rows: int):
        try:
            self.proc = PtyProcess.spawn('powershell.exe -NoLogo', dimensions=(rows, cols))
        except Exception as e:
            print(f"Error starting PowerShell: {e}")
            self.proc = None
        
    def read(self, size: int = 65536) -> str:
        try:
            if self.proc and self.proc.isalive():
                return self.proc.read(size)
        except EOFError:
            pass
        return ""
            
    def write(self, data: str):
        try:
            if self.proc and self.proc.isalive():
                self.proc.write(data)
        except (EOFError, OSError) as e:
            print(f"Write error: {e}")
        
    def resize(self, cols: int, rows: int):
        try:
            if self.proc and self.proc.isalive():
                self.proc.setwinsize(rows, cols)
        except Exception:
            pass
        
    def is_alive(self) -> bool:
        try:
            return self.proc is not None and self.proc.isalive()
        except Exception:
            return False
        
    def close(self):
        try:
            if self.proc:
                self.proc.terminate(force=True)
        except Exception:
            pass