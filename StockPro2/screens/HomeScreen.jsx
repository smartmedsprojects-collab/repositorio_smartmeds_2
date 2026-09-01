import React, { useState, useCallback } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import api from '../src/services/api';

export default function HomeScreen({ navigation }) {
  const [dashboardData, setDashboardData] = useState({
    totalProducts: 0,
    lowStockCount: 0,
    recentActivities: [],
  });

  const loadDashboard = async () => {
    try {
      const response = await api.get('/dashboard');
      setDashboardData(response.data);
    } catch (error) {
      console.log('Erro ao carregar Dashboard:', error);
    }
  };

  useFocusEffect(
    useCallback(() => {
      loadDashboard();
    }, [])
  );

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <View>
          <Text style={styles.welcome}>Bem-vindo</Text>
          <Text style={styles.userName}>Sistema de Estoque</Text>
        </View>
        <TouchableOpacity style={styles.notification}>
          <Ionicons name="notifications-outline" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      <View style={styles.balanceCard}>
        <Text style={styles.balanceLabel}>Produtos em Estoque</Text>
        <Text style={styles.balanceValue}>{dashboardData.totalProducts}</Text>
        <View style={styles.balanceFooter}>
          <Ionicons name="trending-up" size={18} color="#22C55E" />
          <Text style={styles.balanceGrowth}>Atualizado com o BD</Text>
        </View>
      </View>

      <View style={styles.cardsContainer}>
        <View style={styles.smallCard}>
          <View style={styles.iconBlue}>
            <Ionicons name="cube" size={24} color="#3B82F6" />
          </View>
          <Text style={styles.cardNumber}>{dashboardData.totalProducts}</Text>
          <Text style={styles.cardLabel}>Unidades Totais</Text>
        </View>

        <View style={styles.smallCard}>
          <View style={styles.iconRed}>
            <Ionicons name="alert-circle" size={24} color="#EF4444" />
          </View>
          <Text style={styles.cardNumber}>{dashboardData.lowStockCount}</Text>
          <Text style={styles.cardLabel}>Estoque Baixo</Text>
        </View>
      </View>

      <Text style={styles.sectionTitle}>Operações</Text>

      <TouchableOpacity style={styles.actionButtonBlue} onPress={() => navigation.navigate('Produtos')}>
        <View style={styles.buttonContent}>
          <Ionicons name="cube-outline" size={26} color="#fff" />
          <View>
            <Text style={styles.buttonTitle}>Produtos</Text>
            <Text style={styles.buttonSubtitle}>Visualizar estoque completo</Text>
          </View>
        </View>
        <Ionicons name="chevron-forward" size={22} color="#fff" />
      </TouchableOpacity>

      <TouchableOpacity style={styles.actionButtonGreen} onPress={() => navigation.navigate('Entrada')}>
        <View style={styles.buttonContent}>
          <Ionicons name="arrow-down-circle-outline" size={26} color="#fff" />
          <View>
            <Text style={styles.buttonTitle}>Entrada de Estoque</Text>
            <Text style={styles.buttonSubtitle}>Registrar novos produtos</Text>
          </View>
        </View>
        <Ionicons name="chevron-forward" size={22} color="#fff" />
      </TouchableOpacity>

      <TouchableOpacity style={styles.actionButtonRed} onPress={() => navigation.navigate('Saída')}>
        <View style={styles.buttonContent}>
          <Ionicons name="arrow-up-circle-outline" size={26} color="#fff" />
          <View>
            <Text style={styles.buttonTitle}>Saída de Estoque</Text>
            <Text style={styles.buttonSubtitle}>Registrar retirada</Text>
          </View>
        </View>
        <Ionicons name="chevron-forward" size={22} color="#fff" />
      </TouchableOpacity>

      <Text style={styles.sectionTitle}>Atividades Recentes</Text>

      {dashboardData.recentActivities.map((item) => (
        <View key={item.id} style={styles.activityCard}>
          <Ionicons
            name={item.type === 'Entrada' ? 'checkmark-circle' : 'remove-circle'}
            size={22}
            color={item.type === 'Entrada' ? '#22C55E' : '#EF4444'}
          />
          <Text style={styles.activityText}>
            {item.type} de {item.quantity} {item.product}
          </Text>
        </View>
      ))}

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#020617', paddingHorizontal: 20 },
  header: { marginTop: 60, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  welcome: { color: '#94A3B8', fontSize: 15 },
  userName: { color: '#fff', fontSize: 28, fontWeight: 'bold', marginTop: 3 },
  notification: { width: 50, height: 50, backgroundColor: '#1E293B', borderRadius: 15, justifyContent: 'center', alignItems: 'center' },
  balanceCard: { backgroundColor: '#2563EB', borderRadius: 30, padding: 25, marginTop: 30 },
  balanceLabel: { color: '#DBEAFE', fontSize: 16 },
  balanceValue: { color: '#fff', fontSize: 42, fontWeight: 'bold', marginTop: 10 },
  balanceFooter: { flexDirection: 'row', alignItems: 'center', marginTop: 12 },
  balanceGrowth: { color: '#DCFCE7', marginLeft: 6, fontWeight: '600' },
  cardsContainer: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 25 },
  smallCard: { backgroundColor: '#1E293B', width: '48%', borderRadius: 22, padding: 20 },
  iconBlue: { width: 50, height: 50, backgroundColor: '#172554', borderRadius: 15, justifyContent: 'center', alignItems: 'center' },
  iconRed: { width: 50, height: 50, backgroundColor: '#450A0A', borderRadius: 15, justifyContent: 'center', alignItems: 'center' },
  cardNumber: { color: '#fff', fontSize: 28, fontWeight: 'bold', marginTop: 15 },
  cardLabel: { color: '#94A3B8', marginTop: 5 },
  sectionTitle: { color: '#fff', fontSize: 22, fontWeight: 'bold', marginTop: 35, marginBottom: 18 },
  actionButtonBlue: { backgroundColor: '#2563EB', borderRadius: 24, padding: 20, marginBottom: 15, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  actionButtonGreen: { backgroundColor: '#16A34A', borderRadius: 24, padding: 20, marginBottom: 15, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  actionButtonRed: { backgroundColor: '#DC2626', borderRadius: 24, padding: 20, marginBottom: 15, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  buttonContent: { flexDirection: 'row', alignItems: 'center', gap: 15 },
  buttonTitle: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
  buttonSubtitle: { color: '#E2E8F0', marginTop: 3, fontSize: 13 },
  activityCard: { backgroundColor: '#1E293B', borderRadius: 18, padding: 18, marginBottom: 12, flexDirection: 'row', alignItems: 'center', gap: 12 },
  activityText: { color: '#fff', fontSize: 15 },
});