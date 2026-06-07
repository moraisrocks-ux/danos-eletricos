import os
import zipfile
import io
import tempfile
from pathlib import Path
from typing import List, Optional, BinaryIO
import logging

logger = logging.getLogger(__name__)


class ZipGenerator:
    """Classe responsável por gerar arquivos ZIP com relatórios."""

    @staticmethod
    def criar_zip_memoria(arquivos: dict, nome_zip: str = "relatorio.zip") -> io.BytesIO:
        """
        Cria um arquivo ZIP em memória.
        
        Args:
            arquivos: Dicionário com formato {caminho_no_zip: conteudo_arquivo}
            nome_zip: Nome do arquivo ZIP
            
        Returns:
            BytesIO contendo o arquivo ZIP
            
        Raises:
            ValueError: Se a lista de arquivos estiver vazia
            Exception: Se houver erro ao criar o ZIP
        """
        if not arquivos:
            raise ValueError("Lista de arquivos não pode estar vazia")
        
        try:
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for caminho, conteudo in arquivos.items():
                    if isinstance(conteudo, str):
                        conteudo = conteudo.encode('utf-8')
                    zip_file.writestr(caminho, conteudo)
            
            zip_buffer.seek(0)
            logger.info(f"Arquivo ZIP '{nome_zip}' criado com sucesso em memória")
            return zip_buffer
            
        except Exception as e:
            logger.error(f"Erro ao criar ZIP em memória: {str(e)}")
            raise Exception(f"Erro ao gerar arquivo ZIP: {str(e)}")

    @staticmethod
    def criar_zip_pasta(caminho_pasta: str, nome_zip: str = "relatorio.zip") -> io.BytesIO:
        """
        Cria um arquivo ZIP a partir de uma pasta no disco.
        
        Args:
            caminho_pasta: Caminho da pasta a ser compactada
            nome_zip: Nome do arquivo ZIP
            
        Returns:
            BytesIO contendo o arquivo ZIP
            
        Raises:
            FileNotFoundError: Se a pasta não existir
            Exception: Se houver erro ao criar o ZIP
        """
        pasta_path = Path(caminho_pasta)
        
        if not pasta_path.exists():
            raise FileNotFoundError(f"Pasta não encontrada: {caminho_pasta}")
        
        if not pasta_path.is_dir():
            raise ValueError(f"Caminho não é uma pasta: {caminho_pasta}")
        
        try:
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for root, dirs, files in os.walk(caminho_pasta):
                    for file in files:
                        arquivo_path = os.path.join(root, file)
                        # Caminho relativo dentro do ZIP
                        arcname = os.path.relpath(arquivo_path, caminho_pasta)
                        zip_file.write(arquivo_path, arcname)
            
            zip_buffer.seek(0)
            logger.info(f"Arquivo ZIP '{nome_zip}' criado com sucesso a partir de pasta")
            return zip_buffer
            
        except Exception as e:
            logger.error(f"Erro ao criar ZIP de pasta: {str(e)}")
            raise Exception(f"Erro ao gerar arquivo ZIP: {str(e)}")

    @staticmethod
    def adicionar_arquivo_zip(zip_buffer: io.BytesIO, caminho_arquivo: str, 
                             nome_no_zip: Optional[str] = None) -> io.BytesIO:
        """
        Adiciona um arquivo a um ZIP existente em memória.
        
        Args:
            zip_buffer: BytesIO contendo um ZIP
            caminho_arquivo: Caminho do arquivo a adicionar
            nome_no_zip: Nome do arquivo dentro do ZIP (se None, usa o nome original)
            
        Returns:
            BytesIO atualizado com o novo arquivo
        """
        if not Path(caminho_arquivo).exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")
        
        try:
            # Ler o ZIP existente
            zip_buffer.seek(0)
            temp_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'r') as zip_read:
                with zipfile.ZipFile(temp_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_write:
                    # Copiar arquivos existentes
                    for item in zip_read.infolist():
                        data = zip_read.read(item.filename)
                        zip_write.writestr(item, data)
                    
                    # Adicionar novo arquivo
                    arcname = nome_no_zip or os.path.basename(caminho_arquivo)
                    zip_write.write(caminho_arquivo, arcname)
            
            temp_buffer.seek(0)
            logger.info(f"Arquivo '{caminho_arquivo}' adicionado ao ZIP")
            return temp_buffer
            
        except Exception as e:
            logger.error(f"Erro ao adicionar arquivo ao ZIP: {str(e)}")
            raise Exception(f"Erro ao adicionar arquivo: {str(e)}")

    @staticmethod
    def extrair_zip(zip_buffer: io.BytesIO, caminho_destino: str) -> None:
        """
        Extrai um arquivo ZIP para uma pasta.
        
        Args:
            zip_buffer: BytesIO contendo um ZIP
            caminho_destino: Caminho da pasta de destino
            
        Raises:
            Exception: Se houver erro ao extrair
        """
        Path(caminho_destino).mkdir(parents=True, exist_ok=True)
        
        try:
            zip_buffer.seek(0)
            with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
                zip_file.extractall(caminho_destino)
            
            logger.info(f"Arquivo ZIP extraído com sucesso para {caminho_destino}")
            
        except Exception as e:
            logger.error(f"Erro ao extrair ZIP: {str(e)}")
            raise Exception(f"Erro ao extrair arquivo: {str(e)}")
