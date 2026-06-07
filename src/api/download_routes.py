from flask import Blueprint, send_file, jsonify, request, make_response
from functools import wraps
import logging
import io
from datetime import datetime
from src.utils.zip_generator import ZipGenerator

logger = logging.getLogger(__name__)

# Blueprint para rotas de download
download_bp = Blueprint('download', __name__, url_prefix='/api/download')


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


def preparar_resposta_download(zip_buffer: io.BytesIO, nome_arquivo: str):
    """
    Prepara a resposta de download com headers corretos para mobile e desktop.
    
    Args:
        zip_buffer: Buffer contendo o arquivo ZIP
        nome_arquivo: Nome do arquivo para download
        
    Returns:
        Response com os headers corretos
    """
    response = make_response(send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=nome_arquivo
    ))
    
    # Headers essenciais para mobile e desktop
    response.headers['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
    response.headers['Content-Type'] = 'application/zip'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    
    # Headers para mobile
    response.headers['Content-Transfer-Encoding'] = 'binary'
    
    return response


@download_bp.route('/relatorio/<relatorio_id>', methods=['GET', 'OPTIONS'])
@tratamento_erro
def download_relatorio(relatorio_id):
    """
    Download de um relatório individual em ZIP.
    
    Args:
        relatorio_id: ID do relatório a baixar
        
    Returns:
        Arquivo ZIP com o relatório
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
        
        nome_arquivo = f'relatorio_{relatorio_id}.zip'
        return preparar_resposta_download(zip_buffer, nome_arquivo)
        
    except Exception as e:
        logger.error(f"Erro ao baixar relatório {relatorio_id}: {str(e)}")
        raise


@download_bp.route('/multiplos', methods=['POST', 'OPTIONS'])
@tratamento_erro
def download_multiplos_relatorios():
    """
    Download de múltiplos relatórios em um único ZIP.
    
    Espera JSON com formato:
    {
        "relatorio_ids": [1, 2, 3],
        "nome_zip": "relatorios_2024.zip"
    }
    
    Returns:
        Arquivo ZIP contendo todos os relatórios
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
            # Simulação: Em um cenário real, você buscaria cada relatório
            pasta_nome = f'relatorio_{rid}'
            arquivos[f'{pasta_nome}/relatorio.txt'] = f'Relatório #{rid}\nData: {datetime.now().isoformat()}'
            arquivos[f'{pasta_nome}/dados.json'] = f'{{"id": {rid}, "status": "ok"}}'
        
        zip_buffer = ZipGenerator.criar_zip_memoria(arquivos, nome_zip=nome_zip)
        
        return preparar_resposta_download(zip_buffer, nome_zip)
        
    except Exception as e:
        logger.error(f"Erro ao baixar múltiplos relatórios: {str(e)}")
        raise


@download_bp.route('/relatorio-com-anexos/<relatorio_id>', methods=['GET', 'OPTIONS'])
@tratamento_erro
def download_relatorio_com_anexos(relatorio_id):
    """
    Download de relatório com anexos (imagens, documentos, etc).
    
    Args:
        relatorio_id: ID do relatório
        
    Returns:
        Arquivo ZIP contendo relatório e anexos
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
            'relatorio.pdf': b'%PDF-1.4\n... PDF content ...',  # Binário
            'fotos/foto1.jpg': b'... imagem binária ...',
            'fotos/foto2.jpg': b'... imagem binária ...',
            'documentos/laudo.txt': 'Laudo técnico de danos elétricos',
            'documentos/notas.md': '# Notas do Técnico\n\n- Encontrado dano em cabo X\n- Recomendação: Substituição imediata',
        }
        
        zip_buffer = ZipGenerator.criar_zip_memoria(
            arquivos, 
            nome_zip=f"relatorio_completo_{relatorio_id}.zip"
        )
        
        nome_arquivo = f'relatorio_completo_{relatorio_id}.zip'
        return preparar_resposta_download(zip_buffer, nome_arquivo)
        
    except Exception as e:
        logger.error(f"Erro ao baixar relatório com anexos: {str(e)}")
        raise


@download_bp.route('/pasta', methods=['POST', 'OPTIONS'])
@tratamento_erro
def download_pasta():
    """
    Download de uma pasta inteira em ZIP.
    
    Espera JSON com formato:
    {
        "caminho_pasta": "/caminho/da/pasta",
        "nome_zip": "pasta.zip"
    }
    
    Returns:
        Arquivo ZIP da pasta
    """
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response, 200
    
    dados = request.get_json()
    
    if not dados or 'caminho_pasta' not in dados:
        return jsonify({'erro': 'Campo "caminho_pasta" obrigatório'}), 400
    
    caminho_pasta = dados.get('caminho_pasta')
    nome_zip = dados.get('nome_zip', 'pasta.zip')
    
    try:
        zip_buffer = ZipGenerator.criar_zip_pasta(caminho_pasta, nome_zip=nome_zip)
        
        return preparar_resposta_download(zip_buffer, nome_zip)
        
    except Exception as e:
        logger.error(f"Erro ao baixar pasta: {str(e)}")
        raise


@download_bp.route('/status', methods=['GET', 'OPTIONS'])
def status_download():
    """Endpoint para verificar se a funcionalidade de download está disponível."""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response, 200
    
    return jsonify({
        'status': 'operacional',
        'endpoints': {
            'relatorio_unico': '/api/download/relatorio/<id>',
            'multiplos': '/api/download/multiplos',
            'com_anexos': '/api/download/relatorio-com-anexos/<id>',
            'pasta': '/api/download/pasta'
        }
    }), 200


def registrar_blueprint(app):
    """Registra o blueprint na aplicação Flask."""
    app.register_blueprint(download_bp)
    logger.info("Blueprint de download registrado com sucesso")
