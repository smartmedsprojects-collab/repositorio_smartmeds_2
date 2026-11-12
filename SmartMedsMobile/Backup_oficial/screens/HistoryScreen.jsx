
import React, {
  useState,
  useCallback,
  useMemo,
} from 'react';

import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';

import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import api from '../src/services/api';

// =============================================
// NORMALIZAR TIPO DE MOVIMENTAÇÃO
// =============================================

const normalizarTipo = (item) => {
  const valor = String(
    item?.type ??
    item?.tipo ??
    item?.tipo_movimentacao ??
    item?.tipoMovimentacao ??
    ''
  )
    .trim()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toUpperCase();

  if (
    valor === 'ENTRADA' ||
    valor.includes('ENTRADA')
  ) {
    return 'Entrada';
  }

  if (
    valor === 'SAIDA' ||
    valor.includes('SAIDA')
  ) {
    return 'Saída';
  }

  return 'Movimentação';
};

// =============================================
// NORMALIZAR REGISTRO RECEBIDO DA API
// =============================================

const normalizarMovimentacao = (item, index) => {
  const tipo = normalizarTipo(item);

  const quantidadeBruta =
    item?.quantity ??
    item?.quantidade ??
    item?.qtd;

  const quantidade = Number(quantidadeBruta);

  const dataBruta =
    item?.date ??
    item?.data_movimentacao ??
    item?.data ??
    item?.created_at;

  const horaBruta =
    item?.hour ??
    item?.hora;

  let dataFormatada = '';
  let horaFormatada = horaBruta
    ? String(horaBruta)
    : '';

  if (dataBruta) {
    if (
      typeof dataBruta === 'string' &&
      /^\d{2}\/\d{2}\/\d{4}$/.test(dataBruta)
    ) {
      dataFormatada = dataBruta;
    } else {
      const data =
        dataBruta instanceof Date
          ? dataBruta
          : new Date(
              String(dataBruta).replace(' ', 'T')
            );

      if (!Number.isNaN(data.getTime())) {
        if (!dataFormatada) {
          dataFormatada =
            data.toLocaleDateString('pt-BR');
        }

        if (!horaFormatada) {
          horaFormatada =
            data.toLocaleTimeString('pt-BR', {
              hour: '2-digit',
              minute: '2-digit',
            });
        }
      }
    }
  }

  const produtoId =
    item?.produto_id ??
    item?.product_id ??
    item?.id_produto;

  const produto =
    item?.product ??
    item?.produto_nome ??
    item?.nome_produto ??
    item?.nomeProduto;

  const marca =
    item?.brand ??
    item?.produto_marca ??
    item?.marca ??
    '';

  return {
    ...item,

    id:
      item?.id ??
      item?.movimentacao_id ??
      `movimentacao-${index}`,

    product:
      produto ||
      (
        produtoId != null
          ? `Produto #${produtoId}`
          : 'Produto não informado'
      ),

    brand: marca,
    type: tipo,

    quantity:
      Number.isFinite(quantidade)
        ? quantidade
        : 0,

    date: dataFormatada || '--/--/----',
    hour: horaFormatada || '--:--',
  };
};

// =============================================
// TELA DE HISTÓRICO
// =============================================

