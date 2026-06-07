// DownloadService.js - Serviço de download para React Native
// CORRIGIDO: Decodifica BASE64 e salva arquivo ZIP corretamente

import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import * as DocumentPicker from 'expo-document-picker';

// Mude para seu domínio em produção
const API_BASE_URL = 'https://inspeq.startstanly.com';
// Ou para testes locais: 'http://192.168.1.XXX:5000'

export class DownloadService {
  /**
   * Baixa um relatório individual em BASE64
   * @param {string} relatorioId - ID do relatório
   * @returns {Promise<{success: boolean, arquivo: string, nomeArquivo: string, tamanho: number}>}
   */
  static async baixarRelatorio(relatorioId) {
    try {
      console.log(`[DownloadService] Iniciando download do relatório ${relatorioId}`);
      
      const response = await fetch(
        `${API_BASE_URL}/api/download/base64/relatorio/${relatorioId}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      console.log(`[DownloadService] Status da resposta: ${response.status}`);

      if (!response.ok) {
        const erro = await response.json();
        throw new Error(erro.detalhes || `Erro ao baixar relatório: ${response.status}`);
      }

      const dados = await response.json();
      
      console.log(`[DownloadService] Dados recebidos:`, {
        success: dados.success,
        nomeArquivo: dados.nome_arquivo,
        tamanhoBase64: dados.arquivo?.length,
      });

      if (!dados.success || !dados.arquivo) {
        throw new Error('Resposta inválida da API');
      }

      return {
        success: true,
        arquivo: dados.arquivo, // BASE64 string
        nomeArquivo: dados.nome_arquivo,
        tamanho: dados.tamanho_bytes,
      };
    } catch (error) {
      console.error('[DownloadService] Erro ao baixar relatório:', error);
      throw error;
    }
  }

  /**
   * Baixa múltiplos relatórios em BASE64
   * @param {number[]} relatorioIds - Array com IDs dos relatórios
   * @param {string} nomeZip - Nome do arquivo ZIP
   * @returns {Promise<{success: boolean, arquivo: string, nomeArquivo: string, tamanho: number}>}
   */
  static async baixarMultiplos(relatorioIds, nomeZip = 'relatorios.zip') {
    try {
      console.log(`[DownloadService] Iniciando download de ${relatorioIds.length} relatórios`);

      const response = await fetch(
        `${API_BASE_URL}/api/download/base64/multiplos`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            relatorio_ids: relatorioIds,
            nome_zip: nomeZip,
          }),
        }
      );

      console.log(`[DownloadService] Status da resposta: ${response.status}`);

      if (!response.ok) {
        const erro = await response.json();
        throw new Error(erro.detalhes || `Erro ao baixar: ${response.status}`);
      }

      const dados = await response.json();
      
      if (!dados.success || !dados.arquivo) {
        throw new Error('Resposta inválida da API');
      }

      return {
        success: true,
        arquivo: dados.arquivo,
        nomeArquivo: dados.nome_arquivo,
        tamanho: dados.tamanho_bytes,
        quantidade: dados.quantidade,
      };
    } catch (error) {
      console.error('[DownloadService] Erro ao baixar múltiplos:', error);
      throw error;
    }
  }

  /**
   * Baixa relatório com anexos em BASE64
   * @param {string} relatorioId - ID do relatório
   * @returns {Promise<{success: boolean, arquivo: string, nomeArquivo: string, tamanho: number}>}
   */
  static async baixarComAnexos(relatorioId) {
    try {
      console.log(`[DownloadService] Iniciando download com anexos ${relatorioId}`);

      const response = await fetch(
        `${API_BASE_URL}/api/download/base64/relatorio-com-anexos/${relatorioId}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      console.log(`[DownloadService] Status da resposta: ${response.status}`);

      if (!response.ok) {
        const erro = await response.json();
        throw new Error(erro.detalhes || `Erro ao baixar: ${response.status}`);
      }

      const dados = await response.json();
      
      if (!dados.success || !dados.arquivo) {
        throw new Error('Resposta inválida da API');
      }

      return {
        success: true,
        arquivo: dados.arquivo,
        nomeArquivo: dados.nome_arquivo,
        tamanho: dados.tamanho_bytes,
      };
    } catch (error) {
      console.error('[DownloadService] Erro ao baixar com anexos:', error);
      throw error;
    }
  }

  /**
   * Salva arquivo BASE64 no dispositivo
   * ESTE É O MÉTODO QUE REALMENTE SALVA O ZIP
   * @param {string} base64String - String em BASE64
   * @param {string} nomeArquivo - Nome do arquivo (ex: relatorio.zip)
   * @returns {Promise<string>} - Caminho do arquivo salvo
   */
  static async salvarArquivo(base64String, nomeArquivo) {
    try {
      console.log(`[DownloadService] Decodificando BASE64...`);
      
      // Caminho para salvar o arquivo
      const fileUri = `${FileSystem.DocumentDirectoryPath}/${nomeArquivo}`;
      
      console.log(`[DownloadService] Caminho do arquivo: ${fileUri}`);
      console.log(`[DownloadService] Tamanho do BASE64: ${base64String.length} caracteres`);

      // Salvar o arquivo decodificando BASE64
      await FileSystem.writeAsStringAsync(fileUri, base64String, {
        encoding: FileSystem.EncodingType.Base64,
      });

      console.log(`[DownloadService] ✅ Arquivo salvo com sucesso: ${fileUri}`);
      
      // Verificar se o arquivo foi criado
      const fileInfo = await FileSystem.getInfoAsync(fileUri);
      console.log(`[DownloadService] Info do arquivo:`, fileInfo);

      return fileUri;
    } catch (error) {
      console.error('[DownloadService] Erro ao salvar arquivo:', error);
      throw new Error(`Erro ao salvar arquivo: ${error.message}`);
    }
  }

  /**
   * Compartilha arquivo com outras apps
   * @param {string} fileUri - Caminho do arquivo
   * @param {string} nomeArquivo - Nome do arquivo
   * @returns {Promise<void>}
   */
  static async compartilharArquivo(fileUri, nomeArquivo) {
    try {
      console.log(`[DownloadService] Compartilhando arquivo: ${fileUri}`);

      if (!(await Sharing.isAvailableAsync())) {
        console.warn('[DownloadService] Compartilhamento não disponível');
        alert('Compartilhamento não disponível neste dispositivo');
        return;
      }

      await Sharing.shareAsync(fileUri, {
        mimeType: 'application/zip',
        dialogTitle: `Compartilhar ${nomeArquivo}`,
      });

      console.log(`[DownloadService] ✅ Arquivo compartilhado`);
    } catch (error) {
      console.error('[DownloadService] Erro ao compartilhar:', error);
      throw error;
    }
  }

  /**
   * MÉTODO PRINCIPAL: Download completo
   * 1. Busca na API
   * 2. Decodifica BASE64
   * 3. Salva no dispositivo
   * 4. Compartilha (opcional)
   * 
   * @param {string} relatorioId - ID do relatório
   * @param {boolean} compartilhar - Se deve compartilhar automaticamente
   * @returns {Promise<{sucesso: boolean, caminhoArquivo: string, nomeArquivo: string}>}
   */
  static async downloadCompleto(relatorioId, compartilhar = true) {
    try {
      console.log(`\n========== INICIANDO DOWNLOAD COMPLETO ==========`);
      console.log(`Relatório ID: ${relatorioId}`);
      console.log(`Compartilhar: ${compartilhar}`);

      // PASSO 1: Buscar relatório da API
      console.log('\n[PASSO 1] Buscando relatório na API...');
      const dados = await this.baixarRelatorio(relatorioId);
      console.log('[PASSO 1] ✅ Relatório obtido');

      // PASSO 2: Salvar no dispositivo
      console.log('\n[PASSO 2] Salvando arquivo no dispositivo...');
      const caminhoArquivo = await this.salvarArquivo(
        dados.arquivo,
        dados.nomeArquivo
      );
      console.log('[PASSO 2] ✅ Arquivo salvo');

      // PASSO 3: Compartilhar se solicitado
      if (compartilhar) {
        console.log('\n[PASSO 3] Compartilhando arquivo...');
        await this.compartilharArquivo(caminhoArquivo, dados.nomeArquivo);
        console.log('[PASSO 3] ✅ Arquivo compartilhado');
      }

      console.log(`\n========== DOWNLOAD COMPLETO ✅ ==========\n`);

      return {
        sucesso: true,
        caminhoArquivo,
        nomeArquivo: dados.nomeArquivo,
      };
    } catch (error) {
      console.error('\n❌ ERRO NO DOWNLOAD COMPLETO:', error);
      throw error;
    }
  }

  /**
   * Download múltiplo completo
   */
  static async downloadMultiploCompleto(relatorioIds, nomeZip = 'relatorios.zip', compartilhar = true) {
    try {
      console.log(`\n========== DOWNLOAD MÚLTIPLO COMPLETO ==========`);
      
      const dados = await this.baixarMultiplos(relatorioIds, nomeZip);
      const caminhoArquivo = await this.salvarArquivo(
        dados.arquivo,
        dados.nomeArquivo
      );

      if (compartilhar) {
        await this.compartilharArquivo(caminhoArquivo, dados.nomeArquivo);
      }

      console.log(`========== ✅ CONCLUÍDO ==========\n`);

      return {
        sucesso: true,
        caminhoArquivo,
        nomeArquivo: dados.nomeArquivo,
      };
    } catch (error) {
      console.error('❌ ERRO:', error);
      throw error;
    }
  }
}

export default DownloadService;
