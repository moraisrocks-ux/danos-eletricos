from flask import Flask, jsonify, render_template
from flask_cors import CORS
import logging
import os
from src.api.download_routes import registrar_blueprint as registrar_download
from src.api.download_base64_routes import registrar_blueprint as registrar_download_base64

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def criar_app():
    """Cria e configura a aplicação Flask."""
    app = Flask(__name__, template_folder='templates')
    
    # Configurações
    app.config['JSON_SORT_KEYS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max
    
    # CORS - permitir requisições de qualquer origem
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Registrar blueprints
    registrar_download(app)
    registrar_download_base64(app)
    
    # Rotas básicas
    @app.route('/', methods=['GET'])
    def index():
        """Página inicial da aplicação."""
        return render_template('download.html')
    
    @app.route('/api', methods=['GET'])
    def api_info():
        """Informações sobre a API."""
        return jsonify({
            'nome': 'Danos Elétricos - Sistema de Relatórios',
            'versao': '1.0.0',
            'descricao': 'Sistema para gerar e exportar relatórios de danos elétricos',
            'endpoints': {
                'download_relatorio': '/api/download/relatorio/<id>',
                'download_multiplos': '/api/download/multiplos',
                'download_com_anexos': '/api/download/relatorio-com-anexos/<id>',
                'download_pasta': '/api/download/pasta',
                'download_base64_relatorio': '/api/download/base64/relatorio/<id>',
                'download_base64_multiplos': '/api/download/base64/multiplos',
                'download_base64_com_anexos': '/api/download/base64/relatorio-com-anexos/<id>',
                'status': '/api/download/status',
                'status_base64': '/api/download/base64/status',
                'health': '/health'
            }
        }), 200
    
    @app.route('/health', methods=['GET'])
    def health():
        """Verificar saúde da aplicação."""
        return jsonify({
            'status': 'online',
            'servico': 'Danos Elétricos'
        }), 200
    
    # Tratamento de erros
    @app.errorhandler(404)
    def nao_encontrado(error):
        return jsonify({'erro': 'Rota não encontrada', 'detalhes': str(error)}), 404
    
    @app.errorhandler(500)
    def erro_interno(error):
        logger.error(f"Erro interno do servidor: {str(error)}")
        return jsonify({'erro': 'Erro interno do servidor', 'detalhes': str(error)}), 500
    
    logger.info("Aplicação Flask criada com sucesso")
    return app


if __name__ == '__main__':
    app = criar_app()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
