"""Inicia o servidor do formulário e abre o Chrome automaticamente."""
import os
import socket
import threading
import time
import traceback
import webbrowser
from pathlib import Path

PORTA = 5000
URL = f"http://localhost:{PORTA}"


def porta_ocupada():
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", PORTA)) == 0


def achar_chrome():
    pastas = [os.environ.get("PROGRAMFILES"), os.environ.get("PROGRAMFILES(X86)"),
              os.environ.get("LOCALAPPDATA")]
    for pasta in filter(None, pastas):
        caminho = Path(pasta) / "Google" / "Chrome" / "Application" / "chrome.exe"
        if caminho.exists():
            return str(caminho)
    return None


def abrir_navegador():
    for _ in range(50):  # espera até 10 segundos o servidor ligar
        if porta_ocupada():
            break
        time.sleep(0.2)
    chrome = achar_chrome()
    if chrome:
        webbrowser.register("chrome", None, webbrowser.BackgroundBrowser(chrome))
        webbrowser.get("chrome").open(URL)
    else:
        webbrowser.open(URL)  # Chrome não encontrado: usa o navegador padrão


def main():
    if porta_ocupada():
        print("O formulário já está rodando. Abrindo o navegador...")
        abrir_navegador()
        return
    import app  # importado aqui para mostrar erros de configuração de forma clara

    threading.Thread(target=abrir_navegador, daemon=True).start()
    print(f"Formulário rodando em {URL}")
    print("Para encerrar, feche esta janela (ou aperte Ctrl+C).")
    app.app.run(host="127.0.0.1", port=PORTA, debug=False)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        input("\nOcorreu um erro. Pressione Enter para sair...")
