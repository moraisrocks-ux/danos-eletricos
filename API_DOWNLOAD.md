# 📦 API de Download - Danos Elétricos

Documentação completa da API de download de relatórios em ZIP.

## 🚀 Instalação

```bash
pip install -r requirements.txt
```

## ▶️ Como Executar

```bash
python main.py
```

A aplicação estará disponível em `http://localhost:5000`

---

## 📍 Endpoints Disponíveis

### 1. **Verificar Status** ✅
```
GET /api/download/status
```

**Resposta:**
```json
{
    "status": "operacional",
    "endpoints": {
        "relatorio_unico": "/api/download/relatorio/<id>",
        "multiplos": "/api/download/multiplos",
        "com_anexos": "/api/download/relatorio-com-anexos/<id>",
        "pasta": "/api/download/pasta"
    }
}
```

---

### 2. **Download de Relatório Individual** 📄
```
GET /api/download/relatorio/<relatorio_id>
```

**Exemplo:**
```bash
curl -X GET http://localhost:5000/api/download/relatorio/123 \
  -o relatorio_123.zip
```

**Resposta:** Arquivo ZIP com o relatório

---

### 3. **Download de Múltiplos Relatórios** 📚
```
POST /api/download/multiplos
Content-Type: application/json
```

**Body:**
```json
{
    "relatorio_ids": [1, 2, 3],
    "nome_zip": "relatorios_2024.zip"
}
```

**Exemplo com cURL:**
```bash
curl -X POST http://localhost:5000/api/download/multiplos \
  -H "Content-Type: application/json" \
  -d '{
    "relatorio_ids": [1, 2, 3],
    "nome_zip": "relatorios_janeiro.zip"
  }' \
  -o relatorios_janeiro.zip
```

**Resposta:** Arquivo ZIP contendo todos os relatórios

---

### 4. **Download de Relatório com Anexos** 📎
```
GET /api/download/relatorio-com-anexos/<relatorio_id>
```

**Exemplo:**
```bash
curl -X GET http://localhost:5000/api/download/relatorio-com-anexos/123 \
  -o relatorio_completo_123.zip
```

**Estrutura do ZIP:**
```
relatorio_completo_123.zip
├── relatorio.pdf
├── fotos/
│   ├── foto1.jpg
│   └── foto2.jpg
├── documentos/
│   ├── laudo.txt
│   └── notas.md
```

**Resposta:** Arquivo ZIP com relatório, fotos e documentos

---

### 5. **Download de Pasta** 📁
```
POST /api/download/pasta
Content-Type: application/json
```

**Body:**
```json
{
    "caminho_pasta": "/caminho/da/pasta",
    "nome_zip": "backup.zip"
}
```

**Exemplo:**
```bash
curl -X POST http://localhost:5000/api/download/pasta \
  -H "Content-Type: application/json" \
  -d '{
    "caminho_pasta": "/home/user/relatorios",
    "nome_zip": "backup_relatorios.zip"
  }' \
  -o backup_relatorios.zip
```

**Resposta:** Arquivo ZIP da pasta

---

## 🎨 Exemplo com JavaScript/Fetch

### Download Simples
```javascript
// Download de um relatório
async function baixarRelatorio(id) {
    try {
        const response = await fetch(`/api/download/relatorio/${id}`);
        
        if (!response.ok) {
            throw new Error('Erro ao baixar');
        }
        
        // Converter resposta em Blob
        const blob = await response.blob();
        
        // Criar link de download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `relatorio_${id}.zip`;
        
        document.body.appendChild(a);
        a.click();
        
        // Limpar
        window.URL.revokeObjectURL(url);
        a.remove();
        
    } catch (error) {
        console.error('Erro:', error);
    }
}
```

### Download Múltiplo
```javascript
async function baixarMultiplos(ids) {
    try {
        const response = await fetch('/api/download/multiplos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                relatorio_ids: ids,
                nome_zip: `relatorios_${new Date().toISOString().split('T')[0]}.zip`
            })
        });
        
        if (!response.ok) {
            throw new Error('Erro ao baixar');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'relatorios.zip';
        
        document.body.appendChild(a);
        a.click();
        
        window.URL.revokeObjectURL(url);
        a.remove();
        
    } catch (error) {
        console.error('Erro:', error);
    }
}
```

---

## 🐍 Exemplo com Python

### Usando requests
```python
import requests
import os

def baixar_relatorio(relatorio_id):
    """Baixa um relatório em ZIP"""
    url = f'http://localhost:5000/api/download/relatorio/{relatorio_id}'
    
    response = requests.get(url)
    
    if response.status_code == 200:
        filename = f'relatorio_{relatorio_id}.zip'
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f'✅ Arquivo salvo: {filename}')
    else:
        print(f'❌ Erro {response.status_code}: {response.text}')

def baixar_multiplos(ids, nome_zip='relatorios.zip'):
    """Baixa múltiplos relatórios"""
    url = 'http://localhost:5000/api/download/multiplos'
    
    payload = {
        'relatorio_ids': ids,
        'nome_zip': nome_zip
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        with open(nome_zip, 'wb') as f:
            f.write(response.content)
        print(f'✅ Arquivo salvo: {nome_zip}')
    else:
        print(f'❌ Erro {response.status_code}: {response.text}')

# Uso
if __name__ == '__main__':
    # Download simples
    baixar_relatorio(123)
    
    # Download múltiplo
    baixar_multiplos([1, 2, 3, 4], 'relatorios_janeiro.zip')
```

---

## ⚙️ Estrutura do Projeto

```
danos-eletricos/
├── src/
│   ├── __init__.py
│   ├── app.py                    # Aplicação principal Flask
│   ├── api/
│   │   ├── __init__.py
│   │   └── download_routes.py    # Rotas de download
│   └── utils/
│       ├── __init__.py
│       └── zip_generator.py      # Gerador de ZIPs
├── main.py                       # Ponto de entrada
├── requirements.txt              # Dependências
├── API_DOWNLOAD.md              # Esta documentação
└── README.md
```

---

## ✨ Recursos

✅ **Geração de ZIP em Memória** - Sem gravar em disco
✅ **Suporte a Múltiplos Formatos** - Texto, binário, etc
✅ **Tratamento de Erros** - Mensagens claras e logging
✅ **CORS Habilitado** - Funciona com frontend em qualquer origem
✅ **Limite de Upload** - 100MB máximo
✅ **Logging Completo** - Rastreamento de todas as operações

---

## 🐛 Troubleshooting

### Erro: "Arquivo não encontrado"
- Verifique se o caminho está correto
- Certifique-se de que o arquivo existe

### Erro: "Lista de arquivos vazia"
- O dicionário de arquivos não pode estar vazio
- Adicione pelo menos um arquivo

### Erro: "Content-Type: application/json"
- Use `Content-Type: application/json` em requisições POST
- Verifique se o JSON está válido

### Arquivo ZIP corrompido
- Verifique logs para erros de criação
- Tente novamente a requisição

---

## 📞 Suporte

Para questões ou bugs, abra uma issue no repositório:
https://github.com/moraisrocks-ux/danos-eletricos
