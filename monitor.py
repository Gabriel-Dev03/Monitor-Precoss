"""
Monitor de Preços — Web Scraper
Autor: Gabriel-Dev03
GitHub: github.com/Gabriel-Dev03/monitor-precos

Rastreia preços em e-commerces e dispara alertas quando o preço cai.
"""

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import sqlite3
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import time
import random
import logging

logging.basicConfig(
    filename="monitor.log", level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ─── Configurações ─────────────────────────────────────────
DB_PATH = "precos.db"
INTERVALO_MINUTOS = 30          # Checa a cada 30 minutos
EMAIL_ALERTA = "seu@email.com"  # Onde receber alertas

# Lista de produtos para monitorar
PRODUTOS = [
    {
        "nome": "Notebook Dell XPS 15",
        "url": "https://www.mercadolivre.com.br/...",
        "preco_alvo": 5000.00,   # Alerta se ficar abaixo desse valor
        "loja": "mercadolivre"
    },
    {
        "nome": "iPhone 15 Pro 128GB",
        "url": "https://www.amazon.com.br/...",
        "preco_alvo": 6500.00,
        "loja": "amazon"
    },
]

# User-agents para evitar bloqueio
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
]


# ─── Banco de dados ────────────────────────────────────────
def iniciar_banco():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS historico_precos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto TEXT NOT NULL,
            loja TEXT NOT NULL,
            preco REAL NOT NULL,
            data_hora TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def salvar_preco(produto: str, loja: str, preco: float):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO historico_precos (produto, loja, preco, data_hora) VALUES (?, ?, ?, ?)",
        (produto, loja, preco, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def buscar_historico(produto: str) -> list:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT preco, data_hora FROM historico_precos WHERE produto = ? ORDER BY data_hora DESC LIMIT 30",
        (produto,)
    ).fetchall()
    conn.close()
    return rows


# ─── Scrapers por loja ─────────────────────────────────────
def scrape_mercadolivre(url: str) -> float | None:
    """Extrai preço do Mercado Livre."""
    try:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Tenta diferentes seletores (ML muda com frequência)
        seletores = [
            "span.andes-money-amount__fraction",
            ".price-tag-fraction",
            "meta[itemprop='price']",
        ]
        for seletor in seletores:
            el = soup.select_one(seletor)
            if el:
                preco_str = el.get("content") or el.text
                preco = float(preco_str.replace(".", "").replace(",", ".").strip())
                return preco
    except Exception as e:
        logging.error(f"Erro ML: {e}")
    return None


def scrape_amazon(url: str) -> float | None:
    """Extrai preço da Amazon (usa Playwright para JS)."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=random.choice(USER_AGENTS))
            page.goto(url, timeout=20000)
            page.wait_for_load_state("networkidle")
            
            el = page.query_selector(".a-price-whole")
            if el:
                preco_str = el.inner_text().replace(".", "").replace(",", ".").strip()
                browser.close()
                return float(preco_str)
            browser.close()
    except Exception as e:
        logging.error(f"Erro Amazon: {e}")
    return None


SCRAPERS = {
    "mercadolivre": scrape_mercadolivre,
    "amazon": scrape_amazon,
}


# ─── Alertas ───────────────────────────────────────────────
def enviar_alerta(produto: dict, preco_atual: float):
    """Envia alerta de queda de preço por e-mail."""
    desconto = ((produto["preco_alvo"] - preco_atual) / produto["preco_alvo"]) * 100
    
    corpo = f"""
🚨 ALERTA DE PREÇO — {produto['nome']}

O preço caiu abaixo do seu alvo!

Produto: {produto['nome']}
Loja:    {produto['loja'].upper()}
Preço atual: R$ {preco_atual:,.2f}
Seu alvo:    R$ {produto['preco_alvo']:,.2f}
Economia:    {desconto:.1f}% abaixo do alvo

👉 Link: {produto['url']}

Este alerta foi gerado automaticamente.
    """
    
    msg = MIMEText(corpo, "plain", "utf-8")
    msg["Subject"] = f"🔥 Queda de preço: {produto['nome']}"
    msg["From"] = "monitor@seudominio.com"
    msg["To"] = EMAIL_ALERTA
    
    # Substitua com seu servidor SMTP
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login("seuemail@gmail.com", "senha_de_app")
        s.send_message(msg)
    
    logging.info(f"Alerta enviado: {produto['nome']} por R${preco_atual:.2f}")


# ─── Loop principal ────────────────────────────────────────
def checar_precos():
    logging.info("Iniciando verificação de preços...")
    
    for produto in PRODUTOS:
        loja = produto.get("loja", "mercadolivre")
        scraper = SCRAPERS.get(loja)
        
        if not scraper:
            logging.warning(f"Loja não suportada: {loja}")
            continue
        
        preco = scraper(produto["url"])
        
        if preco is None:
            logging.warning(f"Não foi possível extrair preço: {produto['nome']}")
            continue
        
        logging.info(f"{produto['nome']}: R$ {preco:.2f} (alvo: R$ {produto['preco_alvo']:.2f})")
        salvar_preco(produto["nome"], loja, preco)
        
        if preco <= produto["preco_alvo"]:
            enviar_alerta(produto, preco)
        
        # Pausa entre requests para não ser bloqueado
        time.sleep(random.uniform(3, 8))


if __name__ == "__main__":
    iniciar_banco()
    print(f"🛒 Monitor de Preços iniciado — verificando a cada {INTERVALO_MINUTOS} min")
    
    while True:
        checar_precos()
        print(f"Próxima verificação em {INTERVALO_MINUTOS} minutos...")
        time.sleep(INTERVALO_MINUTOS * 60)
