import React, {
  useState,
  useCallback,
} from 'react';

import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TextInput,
  TouchableOpacity,
} from 'react-native';

import { Ionicons } from '@expo/vector-icons';

import {
  useFocusEffect,
} from '@react-navigation/native';

import api from '../src/services/api';


export default function HistoryScreen() {

  const [search, setSearch] = useState('');

  const [history, setHistory] = useState([]);


  // =====================================================
  // CARREGAR HISTÓRICO
  // =====================================================

  const loadHistory = async () => {

    try {

      const response =
        await api.get('/history');


      console.log(
        'Histórico recebido:',
        response.data
      );


      if (Array.isArray(response.data)) {

        setHistory(response.data);

      } else {

        setHistory([]);
      }


    } catch (error) {

      console.log(
        'Erro ao carregar histórico:',
        error.response?.data ||
        error.message
      );

      setHistory([]);
    }
  };


  // =====================================================
  // ATUALIZAR QUANDO ENTRAR NA TELA
  // =====================================================

  useFocusEffect(
    useCallback(() => {

      loadHistory();

    }, [])
  );


  // =====================================================
  // CONTADORES
  // =====================================================

  const entriesCount =
    history.filter(
      (item) =>
        item.type === 'Entrada'
    ).length;


  const exitsCount =
    history.filter(
      (item) =>
        item.type === 'Saída'
    ).length;


  // =====================================================
  // FILTRO
  // =====================================================

  const textoPesquisa =
    search.toLowerCase();


  const filteredHistory =
    history.filter((item) => {

      const produto =
        String(
          item.product || ''
        ).toLowerCase();


      const tipo =
        String(
          item.type || ''
        ).toLowerCase();


      return (
        produto.includes(textoPesquisa) ||
        tipo.includes(textoPesquisa)
      );
    });


  // =====================================================
  // RENDER
  // =====================================================

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
          style={styles.filterButton}
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

        />

      </View>


      {/* ESTATÍSTICAS */}

      <View style={styles.statsContainer}>


        {/* ENTRADAS */}

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


        {/* SAÍDAS */}

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

      <FlatList

        data={filteredHistory}

        keyExtractor={(item, index) =>
          String(
            item.id ??
            `historico-${index}`
          )
        }

        showsVerticalScrollIndicator={false}

        contentContainerStyle={{
          paddingBottom: 40,
        }}


        ListEmptyComponent={

          <View style={styles.emptyContainer}>

            <Ionicons
              name="time-outline"
              size={50}
              color="#8FA0B3"
            />

            <Text style={styles.emptyTitle}>
              Nenhuma movimentação
            </Text>

            <Text style={styles.emptyText}>
              As entradas e saídas do estoque aparecerão aqui.
            </Text>

          </View>

        }


        renderItem={({ item }) => {

          const isEntrada =
            item.type === 'Entrada';


          return (

            <View style={styles.card}>

              {/* ÍCONE */}

              <View
                style={[
                  styles.iconContainer,

                  {
                    backgroundColor:
                      isEntrada
                        ? '#E6F7F2'
                        : '#FDECEA',
                  },
                ]}
              >

                <Ionicons

                  name={
                    isEntrada
                      ? 'arrow-down-circle'
                      : 'arrow-up-circle'
                  }

                  size={30}

                  color={
                    isEntrada
                      ? '#1A9E72'
                      : '#D94040'
                  }

                />

              </View>


              {/* INFORMAÇÕES */}

              <View style={styles.info}>


                {/* NOME + TIPO */}

                <View style={styles.topRow}>

                  <Text
                    style={styles.product}
                    numberOfLines={1}
                  >
                    {item.product ||
                      'Produto não informado'}
                  </Text>


                  <Text
                    style={[
                      styles.type,

                      {
                        color:
                          isEntrada
                            ? '#0E6649'
                            : '#8B1A1A',
                      },
                    ]}
                  >
                    {item.type}
                  </Text>

                </View>


                {/* QUANTIDADE + DATA */}

                <View style={styles.detailsRow}>

                  <Text style={styles.quantity}>

                    Quantidade:{' '}

                    {Number(
                      item.quantity || 0
                    )}

                  </Text>


                  <Text style={styles.date}>

                    {item.date ||
                      'Data não informada'}

                  </Text>

                </View>


                {/* HORA */}

                <Text style={styles.hour}>

                  {item.hour ||
                    'Horário não informado'}

                </Text>

              </View>

            </View>
          );
        }}

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
    height: 62,
    borderRadius: 20,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 18,
    marginBottom: 25,
    borderWidth: 1,
    borderColor: '#D8E3ED',
  },


  searchInput: {
    flex: 1,
    marginLeft: 10,
    color: '#1A2332',
    fontSize: 16,
  },


  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 25,
  },


  statsCardGreen: {
    width: '48%',
    backgroundColor: '#E6F7F2',
    borderRadius: 24,
    padding: 20,
    borderWidth: 1,
    borderColor: '#C9EDE1',
  },


  statsCardRed: {
    width: '48%',
    backgroundColor: '#FDECEA',
    borderRadius: 24,
    padding: 20,
    borderWidth: 1,
    borderColor: '#F4C9C6',
  },


  statsNumber: {
    color: '#1A2332',
    fontSize: 28,
    fontWeight: 'bold',
    marginTop: 12,
  },


  statsLabel: {
    color: '#5A6B7D',
    marginTop: 6,
  },


  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 18,
    marginBottom: 18,
    flexDirection: 'row',
    borderWidth: 1,
    borderColor: '#D8E3ED',
  },


  iconContainer: {
    width: 65,
    height: 65,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },


  info: {
    flex: 1,
  },


  topRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },


  product: {
    color: '#1A2332',
    fontSize: 18,
    fontWeight: 'bold',
    flex: 1,
    marginRight: 10,
  },


  type: {
    fontSize: 14,
    fontWeight: 'bold',
  },


  detailsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 10,
  },


  quantity: {
    color: '#5A6B7D',
    fontSize: 14,
  },


  date: {
    color: '#8FA0B3',
    fontSize: 13,
  },


  hour: {
    color: '#8FA0B3',
    marginTop: 8,
    fontSize: 13,
  },


  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: 70,
    paddingHorizontal: 30,
  },


  emptyTitle: {
    color: '#1A2332',
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 15,
  },


  emptyText: {
    color: '#8FA0B3',
    fontSize: 14,
    textAlign: 'center',
    marginTop: 8,
    lineHeight: 21,
  },

});