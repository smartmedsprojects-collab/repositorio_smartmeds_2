import React, { useState, useCallback } from 'react';

import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TextInput,
  TouchableOpacity,
  Alert,
} from 'react-native';

import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';

import api from '../src/services/api';


export default function ProductsScreen() {

  const [search, setSearch] = useState('');
  const [products, setProducts] = useState([]);
  const [quantidades, setQuantidades] = useState({});


  // ==============================
  // BUSCAR PRODUTOS
  // ==============================

  const loadProducts = async () => {

    try {

      const response = await api.get('/produtos');

      console.log('Produtos recebidos:', response.data);

      setProducts(response.data);

    } catch (error) {

      console.log('Erro ao buscar produtos:', error);

      Alert.alert(
        'Erro',
        'Não foi possível carregar os produtos.'
      );

    }

  };


  useFocusEffect(

    useCallback(() => {

      loadProducts();

    }, [])

  );


  // ==============================
  // ALTERAR QUANTIDADE
  // ==============================

  const alterarQuantidade = (id, valor) => {

    setQuantidades((prev) => {

      const quantidadeAtual = prev[id] || 1;

      const novaQuantidade =
        quantidadeAtual + valor;

      return {
        ...prev,
        [id]: Math.max(1, novaQuantidade),
      };

    });

  };


  // ==============================
  // REGISTRAR ENTRADA
  // ==============================

  const registrarEntrada = async (item) => {

    const quantidade =
      quantidades[item.id] || 1;

    try {

      const response = await api.post(
        '/entradas',
        {
          produto_id: item.id,
          quantidade: quantidade,
        }
      );

      console.log(
        'Entrada registrada:',
        response.data
      );

      Alert.alert(
        'Entrada registrada',
        `${quantidade} unidade(s) adicionada(s) ao estoque.`
      );

      await loadProducts();

      setQuantidades((prev) => ({
        ...prev,
        [item.id]: 1,
      }));

    } catch (error) {

      console.log(
        'Erro na entrada:',
        error.response?.data || error.message
      );

      Alert.alert(
        'Erro',
        error.response?.data?.message ||
          'Não foi possível registrar a entrada.'
      );

    }

  };


  // ==============================
  // REGISTRAR SAÍDA
  // ==============================

  const registrarSaida = async (item) => {

    const quantidade =
      quantidades[item.id] || 1;

    const estoqueAtual =
      Number(item.quantidade) || 0;


    // Evita tentar retirar mais que o estoque
    if (quantidade > estoqueAtual) {

      Alert.alert(
        'Estoque insuficiente',
        `O estoque atual é de ${estoqueAtual} unidade(s).`
      );

      return;

    }


    try {

      const response = await api.post(
        '/saidas',
        {
          produto_id: item.id,
          quantidade: quantidade,
        }
      );

      console.log(
        'Saída registrada:',
        response.data
      );

      Alert.alert(
        'Saída registrada',
        `${quantidade} unidade(s) retirada(s) do estoque.`
      );

      await loadProducts();

      setQuantidades((prev) => ({
        ...prev,
        [item.id]: 1,
      }));

    } catch (error) {

      console.log(
        'Erro na saída:',
        error.response?.data || error.message
      );

      Alert.alert(
        'Erro',
        error.response?.data?.message ||
          'Não foi possível registrar a saída.'
      );

    }

  };


  // ==============================
  // FILTRO
  // ==============================

  const filteredProducts = products.filter((item) => {

    const nome =
      String(item.nome || '').toLowerCase();

    const marca =
      String(item.marca || '').toLowerCase();

    const textoPesquisa =
      search.toLowerCase();

    return (
      nome.includes(textoPesquisa) ||
      marca.includes(textoPesquisa)
    );

  });


  // ==============================
  // CARD DO PRODUTO
  // ==============================

  const renderProduct = ({ item }) => {

    const quantidade =
      Number(item.quantidade) || 0;

    const estoqueBaixo =
      quantidade <= 5;


    return (

      <View style={styles.card}>

        {/* CABEÇALHO DO CARD */}

        <View style={styles.cardHeader}>

          <View style={styles.titleContainer}>

            <Text
              style={styles.productName}
              numberOfLines={1}
            >
              {item.nome}
            </Text>

            <Text
              style={styles.brand}
              numberOfLines={1}
            >
              {item.marca || 'Marca não informada'}
            </Text>

          </View>


          {/* STATUS */}

          <View
            style={[
              styles.statusBadge,
              estoqueBaixo
                ? styles.lowStockBadge
                : styles.availableBadge,
            ]}
          >

            <View
              style={[
                styles.statusDot,
                estoqueBaixo
                  ? styles.lowStockDot
                  : styles.availableDot,
              ]}
            />

            <Text
              style={[
                styles.statusText,
                estoqueBaixo
                  ? styles.lowStockText
                  : styles.availableText,
              ]}
            >
              {estoqueBaixo
                ? 'Estoque baixo'
                : 'Disponível'}
            </Text>

          </View>

        </View>


        {/* LINHA DIVISÓRIA */}

        <View style={styles.divider} />


        {/* INFORMAÇÕES */}

        <View style={styles.infoGrid}>

          {/* ESTOQUE */}

          <View style={styles.infoItem}>

            <View style={styles.iconBox}>

              <Ionicons
                name="cube-outline"
                size={19}
                color="#1a6fa8"
              />

            </View>

            <View>

              <Text style={styles.infoLabel}>
                Estoque
              </Text>

              <Text style={styles.infoValue}>
                {quantidade}{' '}
                {item.unidade_medida || ''}
              </Text>

            </View>

          </View>


          {/* VALIDADE */}

          <View style={styles.infoItem}>

            <View style={styles.iconBox}>

              <Ionicons
                name="calendar-outline"
                size={19}
                color="#1a6fa8"
              />

            </View>

            <View>

              <Text style={styles.infoLabel}>
                Validade
              </Text>

              <Text style={styles.infoValue}>

                {item.data_de_validade
                  ? new Date(
                      item.data_de_validade
                    ).toLocaleDateString('pt-BR')
                  : 'Não informada'}

              </Text>

            </View>

          </View>

        </View>


        {/* SEGUNDA LINHA */}

        <View style={styles.secondaryInfo}>

          <View style={styles.secondaryItem}>

            <Ionicons
              name="barcode-outline"
              size={17}
              color="#718096"
            />

            <Text style={styles.secondaryText}>

              Código #{item.id}

            </Text>

          </View>


          <View style={styles.secondaryItem}>

            <Ionicons
              name="cube-outline"
              size={17}
              color="#718096"
            />

            <Text
              style={styles.secondaryText}
              numberOfLines={1}
            >
              {item.especificacao ||
                'Sem especificação'}
            </Text>

          </View>

        </View>


        {/* ============================== */}
        {/* CONTROLE DE ENTRADA / SAÍDA */}
        {/* ============================== */}

        <View style={styles.movementContainer}>

          {/* QUANTIDADE */}

          <View style={styles.quantityControl}>

            <TouchableOpacity
              style={styles.quantityButton}
              onPress={() =>
                alterarQuantidade(
                  item.id,
                  -1
                )
              }
            >

              <Ionicons
                name="remove"
                size={18}
                color="#1a6fa8"
              />

            </TouchableOpacity>


            <Text style={styles.quantityText}>

              {quantidades[item.id] || 1}

            </Text>


            <TouchableOpacity
              style={styles.quantityButton}
              onPress={() =>
                alterarQuantidade(
                  item.id,
                  1
                )
              }
            >

              <Ionicons
                name="add"
                size={18}
                color="#1a6fa8"
              />

            </TouchableOpacity>

          </View>


          {/* ENTRADA */}

          <TouchableOpacity
            style={styles.entryButton}
            onPress={() =>
              registrarEntrada(item)
            }
          >

            <Ionicons
              name="arrow-down"
              size={17}
              color="#ffffff"
            />

            <Text style={styles.entryButtonText}>
              Entrada
            </Text>

          </TouchableOpacity>


          {/* SAÍDA */}

          <TouchableOpacity
            style={styles.exitButton}
            onPress={() =>
              registrarSaida(item)
            }
          >

            <Ionicons
              name="arrow-up"
              size={17}
              color="#ffffff"
            />

            <Text style={styles.exitButtonText}>
              Saída
            </Text>

          </TouchableOpacity>

        </View>

      </View>

    );

  };


  // ==============================
  // TELA
  // ==============================

  return (

    <View style={styles.container}>

      {/* CABEÇALHO */}

      <View style={styles.header}>

        <View>

          <Text style={styles.title}>
            Entrada
          </Text>

          <Text style={styles.subtitle}>
            Consulte os produtos cadastrados
          </Text>

        </View>


        <View style={styles.counter}>

          <Text style={styles.counterNumber}>
            {products.length}
          </Text>

          <Text style={styles.counterLabel}>
            itens
          </Text>

        </View>

      </View>


      {/* PESQUISA */}

      <View style={styles.searchContainer}>

        <Ionicons
          name="search-outline"
          size={21}
          color="#718096"
        />

        <TextInput
          style={styles.searchInput}
          placeholder="Pesquisar por nome ou marca..."
          placeholderTextColor="#9aa8b7"
          value={search}
          onChangeText={setSearch}
        />

        {search.length > 0 && (

          <TouchableOpacity
            onPress={() =>
              setSearch('')
            }
          >

            <Ionicons
              name="close-circle"
              size={20}
              color="#9aa8b7"
            />

          </TouchableOpacity>

        )}

      </View>


      {/* LISTA */}

      <FlatList

        data={filteredProducts}

        keyExtractor={(item) =>
          item.id.toString()
        }

        renderItem={renderProduct}

        showsVerticalScrollIndicator={false}

        contentContainerStyle={
          styles.listContent
        }


        ListEmptyComponent={

          <View style={styles.emptyContainer}>

            <Ionicons
              name="cube-outline"
              size={52}
              color="#a5b3c1"
            />

            <Text style={styles.emptyTitle}>
              Nenhum produto encontrado
            </Text>

            <Text style={styles.emptyText}>

              {search
                ? 'Tente pesquisar por outro nome ou marca.'
                : 'Não existem produtos cadastrados.'}

            </Text>

          </View>

        }

      />

    </View>

  );

}