export default function MovimentacaoScreen() {
  const [search, setSearch] = useState('');
  const [movimentacao, setMovimentacao] = useState([]);
  const [loading, setLoading] = useState(false);

  // ===========================================
  // CARREGAR HISTÓRICO
  // ===========================================

  const loadMovimentacao = useCallback(async () => {
    try {
      setLoading(true);

      console.log(
        'Buscando histórico: GET /movimentacao'
      );

      const response = await api.get('/movimentacao');

      const dados = Array.isArray(response.data)
        ? response.data
        : Array.isArray(response.data?.movimentacao)
          ? response.data.movimentacao
          : Array.isArray(response.data?.historico)
            ? response.data.historico
            : [];

      const normalizados = dados.map(
        (item, index) =>
          normalizarMovimentacao(item, index)
      );

      console.log(
        'Total de movimentações:',
        normalizados.length
      );

      console.log(
        'Histórico recebido:',
        normalizados
      );

      setMovimentacao(normalizados);
    } catch (error) {
      console.error(
        'Erro ao carregar histórico:',
        error.response?.data || error.message
      );

      setMovimentacao([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // ===========================================
  // ATUALIZAR AO ABRIR A TELA
  // ===========================================

  useFocusEffect(
    useCallback(() => {
      loadMovimentacao();
    }, [loadMovimentacao])
  );

  // ===========================================
  // CONTADOR DE ENTRADAS
  // ===========================================

  const entriesCount = useMemo(() => {
    return movimentacao.filter(
      (item) => item.type === 'Entrada'
    ).length;
  }, [movimentacao]);

  // ===========================================
  // CONTADOR DE SAÍDAS
  // ===========================================

  const exitsCount = useMemo(() => {
    return movimentacao.filter(
      (item) => item.type === 'Saída'
    ).length;
  }, [movimentacao]);

  // ===========================================
  // PESQUISA
  // ===========================================

  const searchText = search
    .trim()
    .toLocaleLowerCase('pt-BR');

  const filteredMovimentacao = useMemo(() => {
    if (!searchText) {
      return movimentacao;
    }

    return movimentacao.filter((item) => {
      const campos = [
        item.product,
        item.brand,
        item.type,
        item.quantity,
        item.date,
        item.hour,
      ];

      return campos.some((campo) =>
        String(campo ?? '')
          .toLocaleLowerCase('pt-BR')
          .includes(searchText)
      );
    });
  }, [movimentacao, searchText]);

  // ===========================================
  // RENDERIZAR CADA MOVIMENTAÇÃO
  // ===========================================

  const renderMovimentacaoItem = ({ item }) => {
    const entrada = item.type === 'Entrada';

    return (
      <View style={styles.card}>
        <View
          style={[
            styles.iconContainer,
            {
              backgroundColor: entrada
                ? '#E6F7F2'
                : '#FDECEA',
            },
          ]}
        >
          <Ionicons
            name={
              entrada
                ? 'arrow-down-circle'
                : 'arrow-up-circle'
            }
            size={30}
            color={
              entrada
                ? '#1A9E72'
                : '#D94040'
            }
          />
        </View>

        <View style={styles.info}>
          <View style={styles.topRow}>
            <Text
              style={styles.product}
              numberOfLines={2}
            >
              {item.product}
            </Text>

            <Text
              style={[
                styles.type,
                {
                  color: entrada
                    ? '#0E6649'
                    : item.type === 'Saída'
                      ? '#8B1A1A'
                      : '#5A6B7D',
                },
              ]}
            >
              {item.type}
            </Text>
          </View>

          {!!item.brand && (
            <Text
              style={styles.brand}
              numberOfLines={1}
            >
              {item.brand}
            </Text>
          )}

          <View style={styles.detailsRow}>
            <Text style={styles.quantity}>
              Quantidade: {item.quantity}
            </Text>

            <Text style={styles.date}>
              {item.date}
            </Text>
          </View>

          <Text style={styles.hour}>
            {item.hour}
          </Text>
        </View>
      </View>
    );
  };

  // ===========================================
  // INTERFACE
  // ===========================================

  return (
    <View style={styles.container}>
      {/* CABEÇALHO */}

      <View style={styles.header}>
        <View>
          <Text style={styles.title}>
            Histórico
          </Text>

          <Text style={styles.subtitle}>
            Movimentações do estoque
          </Text>
        </View>

        <TouchableOpacity
          accessibilityRole="button"
          accessibilityLabel="Atualizar histórico"
          style={styles.filterButton}
          onPress={loadMovimentacao}
          disabled={loading}
        >
          <Ionicons
            name="calendar-outline"
            size={24}
            color="#FFFFFF"
          />
        </TouchableOpacity>
      </View>

      {/* PESQUISA */}

      <View style={styles.searchContainer}>
        <Ionicons
          name="search"
          size={22}
          color="#8FA0B3"
        />

        <TextInput
          style={styles.searchInput}
          placeholder="Pesquisar movimentações..."
          placeholderTextColor="#8FA0B3"
          value={search}
          onChangeText={setSearch}
          autoCapitalize="none"
          autoCorrect={false}
          returnKeyType="search"
        />

        {!!search && (
          <TouchableOpacity
            onPress={() => setSearch('')}
            accessibilityLabel="Limpar pesquisa"
          >
            <Ionicons
              name="close-circle"
              size={20}
              color="#8FA0B3"
            />
          </TouchableOpacity>
        )}
      </View>

      {/* CONTADORES */}

      <View style={styles.statsContainer}>
        <View style={styles.statsCardGreen}>
          <Ionicons
            name="arrow-down-circle"
            size={24}
            color="#1A9E72"
          />

          <Text style={styles.statsNumber}>
            {entriesCount}
          </Text>

          <Text style={styles.statsLabel}>
            Entradas
          </Text>
        </View>

        <View style={styles.statsCardRed}>
          <Ionicons
            name="arrow-up-circle"
            size={24}
            color="#D94040"
          />

          <Text style={styles.statsNumber}>
            {exitsCount}
          </Text>

          <Text style={styles.statsLabel}>
            Saídas
          </Text>
        </View>
      </View>

      {/* LISTA */}

      {loading && movimentacao.length === 0 ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator
            size="large"
            color="#0F4C7A"
          />

          <Text style={styles.loadingText}>
            Carregando movimentações...
          </Text>
        </View>
      ) : (
        <FlatList
          data={filteredMovimentacao}
          keyExtractor={(item, index) =>
            String(
              item.id ?? `movimentacao-${index}`
            )
          }
          renderItem={renderMovimentacaoItem}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
          contentContainerStyle={
            filteredMovimentacao.length === 0
              ? styles.emptyList
              : styles.list
          }
          refreshControl={
            <RefreshControl
              refreshing={loading}
              onRefresh={loadMovimentacao}
              colors={['#0F4C7A']}
            />
          }
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Ionicons
                name={
                  searchText
                    ? 'search-outline'
                    : 'time-outline'
                }
                size={55}
                color="#8FA0B3"
              />

              <Text style={styles.emptyTitle}>
                {searchText
                  ? 'Nenhuma movimentação encontrada'
                  : 'Nenhuma movimentação'}
              </Text>

              <Text style={styles.emptyText}>
                {searchText
                  ? 'Tente pesquisar por outro produto ou tipo de movimentação.'
                  : 'As entradas e saídas do estoque aparecerão aqui.'}
              </Text>

              {!searchText && (
                <TouchableOpacity
                  style={styles.retryButton}
                  onPress={loadMovimentacao}
                >
                  <Text style={styles.retryButtonText}>
                    Atualizar histórico
                  </Text>
                </TouchableOpacity>
              )}
            </View>
          }
        />
      )}
    </View>
  );
}

// =============================================
// ESTILOS
// =============================================

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F4F7FA',
    paddingHorizontal: 20,
  },

  header: {
    marginTop: 55,
    marginBottom: 25,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },

  title: {
    color: '#1A2332',
    fontSize: 32,
    fontWeight: 'bold',
  },

  subtitle: {
    color: '#5A6B7D',
    marginTop: 5,
    fontSize: 15,
  },

  filterButton: {
    width: 52,
    height: 52,
    backgroundColor: '#0F4C7A',
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },

  searchContainer: {
    backgroundColor: '#EDF1F5',
    minHeight: 56,
    borderRadius: 20,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 18,
    marginBottom: 22,
    borderWidth: 1,
    borderColor: '#D8E3ED',
  },

  searchInput: {
    flex: 1,
    marginLeft: 10,
    color: '#1A2332',
    fontSize: 16,
    paddingVertical: 12,
  },

  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 22,
  },

  statsCardGreen: {
    width: '48%',
    backgroundColor: '#E6F7F2',
    borderRadius: 24,
    padding: 18,
    borderWidth: 1,
    borderColor: '#C9EDE1',
  },

  statsCardRed: {
    width: '48%',
    backgroundColor: '#FDECEA',
    borderRadius: 24,
    padding: 18,
    borderWidth: 1,
    borderColor: '#F4C9C6',
  },

  statsNumber: {
    color: '#1A2332',
    fontSize: 28,
    fontWeight: 'bold',
    marginTop: 10,
  },

  statsLabel: {
    color: '#5A6B7D',
    marginTop: 6,
  },

  list: {
    paddingBottom: 40,
  },

  emptyList: {
    flexGrow: 1,
    paddingBottom: 40,
  },

  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 16,
    marginBottom: 16,
    flexDirection: 'row',
    borderWidth: 1,
    borderColor: '#D8E3ED',
  },

  iconContainer: {
    width: 58,
    height: 58,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 14,
  },

  info: {
    flex: 1,
    minWidth: 0,
  },

  topRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },

  product: {
    color: '#1A2332',
    fontSize: 16,
    fontWeight: 'bold',
    flex: 1,
    marginRight: 8,
  },

  brand: {
    color: '#718096',
    fontSize: 13,
    marginTop: 4,
  },

  type: {
    fontSize: 13,
    fontWeight: 'bold',
    marginLeft: 4,
  },

  detailsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 10,
    flexWrap: 'wrap',
  },

  quantity: {
    color: '#5A6B7D',
    fontSize: 14,
    marginRight: 8,
  },

  date: {
    color: '#8FA0B3',
    fontSize: 12,
  },

  hour: {
    color: '#8FA0B3',
    marginTop: 7,
    fontSize: 12,
  },

  loadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingBottom: 100,
  },

  loadingText: {
    color: '#5A6B7D',
    fontSize: 14,
    marginTop: 12,
  },

  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 30,
    paddingTop: 70,
  },

  emptyTitle: {
    color: '#1A2332',
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 15,
    textAlign: 'center',
  },

  emptyText: {
    color: '#8FA0B3',
    fontSize: 14,
    textAlign: 'center',
    marginTop: 8,
    lineHeight: 21,
  },

  retryButton: {
    backgroundColor: '#0F4C7A',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 12,
    marginTop: 20,
  },

  retryButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: 'bold',
  },
});
