
import React, { useState, useCallback } from 'react';

import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';

import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import api from '../src/services/api';

export default function HomeScreen({ navigation }) {
  const [dashboardData, setDashboardData] = useState({
    totalProdutos: 0,
    totalUnidades: 0,
    lowStockCount: 0,
    recentActivities: [],
  });

  const [loading, setLoading] = useState(false);

  // ==========================================
  // CARREGAR DADOS DO DASHBOARD
  // ==========================================

  const loadDashboard = useCallback(async () => {
    try {
      setLoading(true);

      // Busca os produtos cadastrados.
      const produtosResponse = await api.get('/produtos');

      const produtos = Array.isArray(produtosResponse.data)
        ? produtosResponse.data
        : [];

      // Total de produtos cadastrados.
      const totalProdutos = produtos.length;

      // Soma das unidades existentes em estoque.
      const totalUnidades = produtos.reduce((total, produto) => {
        const quantidade = Number(produto.quantidade) || 0;
        return total + quantidade;
      }, 0);

      // Conta os produtos com estoque baixo.
      const lowStockCount = produtos.filter((produto) => {
        return (Number(produto.quantidade) || 0) <= 5;
      }).length;

      // Busca as atividades recentes.
      let recentActivities = [];

      try {
        const dashboardResponse = await api.get('/dashboard');

        const dadosDashboard = dashboardResponse.data || {};

        // Compatível com os nomes usados pelo servidor.
        const atividades =
          dadosDashboard.recentActivities ||
          dadosDashboard.movimentacoes ||
          dadosDashboard.recentActivities ||
          [];

        if (Array.isArray(atividades)) {
          recentActivities = atividades.map((item, index) => {
            const tipoOriginal = String(
              item.type ??
              item.tipo_movimentacao ??
              item.tipo ??
              ''
            )
              .trim()
              .normalize('NFD')
              .replace(/[\u0300-\u036f]/g, '')
              .toUpperCase();

            let type = 'Movimentação';

            if (tipoOriginal.includes('ENTRADA')) {
              type = 'Entrada';
            } else if (tipoOriginal.includes('SAIDA')) {
              type = 'Saída';
            }

            return {
              id: item.id ?? `atividade-${index}`,
              type,
              quantity: Number(
                item.quantity ?? item.quantidade
              ) || 0,
              product:
                item.product ||
                item.produto_nome ||
                item.nome_produto ||
                (
                  item.produto_id
                    ? `Produto #${item.produto_id}`
                    : 'Produto não informado'
                ),
            };
          });
        }
      } catch (error) {
        console.log(
          'Não foi possível carregar as atividades:',
          error.response?.data || error.message
        );
      }

      setDashboardData({
        totalProdutos,
        totalUnidades,
        lowStockCount,
        recentActivities,
      });

      console.log('Dashboard atualizado:', {
        totalProdutos,
        totalUnidades,
        lowStockCount,
        recentActivities,
      });
    } catch (error) {
      console.error(
        'Erro ao carregar Dashboard:',
        error.response?.data || error.message
      );
    } finally {
      setLoading(false);
    }
  }, []);

  // Atualiza ao abrir ou voltar para a tela.
  useFocusEffect(
    useCallback(() => {
      loadDashboard();
    }, [loadDashboard])
  );

  // ==========================================
  // INTERFACE
  // ==========================================

  return (
    <ScrollView
      style={styles.container}
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl
          refreshing={loading}
          onRefresh={loadDashboard}
          colors={['#1A6FA8']}
        />
      }
    >
      {/* CABEÇALHO */}

      <View style={styles.header}>
        <View>
          <Text style={styles.welcome}>Bem-vindo</Text>
          <Text style={styles.userName}>
            Sistema de Estoque
          </Text>
        </View>

        <TouchableOpacity
          style={styles.notification}
          onPress={loadDashboard}
          accessibilityLabel="Atualizar dashboard"
        >
          <Ionicons
            name="notifications-outline"
            size={24}
            color="#FFFFFF"
          />
        </TouchableOpacity>
      </View>

      {/* TOTAL DE PRODUTOS CADASTRADOS */}

      <View style={styles.balanceCard}>
        <Text style={styles.balanceLabel}>
          Produtos em Estoque
        </Text>

        {loading && dashboardData.totalProdutos === 0 ? (
          <ActivityIndicator
            size="large"
            color="#1A6FA8"
            style={styles.loader}
          />
        ) : (
          <Text style={styles.balanceValue}>
            {dashboardData.totalProdutos}
          </Text>
        )}

        <View style={styles.balanceFooter}>
          <Ionicons
            name="trending-up"
            size={18}
            color="#1A9E72"
          />

          <Text style={styles.balanceGrowth}>
            Atualizado com o BD
          </Text>
        </View>
      </View>

      {/* INDICADORES */}

      <View style={styles.cardsContainer}>
        {/* UNIDADES TOTAIS */}

        <View style={styles.smallCard}>
          <View style={styles.iconBlue}>
            <Ionicons
              name="cube"
              size={24}
              color="#1A6FA8"
            />
          </View>

          <Text style={styles.cardNumber}>
            {dashboardData.totalUnidades}
          </Text>

          <Text style={styles.cardLabel}>
            Unidades Totais
          </Text>
        </View>

        {/* ESTOQUE BAIXO */}

        <View style={styles.smallCard}>
          <View style={styles.iconRed}>
            <Ionicons
              name="alert-circle"
              size={24}
              color="#D94040"
            />
          </View>

          <Text style={styles.cardNumber}>
            {dashboardData.lowStockCount}
          </Text>

          <Text style={styles.cardLabel}>
            Estoque Baixo
          </Text>
        </View>
      </View>

      {/* OPERAÇÕES */}

      <Text style={styles.sectionTitle}>
        Operações
      </Text>

      <TouchableOpacity
        style={styles.actionButton}
        onPress={() => navigation.navigate('Produtos')}
      >
        <View style={styles.buttonContent}>
          <Ionicons
            name="cube-outline"
            size={26}
            color="#1A6FA8"
          />

          <View style={styles.buttonTextContainer}>
            <Text style={styles.buttonTitle}>
              Produtos
            </Text>

            <Text style={styles.buttonSubtitle}>
              Visualizar estoque completo
            </Text>
          </View>
        </View>

        <Ionicons
          name="chevron-forward"
          size={22}
          color="#8FA0B3"
        />
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.actionButton}
        onPress={() => navigation.navigate('Entrada')}
      >
        <View style={styles.buttonContent}>
          <Ionicons
            name="arrow-down-circle-outline"
            size={26}
            color="#1A9E72"
          />

          <View style={styles.buttonTextContainer}>
            <Text style={styles.buttonTitle}>
              Entrada de Estoque
            </Text>

            <Text style={styles.buttonSubtitle}>
              Registrar novos produtos
            </Text>
          </View>
        </View>

        <Ionicons
          name="chevron-forward"
          size={22}
          color="#8FA0B3"
        />
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.actionButton}
        onPress={() => navigation.navigate('Saída')}
      >
        <View style={styles.buttonContent}>
          <Ionicons
            name="arrow-up-circle-outline"
            size={26}
            color="#D94040"
          />

          <View style={styles.buttonTextContainer}>
            <Text style={styles.buttonTitle}>
              Saída de Estoque
            </Text>

            <Text style={styles.buttonSubtitle}>
              Registrar retirada
            </Text>
          </View>
        </View>

        <Ionicons
          name="chevron-forward"
          size={22}
          color="#8FA0B3"
        />
      </TouchableOpacity>

      {/* ATIVIDADES RECENTES */}

      <View style={styles.activitiesHeader}>
        <Text style={styles.sectionTitle}>
          Atividades Recentes
        </Text>

        <TouchableOpacity
          onPress={() => navigation.navigate('Histórico')}
        >
          <Text style={styles.seeAll}>
            Ver histórico
          </Text>
        </TouchableOpacity>
      </View>

      {dashboardData.recentActivities.length > 0 ? (
        dashboardData.recentActivities.map((item) => {
          const entrada = item.type === 'Entrada';

          return (
            <View
              key={String(item.id)}
              style={styles.activityCard}
            >
              <View
                style={[
                  styles.activityIcon,
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
                  size={23}
                  color={
                    entrada
                      ? '#1A9E72'
                      : '#D94040'
                  }
                />
              </View>

              <View style={styles.activityInfo}>
                <Text style={styles.activityText}>
                  {item.type} de {item.quantity} unidade(s)
                </Text>

                <Text
                  style={styles.activityProduct}
                  numberOfLines={1}
                >
                  {item.product}
                </Text>
              </View>
            </View>
          );
        })
      ) : (
        <View style={styles.emptyActivities}>
          <Ionicons
            name="time-outline"
            size={28}
            color="#8FA0B3"
          />

          <Text style={styles.emptyActivitiesText}>
            Nenhuma atividade recente encontrada.
          </Text>
        </View>
      )}

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

// ==============================================
// ESTILOS
// ==============================================

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F4F7FA',
    paddingHorizontal: 20,
  },

  header: {
    marginTop: 60,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },

  welcome: {
    color: '#5A6B7D',
    fontSize: 15,
  },

  userName: {
    color: '#1A2332',
    fontSize: 28,
    fontWeight: 'bold',
    marginTop: 3,
  },

  notification: {
    width: 50,
    height: 50,
    backgroundColor: '#1A6FA8',
    borderRadius: 15,
    justifyContent: 'center',
    alignItems: 'center',
  },

  balanceCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 30,
    padding: 25,
    marginTop: 30,
    minHeight: 150,
    justifyContent: 'space-between',
  },

  balanceLabel: {
    color: '#0C3D61',
    fontSize: 16,
  },

  balanceValue: {
    color: '#1A2332',
    fontSize: 42,
    fontWeight: 'bold',
    marginTop: 10,
  },

  loader: {
    marginTop: 12,
    alignSelf: 'flex-start',
  },

  balanceFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
  },

  balanceGrowth: {
    color: '#1A9E72',
    marginLeft: 6,
    fontWeight: '600',
  },

  cardsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 22,
  },

  smallCard: {
    backgroundColor: '#FFFFFF',
    width: '48%',
    minHeight: 150,
    borderRadius: 22,
    padding: 18,
    justifyContent: 'space-between',
  },

  iconBlue: {
    width: 45,
    height: 45,
    backgroundColor: '#E8F3FB',
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
  },

  iconRed: {
    width: 45,
    height: 45,
    backgroundColor: '#FDECEA',
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
  },

  cardNumber: {
    color: '#1A2332',
    fontSize: 27,
    fontWeight: 'bold',
    marginTop: 12,
  },

  cardLabel: {
    color: '#5A6B7D',
    marginTop: 5,
    fontSize: 13,
  },

  sectionTitle: {
    color: '#1A2332',
    fontSize: 21,
    fontWeight: 'bold',
    marginTop: 32,
    marginBottom: 16,
  },

  actionButton: {
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 20,
    marginBottom: 14,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },

  buttonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },

  buttonTextContainer: {
    marginLeft: 15,
    flex: 1,
  },

  buttonTitle: {
    color: '#1A2332',
    fontSize: 17,
    fontWeight: 'bold',
  },

  buttonSubtitle: {
    color: '#5A6B7D',
    marginTop: 4,
    fontSize: 13,
  },

  activitiesHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },

  seeAll: {
    color: '#1A6FA8',
    fontWeight: '600',
    fontSize: 13,
  },

  activityCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    padding: 15,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#D8E3ED',
  },

  activityIcon: {
    width: 44,
    height: 44,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },

  activityInfo: {
    flex: 1,
    marginLeft: 12,
  },

  activityText: {
    color: '#1A2332',
    fontSize: 15,
    fontWeight: '600',
  },

  activityProduct: {
    color: '#5A6B7D',
    fontSize: 13,
    marginTop: 4,
  },

  emptyActivities: {
    backgroundColor: '#FFFFFF',
    padding: 24,
    borderRadius: 18,
    alignItems: 'center',
  },

  emptyActivitiesText: {
    color: '#718096',
    fontSize: 14,
    marginTop: 10,
    textAlign: 'center',
  },
});
