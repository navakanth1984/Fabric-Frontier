import React, { useState, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, TextInput, Alert, Platform } from 'react-native';
import { auth } from '../src/lib/firebase';
import { 
  signInAnonymously, 
  signInWithPhoneNumber, 
  GoogleAuthProvider, 
  signInWithPopup,
  RecaptchaVerifier,
  ConfirmationResult
} from 'firebase/auth';
import { router } from 'expo-router';

declare global {
  interface Window {
    recaptchaVerifier: any;
  }
}

export default function AuthScreen() {
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState<'phone' | 'otp'>('phone');
  const confirmationResultRef = useRef<ConfirmationResult | null>(null);

  const handleGuest = async () => {
    try {
      await signInAnonymously(auth);
      router.replace('/(tabs)');
    } catch (error: any) {
      Alert.alert("Auth Error", error.message);
    }
  };

  const setupRecaptcha = () => {
    if (Platform.OS === 'web') {
      if (!window.recaptchaVerifier) {
        window.recaptchaVerifier = new RecaptchaVerifier(auth, 'recaptcha-container', {
          'size': 'invisible'
        });
      }
    }
  };

  const handleSendOTP = async () => {
    try {
      if (Platform.OS === 'web') {
        setupRecaptcha();
        const appVerifier = window.recaptchaVerifier;
        const result = await signInWithPhoneNumber(auth, phone, appVerifier);
        confirmationResultRef.current = result;
        setStep('otp');
      } else {
        Alert.alert("Info", "Native Phone Auth requires Firebase Native SDK config.");
      }
    } catch (error: any) {
      Alert.alert("OTP Error", error.message);
    }
  };

  const handleVerifyOTP = async () => {
    try {
      if (confirmationResultRef.current) {
        await confirmationResultRef.current.confirm(otp);
        router.replace('/(tabs)');
      }
    } catch (error: any) {
      Alert.alert("Verification Error", error.message);
    }
  };

  const handleGoogle = async () => {
    try {
      if (Platform.OS === 'web') {
        const provider = new GoogleAuthProvider();
        await signInWithPopup(auth, provider);
        router.replace('/(tabs)');
      } else {
        Alert.alert("Info", "Native Google Login requires expo-auth-session config.");
      }
    } catch (error: any) {
      Alert.alert("Google Auth Error", error.message);
    }
  };

  return (
    <View style={styles.container}>
      <View id="recaptcha-container" />
      <Text style={styles.title}>Puli Meka</Text>
      <Text style={styles.subtitle}>Sign in to save your score</Text>

      <View style={styles.form}>
        {step === 'phone' ? (
          <>
            <TextInput
              style={styles.input}
              placeholder="Mobile (+91...)"
              value={phone}
              onChangeText={setPhone}
              keyboardType="phone-pad"
            />
            <TouchableOpacity style={styles.button} onPress={handleSendOTP}>
              <Text style={styles.buttonText}>Send OTP</Text>
            </TouchableOpacity>
          </>
        ) : (
          <>
            <TextInput
              style={styles.input}
              placeholder="Enter OTP"
              value={otp}
              onChangeText={setOtp}
              keyboardType="number-pad"
            />
            <TouchableOpacity style={styles.button} onPress={handleVerifyOTP}>
              <Text style={styles.buttonText}>Verify & Login</Text>
            </TouchableOpacity>
          </>
        )}

        <View style={styles.divider}>
          <View style={styles.line} />
          <Text style={styles.dividerText}>OR</Text>
          <View style={styles.line} />
        </View>

        <TouchableOpacity style={[styles.button, styles.googleButton]} onPress={handleGoogle}>
          <Text style={styles.buttonText}>Login with Google</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.guestButton} onPress={handleGuest}>
          <Text style={styles.guestText}>Play as Guest</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 30, backgroundColor: '#fff' },
  title: { fontSize: 32, fontWeight: 'bold', textAlign: 'center', color: '#e74c3c' },
  subtitle: { fontSize: 16, textAlign: 'center', color: '#666', marginBottom: 40 },
  form: { width: '100%' },
  input: { borderWidth: 1, borderColor: '#ddd', padding: 15, borderRadius: 8, marginBottom: 15, fontSize: 16 },
  button: { backgroundColor: '#e74c3c', padding: 15, borderRadius: 8, alignItems: 'center' },
  googleButton: { backgroundColor: '#4285F4', marginTop: 10 },
  buttonText: { color: '#fff', fontWeight: 'bold', fontSize: 16 },
  divider: { flexDirection: 'row', alignItems: 'center', marginVertical: 20 },
  line: { flex: 1, height: 1, backgroundColor: '#eee' },
  dividerText: { marginHorizontal: 10, color: '#999' },
  guestButton: { marginTop: 20, padding: 10, alignItems: 'center' },
  guestText: { color: '#666', textDecorationLine: 'underline' }
});
