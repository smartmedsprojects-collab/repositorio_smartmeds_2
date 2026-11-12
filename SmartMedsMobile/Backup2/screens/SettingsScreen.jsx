import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import api from '../src/services/api';

export default function SettingsScreen({ navigation }) {
  const [userData, setUserData] = useState({
    name: 'Carregando...',
    role: 'Operador de Estoque',
    email: 'carregando...',
  });

  // Busca os dados do perfil ao carregar a tela
  useEffect(() => {
    loadUserProfile();
  }, []);

  const loadUserProfile = async () => {
    try {
      const response = await api.post('/login', {
        email: 'lucas@empresa.com',
        senha: '123456',
      });

      if (response.data.success) {
        setUserData(response.data.user);
      }
    } catch (error) {
      console.log('Erro ao carregar dados do usuário:', error);
    }
  };

  const handleLogout = () => {
    Alert.alert(
      'Sair da Conta',
      'Deseja realmente sair da aplicação?',
      [
        {
          text: 'Cancelar',
          style: 'cancel',
        },
        {
          text: 'Sair',
          style: 'destructive',
          onPress: () => {
            navigation.reset({
              index: 0,
              routes: [{ name: 'Login' }],
            });
          },
        },
      ]
    );
  };

  return (
    <ScrollView
      style={styles.container}
      showsVerticalScrollIndicator={false}
    >
      {/* HEADER */}
      <View style={styles.header}>
        <Text style={styles.title}>Configurações</Text>
        <Text style={styles.subtitle}>
          Gerencie preferências do sistema
        </Text>
      </View>

      {/* PERFIL */}
      <View style={styles.profileCard}>
        <Image
          source={{
            uri: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?q=80&w=1200&auto=format&fit=crop',
          }}
          style={styles.avatar}
        />

        <View style={styles.profileInfo}>
          <Text style={styles.userName}>
            {userData.nome || userData.name}
          </Text>

          <Text style={styles.userRole}>
            {userData.role || 'Operador de Estoque'}
          </Text>

          <Text style={styles.userEmail}>
            {userData.email}
          </Text>
        </View>

        <TouchableOpacity style={styles.editButton}>
          <Ionicons
            name="create-outline"
            size={22}
            color="#FFFFFF"
          />
        </TouchableOpacity>
      </View>

      {/* CONTA E SEGURANÇA */}
      <Text style={styles.sectionTitle}>
        Conta e Segurança
      </Text>

      <TouchableOpacity style={styles.menuCard}>
        <View style={styles.menuLeft}>
          <View style={styles.iconPurple}>
            <Ionicons
              name="lock-closed-outline"
              size={22}
              color="#1A6FA8"
            />
          </View>

          <View>
            <Text style={styles.menuTitle}>
              Alterar Senha
            </Text>

            <Text style={styles.menuSubtitle}>
              Atualizar credenciais
            </Text>
          </View>
        </View>

        <Ionicons
          name="chevron-forward"
          size={22}
          color="#8FA0B3"
        />
      </TouchableOpacity>

      {/* SAIR DA CONTA */}
      <TouchableOpacity
        style={styles.logoutButton}
        onPress={handleLogout}
      >
        <Ionicons
          name="log-out-outline"
          size={24}
          color="#FFFFFF"
        />

        <Text style={styles.logoutText}>
          Sair da Conta
        </Text>
      </TouchableOpacity>

      <View style={{ height: 50 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F4F7FA',
    paddingHorizontal: 20,
  },

  header: {
    marginTop: 55,
    marginBottom: 30,
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

  profileCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 22,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#D8E3ED',
  },

  avatar: {
    width: 72,
    height: 72,
    borderRadius: 22,
  },

  profileInfo: {
    flex: 1,
    marginLeft: 16,
  },

  userName: {
    color: '#1A2332',
    fontSize: 20,
    fontWeight: 'bold',
  },

  userRole: {
    color: '#1A6FA8',
    marginTop: 5,
    fontWeight: '600',
  },

  userEmail: {
    color: '#5A6B7D',
    marginTop: 6,
    fontSize: 12,
  },

  editButton: {
    width: 44,
    height: 44,
    backgroundColor: '#1A6FA8',
    borderRadius: 15,
    justifyContent: 'center',
    alignItems: 'center',
  },

  sectionTitle: {
    color: '#1A2332',
    fontSize: 22,
    fontWeight: 'bold',
    marginTop: 35,
    marginBottom: 18,
  },

  menuCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    padding: 18,
    marginBottom: 15,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#D8E3ED',
  },

  menuLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },

  menuTitle: {
    color: '#1A2332',
    fontSize: 17,
    fontWeight: 'bold',
  },

  menuSubtitle: {
    color: '#5A6B7D',
    marginTop: 4,
    fontSize: 13,
  },

  iconPurple: {
    width: 50,
    height: 50,
    backgroundColor: '#E8F3FB',
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },

  logoutButton: {
    backgroundColor: '#D94040',
    height: 60,
    borderRadius: 18,
    marginTop: 30,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 10,
  },

  logoutText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
});