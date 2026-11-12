import React, { useState } from 'react';
import { Modal, View, StyleSheet, Button, Text } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera'; // Ou react-native-vision-camera

export default function QRCodeScannerModal({ visible, onClose, onReadCode }) {
  const [permission, requestPermission] = useCameraPermissions();
  const [scanned, setScanned] = useState(false);

  if (!permission) return <View />;
  if (!permission.granted) {
    return (
      <Modal visible={visible} animationType="slide">
        <View style={styles.centerContainer}>
          <Text style={styles.text}>Precisamos de permissão para usar a câmera</Text>
          <Button onPress={requestPermission} title="Conceder Permissão" />
          <Button title="Fechar" onPress={onClose} color="red" />
        </View>
      </Modal>
    );
  }

  const handleBarcodeScanned = ({ data }) => {
    if (scanned) return;
    setScanned(true);
    onReadCode(data); // Envia o resultado para a tela pai
    setTimeout(() => setScanned(false), 2000); // Debounce de 2s para evitar múltiplos disparos
  };

  return (
    <Modal visible={visible} animationType="slide" onRequestClose={onClose}>
      <View style={styles.container}>
        <CameraView
          style={StyleSheet.absoluteFillObject}
          facing="back"
          onBarcodeScanned={scanned ? undefined : handleBarcodeScanned}
          barcodeScannerSettings={{ barcodeTypes: ['qr'] }}
        />
        <View style={styles.overlay}>
          <Button title="Fechar Câmera" onPress={onClose} color="#FF3B30" />
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  centerContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 },
  text: { textAlign: 'center', marginBottom: 20 },
  overlay: { position: 'absolute', bottom: 40, alignSelf: 'center' },
});