import sys
import os

# Adiciona o diretório raiz ao sys.path para garantir importações corretas
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.gui import AppInterface

if __name__ == "__main__":
    app = AppInterface()
    app.mainloop()
