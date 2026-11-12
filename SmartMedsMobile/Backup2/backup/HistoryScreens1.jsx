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
  ActivityIndicator,
} from 'react-native';

import {
  Ionicons,
} from '@expo/vector-icons';

import {
  useFocusEffect,
} from '@react-navigation/native';

import api from '../src/services/api';


export default function movimentacaoScreen() {

  // =====================================================
  // ESTADOS
  // =====================================================

  const [search, setSearch] =
    useState('');

  const [movimentacao, setmovimentacao] =
    useState([]);

  const [loading, setLoading] =
    useState(false);


  // =====================================================
  // CARREGAR HISTÓRICO
  // =====================================================

  const loadmovimentacao = async () => {

    try {

      setLoading(true);


      console.log(
        '================================'
      );

      console.log(
        'BUSCANDO HISTÓRICO'
      );

      console.log(
        'GET /movimentacao'
      );


      const response =
        await api.get('/movimentacao');


      console.log(
        'STATUS:',
        response.status
      );


      console.log(
        'HISTÓRICO RECEBIDO:',
        response.data
      );


      // -----------------------------------------------
      // GARANTIR QUE A RESPOSTA É UMA LISTA
      // -----------------------------------------------

      if (
        Array.isArray(
          response.data
        )
      ) {

        setmovimentacao(
          response.data
        );

      } else {

        console.log(
          'A API não retornou uma lista.'
        );

        setmovimentacao([]);
      }


    } catch (error) {

      console.log(
        '================================'
      );

      console.log(
        'ERRO AO CARREGAR HISTÓRICO'
      );


      console.log(
        'Mensagem:',
        error.message
      );


      console.log(
        'Status:',
        error.response?.status
      );


      console.log(
        'Resposta:',
        error.response?.data
      );


      setmovimentacao([]);


    } finally {

      setLoading(false);

    }
  };


  // =====================================================
  // ATUALIZAR AO ENTRAR NA TELA
  // =====================================================

  useFocusEffect(

    useCallback(() => {

      loadmovimentacao();

    }, [])

  );


  // =====================================================
  // CONTAGEM DE ENTRADAS
  // =====================================================

  const entriesCount =
    movimentacao.filter(
      (item) => {

        const tipo =
          String(
            item?.type || ''
          )
          .trim()
          .toLowerCase();


        return (
          tipo === 'entrada'
        );
      }
    ).length;


  // =====================================================
  // CONTAGEM DE SAÍDAS
  // =====================================================

  const exitsCount =
    movimentacao.filter(
      (item) => {

        const tipo =
          String(
            item?.type || ''
          )
          .trim()
          .toLowerCase();


        return (
          tipo === 'saída' ||
          tipo === 'saida'
        );
      }
    ).length;


  // =====================================================
  // TEXTO DA PESQUISA
  // =====================================================

  const searchText =
    String(
      search || ''
    )
    .toLowerCase()
    .trim();


  // =====================================================
  // FILTRAR HISTÓRICO
  // =====================================================

  const filteredmovimentacao =
    movimentacao.filter(
      (item) => {

        const produto =
          String(
            item?.product || ''
          )
          .toLowerCase();


        const marca =
          String(
            item?.brand || ''
          )
          .toLowerCase();


        const tipo =
          String(
            item?.type || ''
          )
          .toLowerCase();


        const quantidade =
          String(
            item?.quantity || ''
          )
          .toLowerCase();


        const data =
          String(
            item?.date || ''
          )
          .toLowerCase();


        // Se pesquisa estiver vazia,
        // mostra tudo.

        if (!searchText) {

          return true;
        }


        return (

          produto.includes(
            searchText
          )

          ||

          marca.includes(
            searchText
          )

          ||

          tipo.includes(
            searchText
          )

          ||

          quantidade.includes(
            searchText
          )

          ||

          data.includes(
            searchText
          )
        );
      }
    );


  // =====================================================
  // VERIFICAR TIPO
  // =====================================================

  const isEntrada = (item) => {

    const tipo =
      String(
        item?.type || ''
      )
      .trim()
      .toLowerCase();


    return (
      tipo === 'entrada'
    );
  };


  // =====================================================
  // RENDER DO ITEM
  // =====================================================

  const rendermovimentacaoItem = ({
    item,
  }) => {

    const entrada =
      isEntrada(item);


    const produto =
      item?.product ||
      'Produto não informado';


    const tipo =
      item?.type ||
      (entrada
        ? 'Entrada'
        : 'Saída');


    const quantidade =
      Number(
        item?.quantity
      ) || 0;


    const data =
      item?.date ||
      '--/--/----';


    const hora =
      item?.hour ||
      '--:--';


    const marca =
      item?.brand ||
      '';


    return (

      <View style={styles.card}>

        {/* =================================================
            ÍCONE
        ================================================= */}

        <View
          style={[
            styles.iconContainer,

            {
              backgroundColor:
                entrada
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


        {/* =================================================
            INFORMAÇÕES
        ================================================= */}

        <View style={styles.info}>

          {/* PRODUTO + TIPO */}

          <View style={styles.topRow}>

            <Text
              style={styles.product}
              numberOfLines={1}
            >
              {produto}
            </Text>


            <Text
              style={[
                styles.type,

                {
                  color:
                    entrada
                      ? '#0E6649'
                      : '#8B1A1A',
                },
              ]}
            >
              {tipo}
            </Text>

          </View>


          {/* MARCA */}

          {marca ? (

            <Text
              style={styles.brand}
              numberOfLines={1}
            >
              {marca}
            </Text>

          ) : null}


          {/* QUANTIDADE + DATA */}

          <View style={styles.detailsRow}>

            <Text
              style={styles.quantity}
            >
              Quantidade: {quantidade}
            </Text>


            <Text
              style={styles.date}
            >
              {data}
            </Text>

          </View>


          {/* HORA */}

          <Text
            style={styles.hour}
          >
            {hora}
          </Text>

        </View>

      </View>
    );
  };


  // =====================================================
  // TELA
  // =====================================================

  return (

    <View style={styles.container}>


      {/* =================================================
          CABEÇALHO
      ================================================= */}

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
          onPress={loadmovimentacao}
        >

          <Ionicons
            name="calendar-outline"
            size={24}
            color="#FFFFFF"
          />

        </TouchableOpacity>

      </View>


      {/* =================================================
          PESQUISA
      ================================================= */}

      <View style={styles.searchContainer}>

        <Ionicons
          name="search"
          size={22}
          color="#8FA0B3"
        />


        <TextInput

          style={styles.searchInput}

          placeholder={
            'Pesquisar movimentações...'
          }

          placeholderTextColor={
            '#8FA0B3'
          }

          value={search}

          onChangeText={
            setSearch
          }

          autoCapitalize="none"

          autoCorrect={false}

        />

      </View>


      {/* =================================================
          CONTADORES
      ================================================= */}

      <View style={styles.statsContainer}>


        {/* ENTRADAS */}

        <View
          style={styles.statsCardGreen}
        >

          <Ionicons
            name="arrow-down-circle"
            size={24}
            color="#1A9E72"
          />


          <Text
            style={styles.statsNumber}
          >
            {entriesCount}
          </Text>


          <Text
            style={styles.statsLabel}
          >
            Entradas
          </Text>

        </View>


        {/* SAÍDAS */}

        <View
          style={styles.statsCardRed}
        >

          <Ionicons
            name="arrow-up-circle"
            size={24}
            color="#D94040"
          />


          <Text
            style={styles.statsNumber}
          >
            {exitsCount}
          </Text>


          <Text
            style={styles.statsLabel}
          >
            Saídas
          </Text>

        </View>

      </View>


      {/* =================================================
          CARREGANDO
      ================================================= */}

      {loading ? (

        <View
          style={styles.loadingContainer}
        >

          <ActivityIndicator
            size="large"
            color="#0F4C7A"
          />


          <Text
            style={styles.loadingText}
          >
            Carregando movimentações...
          </Text>

        </View>

      ) : (

        /* =================================================
           LISTA
        ================================================= */

        <FlatList

          data={
            filteredmovimentacao
          }


          keyExtractor={
            (item, index) =>
              String(
                item?.id ??
                `movimentacao-${index}`
              )
          }


          renderItem={
            rendermovimentacaoItem
          }


          showsVerticalScrollIndicator={
            false
          }


          keyboardShouldPersistTaps="handled"


          contentContainerStyle={
            filteredmovimentacao.length === 0
              ? styles.emptyList
              : styles.list
          }


          ListEmptyComponent={

            <View
              style={
                styles.emptyContainer
              }
            >

              <Ionicons
                name={
                  searchText
                    ? 'search-outline'
                    : 'time-outline'
                }
                size={55}
                color="#8FA0B3"
              />


              <Text
                style={
                  styles.emptyTitle
                }
              >

                {searchText
                  ? 'Nenhuma movimentação encontrada'
                  : 'Nenhuma movimentação'}

              </Text>


              <Text
                style={
                  styles.emptyText
                }
              >

                {searchText

                  ? 'Tente pesquisar por outro produto ou tipo de movimentação.'

                  : 'As entradas e saídas do estoque aparecerão aqui.'}

              </Text>

            </View>
          }

        />

      )}

    </View>
  );
}


// =====================================================
// ESTILOS
// =====================================================

const styles = StyleSheet.create({

  container: {

    flex: 1,

    backgroundColor:
      '#F4F7FA',

    paddingHorizontal:
      20,
  },


  // ===================================================
  // CABEÇALHO
  // ===================================================

  header: {

    marginTop:
      55,

    marginBottom:
      25,

    flexDirection:
      'row',

    justifyContent:
      'space-between',

    alignItems:
      'center',
  },


  title: {

    color:
      '#1A2332',

    fontSize:
      32,

    fontWeight:
      'bold',
  },


  subtitle: {

    color:
      '#5A6B7D',

    marginTop:
      5,

    fontSize:
      15,
  },


  filterButton: {

    width:
      52,

    height:
      52,

    backgroundColor:
      '#0F4C7A',

    borderRadius:
      18,

    justifyContent:
      'center',

    alignItems:
      'center',
  },


  // ===================================================
  // PESQUISA
  // ===================================================

  searchContainer: {

    backgroundColor:
      '#EDF1F5',

    height:
      62,

    borderRadius:
      20,

    flexDirection:
      'row',

    alignItems:
      'center',

    paddingHorizontal:
      18,

    marginBottom:
      25,

    borderWidth:
      1,

    borderColor:
      '#D8E3ED',
  },


  searchInput: {

    flex:
      1,

    marginLeft:
      10,

    color:
      '#1A2332',

    fontSize:
      16,
  },


  // ===================================================
  // ESTATÍSTICAS
  // ===================================================

  statsContainer: {

    flexDirection:
      'row',

    justifyContent:
      'space-between',

    marginBottom:
      25,
  },


  statsCardGreen: {

    width:
      '48%',

    backgroundColor:
      '#E6F7F2',

    borderRadius:
      24,

    padding:
      20,

    borderWidth:
      1,

    borderColor:
      '#C9EDE1',
  },


  statsCardRed: {

    width:
      '48%',

    backgroundColor:
      '#FDECEA',

    borderRadius:
      24,

    padding:
      20,

    borderWidth:
      1,

    borderColor:
      '#F4C9C6',
  },


  statsNumber: {

    color:
      '#1A2332',

    fontSize:
      28,

    fontWeight:
      'bold',

    marginTop:
      12,
  },


  statsLabel: {

    color:
      '#5A6B7D',

    marginTop:
      6,
  },


  // ===================================================
  // LISTA
  // ===================================================

  list: {

    paddingBottom:
      40,
  },


  emptyList: {

    flexGrow:
      1,

    paddingBottom:
      40,
  },


  // ===================================================
  // CARD
  // ===================================================

  card: {

    backgroundColor:
      '#FFFFFF',

    borderRadius:
      24,

    padding:
      18,

    marginBottom:
      18,

    flexDirection:
      'row',

    borderWidth:
      1,

    borderColor:
      '#D8E3ED',
  },


  // ===================================================
  // ÍCONE
  // ===================================================

  iconContainer: {

    width:
      65,

    height:
      65,

    borderRadius:
      20,

    justifyContent:
      'center',

    alignItems:
      'center',

    marginRight:
      16,
  },


  // ===================================================
  // INFORMAÇÕES
  // ===================================================

  info: {

    flex:
      1,
  },


  topRow: {

    flexDirection:
      'row',

    justifyContent:
      'space-between',

    alignItems:
      'center',
  },


  product: {

    color:
      '#1A2332',

    fontSize:
      18,

    fontWeight:
      'bold',

    flex:
      1,

    marginRight:
      10,
  },


  brand: {

    color:
      '#718096',

    fontSize:
      13,

    marginTop:
      4,
  },


  type: {

    fontSize:
      14,

    fontWeight:
      'bold',
  },


  detailsRow: {

    flexDirection:
      'row',

    justifyContent:
      'space-between',

    alignItems:
      'center',

    marginTop:
      10,
  },


  quantity: {

    color:
      '#5A6B7D',

    fontSize:
      14,
  },


  date: {

    color:
      '#8FA0B3',

    fontSize:
      13,
  },


  hour: {

    color:
      '#8FA0B3',

    marginTop:
      8,

    fontSize:
      13,
  },


  // ===================================================
  // CARREGANDO
  // ===================================================

  loadingContainer: {

    flex:
      1,

    alignItems:
      'center',

    justifyContent:
      'center',

    paddingBottom:
      100,
  },


  loadingText: {

    color:
      '#5A6B7D',

    fontSize:
      14,

    marginTop:
      12,
  },


  // ===================================================
  // VAZIO
  // ===================================================

  emptyContainer: {

    alignItems:
      'center',

    justifyContent:
      'center',

    paddingHorizontal:
      30,

    paddingTop:
      70,
  },


  emptyTitle: {

    color:
      '#1A2332',

    fontSize:
      18,

    fontWeight:
      'bold',

    marginTop:
      15,

    textAlign:
      'center',
  },


  emptyText: {

    color:
      '#8FA0B3',

    fontSize:
      14,

    textAlign:
      'center',

    marginTop:
      8,

    lineHeight:
      21,
  },

});