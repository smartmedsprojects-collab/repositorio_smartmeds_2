import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import api from '../src/services/api';

export default function LoginScreen({ navigation }) {
  const [user, setUser] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    const cleanUser = user.trim();
    const cleanPassword = password.trim();

    if (!cleanUser || !cleanPassword) {
      Alert.alert('Atenção', 'Preencha todos os campos.');
      return;
    }

    setLoading(true);

    try {
      // 1. Rota corrigida para /api/login para bater exatamente com a rota do Express
      const response = await api.post('/login', {
        email: cleanUser,
        password: cleanPassword
      });

      // 2. Valida a propriedade `success` enviada no JSON do backend
      if (response.data.success) {
        // Exemplo: Salvar dados do usuário se necessário (ex: response.data.usuario)
        navigation.navigate('App');
      } else {
        Alert.alert('Erro', response.data.message || 'Credenciais inválidas.');
      }
    } catch (error) {
      // Captura a mensagem de erro retornada pelo backend (status 400, 401 ou 500)
      const errorMessage = error.response?.data?.message || 'Falha ao conectar ao servidor.';
      Alert.alert('Erro', errorMessage);
    } finally {
      setLoading(false);
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

      <TouchableOpacity
        style={styles.button}
        onPress={handleLogin}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Entrar</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A', justifyContent: 'center', padding: 25 },

  logo: { color: '#fff',
     fontSize: 38,
      fontWeight: 'bold',
       textAlign: 'center',
    marginBottom: 10 },

  subtitle: { color: '#94A3B8',
     textAlign: 'center',
      marginBottom: 40,
       fontSize: 16 },

  input: { backgroundColor: '#1E293B',
     height: 55, borderRadius: 12,
      paddingHorizontal: 15,
       color: '#fff',
        marginBottom: 15 },

  button: { backgroundColor: '#2563EB',
     height: 55,
      borderRadius: 12,
       justifyContent: 'center',
        alignItems: 'center',
         marginTop: 10 },

  buttonText: { color: '#fff',
     fontSize: 18,
      fontWeight: 'bold' },
});