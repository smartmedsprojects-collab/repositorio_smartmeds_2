import React, { useState, useEffect } from 'react';
import {
  Modal,
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { Ionicons } from '@expo/vector-icons';
 
// Formato do QR gerado na tela de Produtos: "smartmeds:produto:13"
const QR_REGEX = /^smartmeds:produto:(\d+)$/;
 
export default function QRCodeScannerModal({ visible, onClose, onReadCode }) {
  const [permission, requestPermission] = useCameraPermissions();
  const [scanned, setScanned] = useState(false);
  const [erro, setErro] = useState('');
 
  // Ao abrir o modal: reseta o estado e pede permissão da câmera se necessário
  useEffect(() => {
    if (visible) {
      setScanned(false);
      setErro('');
 
      if (permission && !permission.granted && permission.canAskAgain) {
        requestPermission();
      }
    }
  }, [visible]);
 
  const handleBarcodeScanned = ({ data }) => {
    if (scanned) return;
 
    const match = QR_REGEX.exec(String(data).trim());
 
    if (!match) {
      // QR que não é de produto: mostra aviso e permite tentar de novo
      setScanned(true);
      setErro('Este QR Code não é de um produto do SmartMeds.');
      setTimeout(() => {
        setErro('');
        setScanned(false);
      }, 2000);
      return;
    }
 
    setScanned(true);
 
    // Devolve só o ID do produto (número) para a tela pai
    onReadCode(Number(match[1]));
  };
 
  if (!visible) return null;
 
  const semPermissao = permission && !permission.granted;
 
  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={false}
      onRequestClose={onClose}
    >
      <View style={styles.container}>
        {!permission ? (
          <Text style={styles.text}>Carregando câmera...</Text>
        ) : semPermissao ? (
          <View style={styles.permissionBox}>
            <Ionicons name="camera-outline" size={48} color="#fff" />
            <Text style={styles.text}>Sem acesso à câmera</Text>
 
            {permission.canAskAgain && (
              <TouchableOpacity
                style={styles.permissionBtn}
                onPress={requestPermission}
              >
                <Text style={styles.permissionBtnText}>Permitir câmera</Text>
              </TouchableOpacity>
            )}
          </View>
        ) : (
          <>
            <CameraView
              style={StyleSheet.absoluteFillObject}
              facing="back"
              onBarcodeScanned={scanned ? undefined : handleBarcodeScanned}
              barcodeScannerSettings={{ barcodeTypes: ['qr'] }}
            />
 
            {/* Moldura de leitura */}
            <View style={styles.overlay} pointerEvents="none">
              <View style={styles.frame} />
              <Text style={styles.hint}>
                Aponte a câmera para o QR Code do produto
              </Text>
              {!!erro && <Text style={styles.error}>{erro}</Text>}
            </View>
          </>
        )}
 
        <TouchableOpacity style={styles.closeBtn} onPress={onClose}>
          <Text style={styles.closeText}>Fechar Câmera</Text>
        </TouchableOpacity>
      </View>
    </Modal>
  );
}
 
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    justifyContent: 'flex-end',
    alignItems: 'center',
  },
  text: {
    color: '#fff',
    fontSize: 18,
    marginTop: 12,
    marginBottom: 20,
  },
  permissionBox: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
  },
  permissionBtn: {
    backgroundColor: '#3B82F6',
    paddingVertical: 12,
    paddingHorizontal: 22,
    borderRadius: 12,
  },
  permissionBtnText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 15,
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
  },
  frame: {
    width: 250,
    height: 250,
    borderRadius: 24,
    borderWidth: 3,
    borderColor: '#3B82F6',
    backgroundColor: 'transparent',
  },
  hint: {
    color: '#fff',
    fontSize: 15,
    marginTop: 20,
    textAlign: 'center',
    paddingHorizontal: 30,
  },
  error: {
    color: '#fff',
    backgroundColor: '#DC2626',
    marginTop: 14,
    paddingVertical: 8,
    paddingHorizontal: 14,
    borderRadius: 10,
    fontSize: 14,
    overflow: 'hidden',
  },
  closeBtn: {
    backgroundColor: '#DC2626',
    padding: 20,
    borderRadius: 15,
    marginBottom: 40,
  },
  closeText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
});
 