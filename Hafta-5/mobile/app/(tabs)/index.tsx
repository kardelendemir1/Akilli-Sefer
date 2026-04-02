import { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';

export default function LoginScreen() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    setError("");
    
    // Mobil uygulamalar local backend'e 127.0.0.1 (emulator vs ise 10.0.2.2) üzerinden bağlanır.
    // Şimdilik varsayılan api url'i koyuyoruz.
    const API_URL = "http://10.0.2.2:8000"; 
    const endpoint = isLogin ? "/api/auth/login" : "/api/auth/register";
    
    try {
      const res = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Sunucuyla bağlantı hatası");
      
      if (isLogin) {
        setToken(data.access_token);
      } else {
        setIsLogin(true);
        setError("🎉 Kayıt başarılı! Lütfen giriş yapınız.");
      }
    } catch(err: any) {
      setError("Hata: " + err.message + "\n\nNot: Expo uygulamasını çalıştırdığınız IP'ye ve FastAPI'nin çalıştığından emin olmalısınız.");
    } finally {
      setLoading(false);
    }
  };

  // JWT Başarılı ekranı
  if (token) {
    return (
      <View style={styles.container}>
        <Text style={styles.successTitle}>🎉 HOŞ GELDİN</Text>
        <Text style={styles.successText}>Sisteme mobil cihazınızdan başarıyla bağlandınız. JWT Token güvencesiyle kontrol sizde.</Text>
        <View style={styles.tokenBox}>
            <Text style={styles.tokenCode}>Token Sonu: ...{token.slice(-10)}</Text>
        </View>
        <TouchableOpacity style={styles.logoutBtn} onPress={() => setToken(null)}>
          <Text style={styles.btnText}>Oturumu Kapat</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // Giriş/Kayıt Çerçevesi
  return (
    <View style={styles.container}>
      <Text style={styles.header}>{isLogin ? "Oturum Aç" : "Kayıt Ol"}</Text>
      <Text style={styles.subhead}>Mobil Sefer Yönetim Paneli</Text>

      {error ? <Text style={styles.errorText}>{error}</Text> : null}

      <TextInput
        style={styles.input}
        placeholder="E-posta Adresi"
        placeholderTextColor="#64748b"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
      />
      <TextInput
        style={styles.input}
        placeholder="Güvelik Şifreniz"
        placeholderTextColor="#64748b"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />

      <TouchableOpacity style={styles.mainBtn} onPress={handleSubmit} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>{isLogin ? "Giris Yap" : "Kaydı Tamamla"}</Text>}
      </TouchableOpacity>

      <TouchableOpacity onPress={() => { setIsLogin(!isLogin); setError(""); }}>
        <Text style={styles.switchText}>
          {isLogin ? "Hesabın yok mu? Yeni Kayıt Oluştur" : "Hesabın var mı? Buradan Giriş Yap"}
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f172a', padding: 24, justifyContent: 'center' },
  header: { fontSize: 36, fontWeight: '800', color: '#f8fafc', textAlign: 'center', marginBottom: 8, letterSpacing: -0.5 },
  subhead: { fontSize: 16, color: '#94a3b8', textAlign: 'center', marginBottom: 40 },
  input: { backgroundColor: '#1e293b', borderWidth: 1, borderColor: '#334155', borderRadius: 16, padding: 18, color: '#f8fafc', marginBottom: 16, fontSize: 16 },
  mainBtn: { backgroundColor: '#3b82f6', padding: 18, borderRadius: 16, alignItems: 'center', marginTop: 12, shadowColor: '#3b82f6', shadowOffset: { width: 0, height: 8 }, shadowOpacity: 0.3, shadowRadius: 10, elevation: 8 },
  btnText: { color: '#ffffff', fontWeight: 'bold', fontSize: 18 },
  switchText: { color: '#60a5fa', textAlign: 'center', marginTop: 32, fontSize: 15, fontWeight: '600' },
  errorText: { color: '#ef4444', backgroundColor: '#7f1d1d33', padding: 16, borderRadius: 12, overflow: 'hidden', textAlign: 'center', marginBottom: 20 },
  successTitle: { fontSize: 36, color: '#10b981', textAlign: 'center', fontWeight: '800', marginBottom: 16 },
  successText: { fontSize: 16, color: '#cbd5e1', textAlign: 'center', marginBottom: 20, lineHeight: 26 },
  tokenBox: { backgroundColor: '#1e293b', padding: 12, borderRadius: 8, marginBottom: 32 },
  tokenCode: { color: '#94a3b8', textAlign: 'center', fontFamily: 'monospace' },
  logoutBtn: { backgroundColor: '#ef4444', padding: 18, borderRadius: 16, alignItems: 'center', shadowColor: '#ef4444', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.3, shadowRadius: 6 }
});
