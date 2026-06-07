// DownloadScreen.jsx - Tela de Download para React Native
// Use com Expo ou React Native puro

import React, { useState } from 'react';
import {
  View,
  ScrollView,
  TouchableOpacity,
  Text,
  TextInput,
  ActivityIndicator,
  Alert,
  StyleSheet,
} from 'react-native';
import DownloadService from '../services/DownloadService';

export default function DownloadScreen() {
  const [relatorioId, setRelatorioId] = useState('');
  const [relatorioIds, setRelatorioIds] = useState('');
  const [nomeZip, setNomeZip] = useState('relatorios.zip');
  const [carregando, setCarregando] = useState(false);
  const [statusMensagem, setStatusMensagem] = useState('');
  const [abaMativa, setAbaMativa] = useState('unico');

  const mostrarStatus = (mensagem, tipo = 'info') => {
    setStatusMensagem(mensagem);
    if (tipo === 'erro') {
      Alert.alert('Erro', mensagem);
    } else if (tipo === 'sucesso') {
      Alert.alert('Sucesso', mensagem);
    }
  };

  const handleBaixarRelatorio = async () => {
    if (!relatorioId.trim()) {
      mostrarStatus('Digite um ID válido', 'erro');
      return;
    }

    setCarregando(true);
    try {
      const resultado = await DownloadService.downloadCompleto(relatorioId);
      mostrarStatus(`✅ Relatório baixado: ${resultado.nomeArquivo}`, 'sucesso');
      setRelatorioId('');
    } catch (error) {
      mostrarStatus(`❌ Erro: ${error.message}`, 'erro');
    } finally {
      setCarregando(false);
    }
  };

  const handleBaixarMultiplos = async () => {
    if (!relatorioIds.trim()) {
      mostrarStatus('Digite IDs válidos', 'erro');
      return;
    }

    const ids = relatorioIds
      .split(/[,\n]/)
      .map((id) => parseInt(id.trim()))
      .filter((id) => !isNaN(id));

    if (ids.length === 0) {
      mostrarStatus('Nenhum ID válido encontrado', 'erro');
      return;
    }

    setCarregando(true);
    try {
      const dados = await DownloadService.baixarMultiplos(ids, nomeZip);
      const caminhoArquivo = await DownloadService.salvarArquivo(
        dados.arquivo,
        dados.nomeArquivo
      );
      mostrarStatus(
        `✅ ${dados.quantidade} relatório(s) baixado(s): ${dados.nomeArquivo}`,
        'sucesso'
      );
      setRelatorioIds('');
    } catch (error) {
      mostrarStatus(`❌ Erro: ${error.message}`, 'erro');
    } finally {
      setCarregando(false);
    }
  };

  const handleBaixarComAnexos = async () => {
    if (!relatorioId.trim()) {
      mostrarStatus('Digite um ID válido', 'erro');
      return;
    }

    setCarregando(true);
    try {
      const dados = await DownloadService.baixarComAnexos(relatorioId);
      await DownloadService.salvarArquivo(dados.arquivo, dados.nomeArquivo);
      mostrarStatus(`✅ Relatório com anexos baixado: ${dados.nomeArquivo}`, 'sucesso');
      setRelatorioId('');
    } catch (error) {
      mostrarStatus(`❌ Erro: ${error.message}`, 'erro');
    } finally {
      setCarregando(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.titulo}>📦 Danos Elétricos</Text>
        <Text style={styles.subtitulo}>Download de Relatórios</Text>
      </View>

      {/* Abas */}
      <View style={styles.abas}>
        <TouchableOpacity
          style={[styles.abaBtn, abaMativa === 'unico' && styles.abaAtiva]}
          onPress={() => setAbaMativa('unico')}
        >
          <Text style={[styles.abaBtnText, abaMativa === 'unico' && styles.abaBtnTextAtivo]}>
            📄 Individual
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.abaBtn, abaMativa === 'multiplo' && styles.abaAtiva]}
          onPress={() => setAbaMativa('multiplo')}
        >
          <Text style={[styles.abaBtnText, abaMativa === 'multiplo' && styles.abaBtnTextAtivo]}>
            📚 Múltiplos
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.abaBtn, abaMativa === 'anexos' && styles.abaAtiva]}
          onPress={() => setAbaMativa('anexos')}
        >
          <Text style={[styles.abaBtnText, abaMativa === 'anexos' && styles.abaBtnTextAtivo]}>
            📎 Anexos
          </Text>
        </TouchableOpacity>
      </View>

      {/* TAB: Individual */}
      {abaMativa === 'unico' && (
        <View style={styles.secao}>
          <Text style={styles.secaoTitulo}>📥 Download Individual</Text>

          <TextInput
            style={styles.input}
            placeholder="ID do relatório (ex: 123)"
            value={relatorioId}
            onChangeText={setRelatorioId}
            keyboardType="numeric"
            placeholderTextColor="#999"
          />

          <TouchableOpacity
            style={[styles.botao, carregando && styles.botaoDesabilitado]}
            onPress={handleBaixarRelatorio}
            disabled={carregando}
          >
            {carregando ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.botaoTexto}>⬇️ Baixar</Text>
            )}
          </TouchableOpacity>

          <View style={styles.infoBox}>
            <Text style={styles.infoBoxTexto}>
              💡 Digite o ID do relatório e toque em Baixar
            </Text>
          </View>
        </View>
      )}

      {/* TAB: Múltiplo */}
      {abaMativa === 'multiplo' && (
        <View style={styles.secao}>
          <Text style={styles.secaoTitulo}>📚 Download Múltiplo</Text>

          <Text style={styles.label}>IDs dos Relatórios (um por linha ou separados por vírgula):</Text>
          <TextInput
            style={[styles.input, styles.textarea]}
            placeholder="1&#10;2&#10;3&#10;&#10;ou: 1,2,3"
            value={relatorioIds}
            onChangeText={setRelatorioIds}
            multiline
            placeholderTextColor="#999"
          />

          <Text style={styles.label}>Nome do arquivo ZIP:</Text>
          <TextInput
            style={styles.input}
            placeholder="relatorios.zip"
            value={nomeZip}
            onChangeText={setNomeZip}
            placeholderTextColor="#999"
          />

          <TouchableOpacity
            style={[styles.botao, carregando && styles.botaoDesabilitado]}
            onPress={handleBaixarMultiplos}
            disabled={carregando}
          >
            {carregando ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.botaoTexto}>⬇️ Baixar Todos</Text>
            )}
          </TouchableOpacity>

          <View style={styles.infoBox}>
            <Text style={styles.infoBoxTexto}>
              💡 Compacta vários relatórios em um único arquivo ZIP
            </Text>
          </View>
        </View>
      )}

      {/* TAB: Com Anexos */}
      {abaMativa === 'anexos' && (
        <View style={styles.secao}>
          <Text style={styles.secaoTitulo}>📎 Com Anexos</Text>

          <TextInput
            style={styles.input}
            placeholder="ID do relatório (ex: 123)"
            value={relatorioId}
            onChangeText={setRelatorioId}
            keyboardType="numeric"
            placeholderTextColor="#999"
          />

          <TouchableOpacity
            style={[styles.botao, carregando && styles.botaoDesabilitado]}
            onPress={handleBaixarComAnexos}
            disabled={carregando}
          >
            {carregando ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.botaoTexto}>⬇️ Baixar</Text>
            )}
          </TouchableOpacity>

          <View style={styles.infoBox}>
            <Text style={styles.infoBoxTexto}>
              💡 Inclui relatório, fotos e documentos anexados
            </Text>
          </View>
        </View>
      )}

      {/* Status */}
      {statusMensagem && (
        <View style={styles.statusBox}>
          <Text style={styles.statusTexto}>{statusMensagem}</Text>
        </View>
      )}

      <View style={styles.espacador} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    paddingVertical: 30,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  titulo: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  subtitulo: {
    fontSize: 14,
    color: '#666',
  },
  abas: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
    backgroundColor: '#fff',
  },
  abaBtn: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 10,
    alignItems: 'center',
    borderBottomWidth: 3,
    borderBottomColor: 'transparent',
  },
  abaAtiva: {
    borderBottomColor: '#667eea',
  },
  abaBtnText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#999',
  },
  abaBtnTextAtivo: {
    color: '#667eea',
  },
  secao: {
    padding: 20,
    backgroundColor: '#fff',
    marginTop: 10,
    marginHorizontal: 10,
    borderRadius: 8,
  },
  secaoTitulo: {
    fontSize: 16,
    fontWeight: '600',
    color: '#667eea',
    marginBottom: 15,
  },
  label: {
    fontSize: 12,
    color: '#666',
    marginBottom: 8,
    marginTop: 12,
  },
  input: {
    borderWidth: 2,
    borderColor: '#e0e0e0',
    borderRadius: 6,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 14,
    marginBottom: 12,
    backgroundColor: '#fff',
  },
  textarea: {
    minHeight: 80,
    textAlignVertical: 'top',
  },
  botao: {
    backgroundColor: '#667eea',
    borderRadius: 6,
    paddingVertical: 12,
    paddingHorizontal: 20,
    alignItems: 'center',
    marginTop: 12,
    marginBottom: 12,
  },
  botaoDesabilitado: {
    opacity: 0.7,
  },
  botaoTexto: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  infoBox: {
    backgroundColor: '#f9f9f9',
    borderLeftWidth: 4,
    borderLeftColor: '#667eea',
    padding: 12,
    borderRadius: 4,
    marginTop: 12,
  },
  infoBoxTexto: {
    fontSize: 12,
    color: '#666',
  },
  statusBox: {
    backgroundColor: '#d1ecf1',
    borderColor: '#bee5eb',
    borderWidth: 1,
    borderRadius: 6,
    padding: 12,
    margin: 10,
  },
  statusTexto: {
    color: '#0c5460',
    fontSize: 12,
  },
  espacador: {
    height: 30,
  },
});
