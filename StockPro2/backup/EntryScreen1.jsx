import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, TextInput, ScrollView, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import api from '../src/services/api';

export default function EntryScreen({ navigation }) {
  const [product, setProduct] = useState(null);
  const [quantity, setQuantity] = useState('');

  useEffect(() => {
    // Busca o produto ID 1 padrão como modelo inicial
    api.get('/produto/1').then(res => setProduct(res.data)).catch(console.log);
  }, []);

  const handleConfirmEntry = async () => {
    if (!product) {
      Alert.alert('Erro', 'Produto ainda não carregado.');
      return;
    }

    if (!quantity || isNaN(quantity) || Number(quantity) <= 0) {
      Alert.alert('Erro', 'Insira uma quantidade válida.');
      return;
    }

    try {
      await api.post('/stock/move', {
        productId: product.id,
        type: 'Entrada',
        quantity: parseInt(quantity),
      });

      Alert.alert('Sucesso', 'Entrada registrada com sucesso!', [
        {
          text: 'OK',
          onPress: () => navigation.navigate('Home'),
        },
      ]);
    } catch (error) {
      Alert.alert(
        'Erro',
        error.response?.data?.message || 'Erro ao registrar entrada.'
      );
    }
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <Text style={styles.title}>Entrada de Estoque</Text>
        <Text style={styles.subtitle}>Registre produtos rapidamente</Text>
      </View>

      <TouchableOpacity style={styles.qrButton}>
        <View style={styles.qrContent}>
          <Ionicons name="qr-code-outline" size={32} color="#ffffff" />
          <View>
            <Text style={styles.qrTitle}>Ler QR Code</Text>
            <Text style={styles.qrSubtitle}>Escanear produto</Text>
          </View>
        </View>
        <Ionicons name="chevron-forward" size={22} color="#ffffff" />
      </TouchableOpacity>

      <Text style={styles.sectionTitle}>Produto Encontrado</Text>

      {product && (
        <View style={styles.productCard}>
          <View style={styles.productIcon}>
            <Ionicons name="cube" size={28} color="#1a6fa8" />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.productName}>{product.name}</Text>
            <Text style={styles.productCode}>Código: {product.code}</Text>
            <Text style={styles.productStock}>Estoque Atual: {product.stock}</Text>
          </View>
        </View>
      )}

      <Text style={styles.sectionTitle}>Quantidade</Text>

      <TextInput
        style={styles.input}
        placeholder="Digite a quantidade"
        placeholderTextColor="#8fa0b3"
        keyboardType="numeric"
        value={quantity}
        onChangeText={setQuantity}
      />

      <View style={styles.summaryCard}>
        <Text style={styles.summaryTitle}>Resumo da Entrada</Text>
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>Produto</Text>
          <Text style={styles.summaryValue}>{product?.name || '-'}</Text>
        </View>
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>Quantidade</Text>
          <Text style={styles.summaryValue}>{quantity || 0}</Text>
        </View>
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>Estoque Final</Text>
          <Text style={styles.summaryValueGreen}>
            {(product?.stock || 0) + Number(quantity || 0)}
          </Text>
        </View>
      </View>

      <TouchableOpacity style={styles.confirmButton} onPress={handleConfirmEntry}>
        <Ionicons name="checkmark-circle" size={24} color="#ffffff" />
        <Text style={styles.confirmText}>Confirmar Entrada</Text>
      </TouchableOpacity>

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f4f7fa',
    paddingHorizontal: 20,
  },

  header: {
    marginTop: 50,
  },

  title: {
    color: '#1a2332',
    fontSize: 30,
    fontWeight: 'bold',
  },

  subtitle: {
    color: '#5a6b7d',
    marginTop: 5,
    fontSize: 15,
  },

  qrButton: {
    backgroundColor: '#0f4c7a',
    borderRadius: 25,
    padding: 22,
    marginTop: 30,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },

  qrContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 15,
  },

  qrTitle: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
  },

  qrSubtitle: {
    color: '#e8f3fb',
    marginTop: 3,
  },

  sectionTitle: {
    color: '#1a2332',
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 35,
    marginBottom: 15,
  },

  productCard: {
    backgroundColor: '#ffffff',
    borderRadius: 22,
    padding: 20,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#d8e3ed',
  },

  productIcon: {
    width: 65,
    height: 65,
    backgroundColor: '#e8f3fb',
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },

  productName: {
    color: '#1a2332',
    fontSize: 18,
    fontWeight: 'bold',
  },

  productCode: {
    color: '#5a6b7d',
    marginTop: 5,
  },

  productStock: {
    color: '#1a9e72',
    marginTop: 8,
    fontWeight: 'bold',
  },

  input: {
    backgroundColor: '#edf1f5',
    height: 65,
    borderRadius: 18,
    paddingHorizontal: 20,
    color: '#1a2332',
    fontSize: 18,
    borderWidth: 1.5,
    borderColor: '#d8e3ed',
  },

  summaryCard: {
    backgroundColor: '#ffffff',
    borderRadius: 22,
    padding: 22,
    marginTop: 35,
    borderWidth: 1,
    borderColor: '#d8e3ed',
  },

  summaryTitle: {
    color: '#1a6fa8',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 20,
  },

  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },

  summaryLabel: {
    color: '#5a6b7d',
    fontSize: 15,
  },

  summaryValue: {
    color: '#0c3d61',
    fontWeight: 'bold',
  },

  summaryValueGreen: {
    color: '#1a9e72',
    fontWeight: 'bold',
  },

  confirmButton: {
    backgroundColor: '#1a6fa8',
    height: 65,
    borderRadius: 22,
    marginTop: 35,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 10,
  },

  confirmText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
