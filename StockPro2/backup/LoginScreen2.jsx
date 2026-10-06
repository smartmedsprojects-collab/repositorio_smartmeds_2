import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import api from '../src/services/api';

export default function LoginScreen({ navigation }) {
  const [user, setUser] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    // Limpa espaços em branco acidentais no início/fim
    const cleanUser = user.trim();
    const cleanPassword = password.trim();

    if (!cleanUser || !cleanPassword) {
      Alert.alert('Atenção', 'Preencha todos os campos.');
      return;
    }

    try {
      // Confirme se o seu backend aceita 'email' ou se espera 'user' / 'username'
      const response = await api.post('/login', { 
        email: cleanUser, 
        password: cleanPassword 
      });

      if (response.data.success || response.status === 200) {
        navigation.navigate('App');
      }
    } catch (error) {
      // Exibe a mensagem enviada pela API ou o erro genérico
      const errorMessage = error.response?.data?.message || 'Falha ao conectar ao servidor.';
      Alert.alert('Erro', errorMessage);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.logo}>SmartMeds</Text>
      <Text style={styles.subtitle}>Controle de estoque inteligente</Text>

      <TextInput
        placeholder="E-mail / Usuário"
        placeholderTextColor="#9CA3AF"
        style={styles.input}
        value={user}
        onChangeText={setUser}
        autoCapitalize="none"
        autoCorrect={false}
        keyboardType="email-address"
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