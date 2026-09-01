import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import api from '../src/services/api';

export default function LoginScreen({ navigation }) {
  const [user, setUser] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    if (!user || !password) {
      Alert.alert('Atenção', 'Preencha todos os campos.');
      return;
    }

    try {
      const response = await api.post('/login', { email: user, password });
      if (response.data.success) {
        navigation.navigate('App');
      }
    } catch (error) {
      Alert.alert('Erro', error.response?.data?.message || 'Falha ao conectar ao servidor.');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.logo}>StockPro</Text>
      <Text style={styles.subtitle}>Controle de estoque inteligente</Text>

      <TextInput
        placeholder="E-mail / Usuário"
        placeholderTextColor="#9CA3AF"
        style={styles.input}
        value={user}
        onChangeText={setUser}
        autoCapitalize="none"
      />

      <TextInput
        placeholder="Senha"
        placeholderTextColor="#9CA3AF"
        secureTextEntry
        style={styles.input}
        value={password}
        onChangeText={setPassword}
      />

      <TouchableOpacity style={styles.button} onPress={handleLogin}>
        <Text style={styles.buttonText}>Entrar</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A', justifyContent: 'center', padding: 25 },
  logo: { color: '#fff', fontSize: 38, fontWeight: 'bold', textAlign: 'center', marginBottom: 10 },
  subtitle: { color: '#94A3B8', textAlign: 'center', marginBottom: 40, fontSize: 16 },
  input: { backgroundColor: '#1E293B', height: 55, borderRadius: 12, paddingHorizontal: 15, color: '#fff', marginBottom: 15 },
  button: { backgroundColor: '#2563EB', height: 55, borderRadius: 12, justifyContent: 'center', alignItems: 'center', marginTop: 10 },
  buttonText: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
});