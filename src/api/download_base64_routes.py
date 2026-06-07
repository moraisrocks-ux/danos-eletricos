from flask import Blueprint, jsonify, request, make_response
from functools import wraps
import logging
import io
import base64
from datetime import datetime
from src.utils.zip_generator import ZipGenerator

logger = logging.getLogger(__name__)

# Blueprint para rotas de download em BASE64
download_base64_bp = Blueprint('download_base64', __name__, url_prefix='/api/download/base64')


def tratamento_erro(f):
    """Decorator para tratamento de erros em rotas de download."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except FileNotFoundError as e:
            logger.error(f"Arquivo não encontrado: {str(e)}")
            return jsonify({'erro': 'Arquivo não encontrado', 'detalhes': str(e)}), 404
        except ValueError as e:
            logger.error(f"Erro de validação: {str(e)}")
            return jsonify({'erro': 'Erro de validação', 'detalhes': str(e)}), 400
        except Exception as e:
            logger.error(f"Erro ao processar download: {str(e)}")
            return jsonify({'erro': 'Erro ao processar download', 'detalhes': str(e)}), 500
    return wrapper


@download_base64_bp.route('/relatorio/<relatorio_id>', methods=['GET', 'OPTIONS'])
@tratamento_erro
def download_relatorio_base64(relatorio_id):
    """
    Download de um relatório individual em BASE64.
    
    Retorna JSON com:
    {
        "success": true,
        "relatorio_id": "123",
        "arquivo": "base64_encoded_zip",
        "nome_arquivo": "relatorio_123.zip",
        "tamanho_bytes": 1024,
        "timestamp": "2026-06-07T02:30:00"
    }
    
    Args:
        relatorio_id: ID do relatório a baixar
        
    Returns:
        JSON com arquivo ZIP codificado em BASE64
    """
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response, 200
    
    try:
        # Simulação: Em um cenário real, você buscaria dados do banco
        arquivos = {
            'relatorio.txt': f'Relatório de Danos Elétricos #{relatorio_id}\nData: {datetime.now().isoformat()}',
            'dados.json': '{"status": "ok", "dados": []}',
        }
        
        zip_buffer = ZipGenerator.criar_zip_memoria(
            arquivos, 
            nome_zip=f"relatorio_{relatorio_id}.zip"
        )
        
        # Converter para BASE64
        zip_bytes = zip_buffer.getvalue()
        arquivo_base64 = base64.b64encode(zip_bytes).decode('utf-8')
        
        nome_arquivo = f'relatorio_{relatorio_id}.zip'
        
        return jsonify({
            'success': True,
            'relatorio_id': relatorio_id,
            'arquivo': arquivo_base64,
            'nome_arquivo': nome_arquivo,
            'tamanho_bytes': len(zip_bytes),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao baixar relatório {relatorio_id}: {str(e)}")
        raise


@download_base64_bp.route('/multiplos', methods=['POST', 'OPTIONS'])
@tratamento_erro
def download_multiplos_base64():
    """
    Download de múltiplos relatórios em BASE64.
    
    Body:
    {
        "relatorio_ids": [1, 2, 3],
        "nome_zip": "relatorios_2024.zip"
    }
    
    Returns:
        JSON com arquivo ZIP codificado em BASE64
    """
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response, 200
    
    dados = request.get_json()
    
    if not dados or 'relatorio_ids' not in dados:
        return jsonify({'erro': 'Campo "relatorio_ids" obrigatório'}), 400
    
    relatorio_ids = dados.get('relatorio_ids', [])
    nome_zip = dados.get('nome_zip', 'relatorios.zip')
    
    if not isinstance(relatorio_ids, list) or len(relatorio_ids) == 0:
        return jsonify({'erro': 'relatorio_ids deve ser uma lista não vazia'}), 400
    
    try:
        # Construir dicionário de arquivos
        arquivos = {}
        
        for rid in relatorio_ids:
            pasta_nome = f'relatorio_{rid}'
            arquivos[f'{pasta_nome}/relatorio.txt'] = f'Relatório #{rid}\nData: {datetime.now().isoformat()}'
            arquivos[f'{pasta_nome}/dados.json'] = f'{{"id": {rid}, "status": "ok"}}'
        
        zip_buffer = ZipGenerator.criar_zip_memoria(arquivos, nome_zip=nome_zip)
        
        # Converter para BASE64
        zip_bytes = zip_buffer.getvalue()
        arquivo_base64 = base64.b64encode(zip_bytes).decode('utf-8')
        
        return jsonify({
            'success': True,
            'quantidade': len(relatorio_ids),
            'relatorio_ids': relatorio_ids,
            'arquivo': arquivo_base64,
            'nome_arquivo': nome_zip,
            'tamanho_bytes': len(zip_bytes),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao baixar múltiplos relatórios: {str(e)}")
        raise


@download_base64_bp.route('/relatorio-com-anexos/<relatorio_id>', methods=['GET', 'OPTIONS'])
@tratamento_erro
def download_relatorio_anexos_base64(relatorio_id):
    """
    Download de relatório com anexos em BASE64.
    
    Returns:
        JSON com arquivo ZIP codificado em BASE64
    """
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response, 200
    
    try:
        # Simulação de arquivos do relatório
        arquivos = {
            'relatorio.pdf': b'%PDF-1.4\n... PDF content ...',
            'fotos/foto1.jpg': b'... imagem binária ...',
            'fotos/foto2.jpg': b'... imagem binária ...',
            'documentos/laudo.txt': 'Laudo técnico de danos elétricos',
            'documentos/notas.md': '# Notas do Técnico\n\n- Encontrado dano em cabo X\n- Recomendação: Substituição imediata',
        }
        
        zip_buffer = ZipGenerator.criar_zip_memoria(
            arquivos, 
            nome_zip=f"relatorio_completo_{relatorio_id}.zip"
        )
        
        # Converter para BASE64
        zip_bytes = zip_buffer.getvalue()
        arquivo_base64 = base64.b64encode(zip_bytes).decode('utf-8')
        
        nome_arquivo = f'relatorio_completo_{relatorio_id}.zip'
        
        return jsonify({
            'success': True,
            'relatorio_id': relatorio_id,
            'tipo': 'com_anexos',
            'arquivo': arquivo_base64,
            'nome_arquivo': nome_arquivo,
            'tamanho_bytes': len(zip_bytes),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao baixar relatório com anexos: {str(e)}")
        raise


@download_base64_bp.route('/status', methods=['GET', 'OPTIONS'])
def status_download_base64():
    """Endpoint para verificar se a funcionalidade de download BASE64 está disponível."""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response, 200
    
    return jsonify({
        'status': 'operacional',
        'tipo': 'BASE64',
        'endpoints': {
            'relatorio_unico': '/api/download/base64/relatorio/<id>',
            'multiplos': '/api/download/base64/multiplos',
            'com_anexos': '/api/download/base64/relatorio-com-anexos/<id>',
        }
    }), 200


def registrar_blueprint(app):
    """Registra o blueprint na aplicação Flask."""
    app.register_blueprint(download_base64_bp)
    logger.info("Blueprint de download BASE64 registrado com sucesso")