// =====================================================
// ESTILOS
// =====================================================

const styles = StyleSheet.create({

  container: {

    flex: 1,

    backgroundColor: '#f5f7fa',

    paddingHorizontal: 20,

  },


  // ==============================
  // CABEÇALHO
  // ==============================

  header: {

    marginTop: 55,

    marginBottom: 22,

    flexDirection: 'row',

    justifyContent: 'space-between',

    alignItems: 'center',

  },


  title: {

    fontSize: 31,

    fontWeight: '800',

    color: '#17212b',

  },


  subtitle: {

    fontSize: 14,

    color: '#718096',

    marginTop: 5,

  },


  counter: {

    backgroundColor: '#e8f2f8',

    borderRadius: 14,

    paddingHorizontal: 14,

    paddingVertical: 9,

    alignItems: 'center',

    minWidth: 58,

  },


  counterNumber: {

    fontSize: 18,

    fontWeight: '800',

    color: '#1a6fa8',

  },


  counterLabel: {

    fontSize: 11,

    color: '#718096',

    marginTop: 1,

  },


  // ==============================
  // PESQUISA
  // ==============================

  searchContainer: {

    height: 56,

    backgroundColor: '#ffffff',

    borderRadius: 16,

    borderWidth: 1,

    borderColor: '#e0e6ec',

    flexDirection: 'row',

    alignItems: 'center',

    paddingHorizontal: 16,

    marginBottom: 18,

  },


  searchInput: {

    flex: 1,

    marginLeft: 10,

    marginRight: 8,

    color: '#17212b',

    fontSize: 15,

  },


  // ==============================
  // LISTA
  // ==============================

  listContent: {

    paddingBottom: 40,

  },


  // ==============================
  // CARD
  // ==============================

  card: {

    backgroundColor: '#ffffff',

    borderRadius: 20,

    borderWidth: 1,

    borderColor: '#e1e7ed',

    padding: 18,

    marginBottom: 14,

    shadowColor: '#000',

    shadowOffset: {
      width: 0,
      height: 2,
    },

    shadowOpacity: 0.04,

    shadowRadius: 5,

    elevation: 2,

  },


  // ==============================
  // CABEÇALHO CARD
  // ==============================

  cardHeader: {

    flexDirection: 'row',

    justifyContent: 'space-between',

    alignItems: 'flex-start',

  },


  titleContainer: {

    flex: 1,

    paddingRight: 10,

  },


  productName: {

    color: '#17212b',

    fontSize: 18,

    fontWeight: '700',

  },


  brand: {

    color: '#718096',

    fontSize: 14,

    marginTop: 4,

  },


  // ==============================
  // STATUS
  // ==============================

  statusBadge: {

    flexDirection: 'row',

    alignItems: 'center',

    borderRadius: 20,

    paddingHorizontal: 10,

    paddingVertical: 7,

  },


  availableBadge: {

    backgroundColor: '#e8f7f1',

  },


  lowStockBadge: {

    backgroundColor: '#fff1f0',

  },


  statusDot: {

    width: 7,

    height: 7,

    borderRadius: 4,

    marginRight: 6,

  },


  availableDot: {

    backgroundColor: '#1a9e72',

  },


  lowStockDot: {

    backgroundColor: '#d64545',

  },


  statusText: {

    fontSize: 11,

    fontWeight: '700',

  },


  availableText: {

    color: '#167154',

  },


  lowStockText: {

    color: '#b33434',

  },


  // ==============================
  // DIVISÓRIA
  // ==============================

  divider: {

    height: 1,

    backgroundColor: '#edf0f3',

    marginVertical: 16,

  },


  // ==============================
  // INFORMAÇÕES
  // ==============================

  infoGrid: {

    flexDirection: 'row',

    gap: 12,

  },


  infoItem: {

    flex: 1,

    flexDirection: 'row',

    alignItems: 'center',

    backgroundColor: '#f7f9fb',

    borderRadius: 13,

    padding: 11,

  },


  iconBox: {

    width: 34,

    height: 34,

    borderRadius: 10,

    backgroundColor: '#e8f2f8',

    justifyContent: 'center',

    alignItems: 'center',

    marginRight: 9,

  },


  infoLabel: {

    color: '#8996a4',

    fontSize: 11,

    marginBottom: 2,

  },


  infoValue: {

    color: '#273444',

    fontSize: 13,

    fontWeight: '700',

  },


  // ==============================
  // INFORMAÇÕES SECUNDÁRIAS
  // ==============================

  secondaryInfo: {

    flexDirection: 'row',

    alignItems: 'center',

    marginTop: 14,

    gap: 15,

  },


  secondaryItem: {

    flexDirection: 'row',

    alignItems: 'center',

    flex: 1,

  },


  secondaryText: {

    color: '#718096',

    fontSize: 12,

    marginLeft: 6,

  },


  // ==============================
  // ENTRADA / SAÍDA
  // ==============================

  movementContainer: {

    flexDirection: 'row',

    alignItems: 'center',

    marginTop: 16,

    paddingTop: 15,

    borderTopWidth: 1,

    borderTopColor: '#edf0f3',

    gap: 8,

  },


  quantityControl: {

    height: 42,

    flexDirection: 'row',

    alignItems: 'center',

    backgroundColor: '#f4f7fa',

    borderRadius: 12,

    borderWidth: 1,

    borderColor: '#e1e7ed',

  },


  quantityButton: {

    width: 36,

    height: 40,

    justifyContent: 'center',

    alignItems: 'center',

  },


  quantityText: {

    minWidth: 28,

    textAlign: 'center',

    fontSize: 15,

    fontWeight: '700',

    color: '#273444',

  },


  entryButton: {

    flex: 1,

    height: 42,

    borderRadius: 12,

    backgroundColor: '#1a9e72',

    flexDirection: 'row',

    alignItems: 'center',

    justifyContent: 'center',

    gap: 6,

  },


  entryButtonText: {

    color: '#ffffff',

    fontSize: 13,

    fontWeight: '700',

  },


  exitButton: {

    flex: 1,

    height: 42,

    borderRadius: 12,

    backgroundColor: '#d64545',

    flexDirection: 'row',

    alignItems: 'center',

    justifyContent: 'center',

    gap: 6,

  },


  exitButtonText: {

    color: '#ffffff',

    fontSize: 13,

    fontWeight: '700',

  },


  // ==============================
  // VAZIO
  // ==============================

  emptyContainer: {

    alignItems: 'center',

    justifyContent: 'center',

    paddingTop: 80,

    paddingHorizontal: 30,

  },


  emptyTitle: {

    color: '#273444',

    fontSize: 19,

    fontWeight: '700',

    marginTop: 15,

  },


  emptyText: {

    color: '#8996a4',

    fontSize: 14,

    textAlign: 'center',

    marginTop: 7,

    lineHeight: 20,

  },

});