import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  Image
} from 'react-native';

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
      const response = await api.post('/login', {
        email: cleanUser,
        senha: cleanPassword
      });

      if (response.data.success) {
        navigation.navigate('App');
      } else {
        Alert.alert(
          'Erro',
          response.data.message || 'Credenciais inválidas.'
        );
      }
    } catch (error) {
      const errorMessage =
        error.response?.data?.message ||
        'Falha ao conectar ao servidor.';

      Alert.alert('Erro', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>

      <Image
        source={require('../assets/logo.png')}
        style={styles.avatar} />
      <Text style={styles.logo}>SmartMeds</Text>

      <Text style={styles.subtitle}>
        Controle de estoque inteligente
      </Text>

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
        style={styles.input}
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        autoCapitalize="none"
        autoCorrect={false}
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
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
    justifyContent: 'center',
    padding: 25
  },

  logo: {
    color: '#1E293B',
    fontSize: 38,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10
  },

  subtitle: {
    color: '#94A3B8',
    textAlign: 'center',
    marginBottom: 40,
    fontSize: 16
  },

  input: {
    backgroundColor: '#1E293B',
    height: 55,
    borderRadius: 12,
    paddingHorizontal: 15,
    color: '#fff',
    marginBottom: 15
  },

  button: {
    backgroundColor: '#2563EB',
    height: 55,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 10
  },

  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold'
  },
   avatar: {
     height: 250,
    width:450,
    justifyContent: 'center',
    marginBottom: 150, 
    marginLeft:50,
    marginRight:35,   

    }
});