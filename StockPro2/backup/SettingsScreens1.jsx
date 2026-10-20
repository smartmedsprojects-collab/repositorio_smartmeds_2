import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Image,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import api from '../src/services/api';

export default function SettingsScreen({ navigation }) {
  const [darkMode, setDarkMode] = useState(true);
  const [notifications, setNotifications] = useState(true);
  const [userData, setUserData] = useState({
    name: 'Carregando...',
    role: 'Operador de Estoque',
    email: 'carregando...',
  });

  // Busca dados do perfil ativo na API / MySQL ao carregar
  useEffect(() => {
    loadUserProfile();
  }, []);

  const loadUserProfile = async () => {
    try {
      // Busca dados do primeiro usuário (como exemplo ou autenticado)
      const response = await api.post('/login', {
        email: 'lucas@empresa.com',
        password: '123456',
      });
      if (response.data.success) {
        setUserData(response.data.user);
      }
    } catch (error) {
      console.log('Erro ao carregar dados do usuário:', error);
    }
  };

  const handleLogout = () => {
    Alert.alert('Sair da Conta', 'Deseja realmente sair da aplicação?', [
      { text: 'Cancelar', style: 'cancel' },
      {
        text: 'Sair',
        style: 'destructive',
        onPress: () => {
          // Reseta a navegação e envia para a tela de Login
          navigation.reset({
            index: 0,
            routes: [{ name: 'Login' }],
          });
        },
      },
    ]);
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* HEADER */}
      <View style={styles.header}>
        <Text style={styles.title}>Configurações</Text>
        <Text style={styles.subtitle}>Gerencie preferências do sistema</Text>
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
          <Text style={styles.userName}>{userData.name}</Text>
          <Text style={styles.userRole}>{userData.role}</Text>
          <Text style={styles.userEmail}>{userData.email}</Text>
        </View>

        <TouchableOpacity style={styles.editButton}>
          <Ionicons name="create-outline" size={22} color="#FFFFFF" />
        </TouchableOpacity>
      </View>

      {/* PREFERÊNCIAS */}
      <Text style={styles.sectionTitle}>Preferências</Text>

      <View style={styles.optionCard}>
        <View style={styles.optionLeft}>
          <View style={styles.iconBlue}>
            <Ionicons name="moon-outline" size={22} color="#1A6FA8" />
          </View>
          <View>
            <Text style={styles.optionTitle}>Modo Escuro</Text>
            <Text style={styles.optionSubtitle}>Tema visual do aplicativo</Text>
          </View>
        </View>

        <Switch value={darkMode} onValueChange={setDarkMode} />
      </View>

      <View style={styles.optionCard}>
        <View style={styles.optionLeft}>
          <View style={styles.iconGreen}>
            <Ionicons name="notifications-outline" size={22} color="#1A9E72" />
          </View>
          <View>
            <Text style={styles.optionTitle}>Notificações</Text>
            <Text style={styles.optionSubtitle}>Alertas do sistema</Text>
          </View>
        </View>

        <Switch value={notifications} onValueChange={setNotifications} />
      </View>

      {/* SEGURANÇA */}
      <Text style={styles.sectionTitle}>Conta e Segurança</Text>

      <TouchableOpacity style={styles.menuCard}>
        <View style={styles.menuLeft}>
          <View style={styles.iconPurple}>
            <Ionicons name="lock-closed-outline" size={22} color="#1A6FA8" />
          </View>
          <View>
            <Text style={styles.menuTitle}>Alterar Senha</Text>
            <Text style={styles.menuSubtitle}>Atualizar credenciais</Text>
          </View>
        </View>
        <Ionicons name="chevron-forward" size={22} color="#8FA0B3" />
      </TouchableOpacity>

      <TouchableOpacity style={styles.menuCard}>
        <View style={styles.menuLeft}>
          <View style={styles.iconOrange}>
            <Ionicons name="shield-checkmark-outline" size={22} color="#D97706" />
          </View>
          <View>
            <Text style={styles.menuTitle}>Privacidade</Text>
            <Text style={styles.menuSubtitle}>Configurações de acesso</Text>
          </View>
        </View>
        <Ionicons name="chevron-forward" size={22} color="#8FA0B3" />
      </TouchableOpacity>

      {/* LOGOUT */}
      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Ionicons name="log-out-outline" size={24} color="#FFFFFF" />
        <Text style={styles.logoutText}>Sair da Conta</Text>
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
    width: 80,
    height: 80,
    borderRadius: 22,
  },

  profileInfo: {
    flex: 1,
    marginLeft: 18,
  },

  userName: {
    color: '#1A2332',
    fontSize: 22,
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
    fontSize: 14,
  },

  editButton: {
    width: 48,
    height: 48,
    backgroundColor: '#1A6FA8',
    borderRadius: 16,
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

  optionCard: {
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

  optionLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },

  optionTitle: {
    color: '#1A2332',
    fontSize: 17,
    fontWeight: 'bold',
  },

  optionSubtitle: {
    color: '#5A6B7D',
    marginTop: 4,
    fontSize: 13,
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

  iconBlue: {
    width: 50,
    height: 50,
    backgroundColor: '#E8F3FB',
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },

  iconGreen: {
    width: 50,
    height: 50,
    backgroundColor: '#E6F7F2',
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
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

  iconOrange: {
    width: 50,
    height: 50,
    backgroundColor: '#FEF3E2',
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },

  logoutButton: {
    backgroundColor: '#D94040',
    height: 65,
    borderRadius: 18,
    marginTop: 35,
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
