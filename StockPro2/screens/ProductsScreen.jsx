import React, { useState, useCallback } from 'react';
import { View, Text, StyleSheet, FlatList, Image, TextInput, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import api from '../src/services/api';

export default function ProductsScreen() {
  const [search, setSearch] = useState('');
  const [products, setProducts] = useState([]);

  const loadProducts = async () => {
    try {
      const response = await api.get('/products');
      setProducts(response.data);
    } catch (error) {
      console.log('Erro ao buscar produtos:', error);
    }
  };

  useFocusEffect(
    useCallback(() => {
      loadProducts();
    }, [])
  );

  const filteredProducts = products.filter(
  (item) =>
    item.name?.toLowerCase().includes(search.toLowerCase()) ||
    item.category?.toLowerCase().includes(search.toLowerCase())
);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>Produtos</Text>
          <Text style={styles.subtitle}>Consulte os produtos cadastrados</Text>
        </View>
        <TouchableOpacity style={styles.filterButton}>
          <Ionicons name="options-outline" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      <View style={styles.searchContainer}>
        <Ionicons name="search" size={22} color="#94A3B8" />
        <TextInput
          style={styles.searchInput}
          placeholder="Pesquisar produtos..."
          placeholderTextColor="#94A3B8"
          value={search}
          onChangeText={setSearch}
        />
      </View>

      <FlatList
        data={filteredProducts}
        keyExtractor={(item) => item.id.toString()}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{ paddingBottom: 40 }}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Image source={{ uri: item.image || 'https://via.placeholder.com/150' }} style={styles.image} />
            <View style={styles.content}>
              <View style={styles.topRow}>
                <View style={{ flex: 1 }}>
                  <Text style={styles.name}>{item.name}</Text>
                  <Text style={styles.category}>{item.category}</Text>
                </View>
                <View style={[styles.stockBadge, { backgroundColor: item.stock <= 5 ? '#7F1D1D' : '#14532D' }]}>
                  <Text style={styles.stockText}>{item.stock}</Text>
                </View>
              </View>

              <View style={styles.infoRow}>
                <View style={styles.infoCard}>
                  <Ionicons name="cube-outline" size={18} color="#3B82F6" />
                  <Text style={styles.infoText}>Estoque</Text>
                </View>
                <View style={styles.infoCard}>
                  <Ionicons name="barcode-outline" size={18} color="#22C55E" />
                  <Text style={styles.infoText}>{item.code || 'S/C'}</Text>
                </View>
              </View>

              <View style={styles.bottomRow}>
                <Text style={styles.price}>R$ {Number(item.price).toFixed(2)}</Text>
                <Text style={[styles.stockStatus, { color: item.stock <= 5 ? '#FCA5A5' : '#86EFAC' }]}>
                  {item.stock <= 5 ? 'Estoque baixo' : 'Disponível'}
                </Text>
              </View>
            </View>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#020617', paddingHorizontal: 20 },
  header: { marginTop: 55, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 25 },
  title: { color: '#fff', fontSize: 32, fontWeight: 'bold' },
  subtitle: { color: '#94A3B8', marginTop: 5, fontSize: 15 },
  filterButton: { width: 52, height: 52, backgroundColor: '#1E293B', borderRadius: 18, justifyContent: 'center', alignItems: 'center' },
  searchContainer: { backgroundColor: '#1E293B', height: 62, borderRadius: 20, flexDirection: 'row', alignItems: 'center', paddingHorizontal: 18, marginBottom: 25 },
  searchInput: { flex: 1, marginLeft: 10, color: '#fff', fontSize: 16 },
  card: { backgroundColor: '#1E293B', borderRadius: 28, overflow: 'hidden', marginBottom: 22 },
  image: { width: '100%', height: 220 },
  content: { padding: 20 },
  topRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  name: { color: '#fff', fontSize: 21, fontWeight: 'bold' },
  category: { color: '#94A3B8', marginTop: 6, fontSize: 15 },
  stockBadge: { minWidth: 48, height: 48, borderRadius: 16, justifyContent: 'center', alignItems: 'center', paddingHorizontal: 12 },
  stockText: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
  infoRow: { flexDirection: 'row', marginTop: 18, gap: 12 },
  infoCard: { backgroundColor: '#0F172A', borderRadius: 14, paddingHorizontal: 14, paddingVertical: 10, flexDirection: 'row', alignItems: 'center' },
  infoText: { color: '#CBD5E1', marginLeft: 8, fontSize: 13 },
  bottomRow: { marginTop: 22, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  price: { color: '#3B82F6', fontSize: 26, fontWeight: 'bold' },
  stockStatus: { fontSize: 14, fontWeight: '600' },
});