# 📊 Monitor de Preços

Web scraper que rastreia preços de produtos em e-commerces brasileiros e envia alertas por e-mail quando o preço cai abaixo do valor definido. Histórico salvo em banco de dados SQLite.

---

## ✨ Como funciona

Você define os produtos que quer monitorar e o preço alvo. O script roda em loop, verifica o preço atual a cada 30 minutos e te manda um e-mail assim que o preço cair.

```
🛒 Monitor iniciado — verificando a cada 30 min

Notebook Dell XPS 15: R$ 5.499,00 (alvo: R$ 5.000,00) — aguardando...
iPhone 15 Pro:        R$ 6.300,00 (alvo: R$ 6.500,00) — 🔥 ALERTA ENVIADO!
```

---

## 🛠️ Tecnologias

- **Python** — linguagem principal
- **BeautifulSoup** — scraping de páginas HTML (Mercado Livre)
- **Playwright** — scraping de páginas com JavaScript (Amazon)
- **SQLite** — histórico de preços local
- **smtplib** — envio de alertas por e-mail
- **requests** — requisições HTTP

---

## 📋 Funcionalidades

- Suporte a Mercado Livre e Amazon
- Rotação de User-Agents para evitar bloqueios
- Múltiplos seletores CSS por loja (adapta a mudanças no site)
- Histórico dos últimos 30 registros por produto em SQLite
- Alertas por e-mail com nome do produto, preço atual, alvo e link direto
- Log completo em `monitor.log`
- Intervalo aleatório entre requisições para não ser bloqueado

---

## ⚙️ Configuração

### 1. Clone o repositório
```bash
git clone https://github.com/Gabriel-Dev03/Monitor-Precoss.git
cd Monitor-Precoss
```

### 2. Instale as dependências
```bash
pip install requests beautifulsoup4 playwright
playwright install chromium
```

### 3. Configure os produtos no `monitor.py`
```python
PRODUTOS = [
    {
        "nome": "Nome do Produto",
        "url": "https://www.mercadolivre.com.br/...",
        "preco_alvo": 500.00,
        "loja": "mercadolivre"  # ou "amazon"
    },
]
```

### 4. Configure o e-mail para alertas
```python
EMAIL_ALERTA = "seu@email.com"

# No método enviar_alerta(), configure seu SMTP:
s.login("seuemail@gmail.com", "senha_de_app_gmail")
```

> 💡 Para usar Gmail, gere uma **senha de app** em: Conta Google → Segurança → Senhas de app

### 5. Rode o monitor
```bash
python monitor.py
```

---

## 📁 Estrutura do projeto

```
Monitor-Precoss/
├── monitor.py     # Código principal
├── precos.db      # Banco SQLite gerado automaticamente
├── monitor.log    # Log de execuções
└── README.md
```

---

## 📧 Exemplo de alerta recebido

```
Assunto: 🔥 Queda de preço: iPhone 15 Pro 128GB

Produto:     iPhone 15 Pro 128GB
Loja:        AMAZON
Preço atual: R$ 6.300,00
Seu alvo:    R$ 6.500,00
Economia:    3.1% abaixo do alvo
```

---

## ⚠️ Observações

- Sites mudam seus seletores com frequência — pode ser necessário atualizar o código
- Use com responsabilidade e respeite os termos de uso dos sites monitorados
- Lojas suportadas: `mercadolivre` e `amazon`

---

## 👤 Autor

**Gabriel Jesus** — [github.com/Gabriel-Dev03](https://github.com/Gabriel-Dev03)
