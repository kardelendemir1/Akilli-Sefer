import { useState } from 'react'

function App() {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [token, setToken] = useState<string | null>(null)
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    
    // Doğrudan backend FastAPI kodlarına istek atar
    const endpoint = isLogin ? "/api/auth/login" : "/api/auth/register"
    try {
      const res = await fetch(`http://127.0.0.1:8000${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || "Bağlantı hatası")
      
      if (isLogin) {
        setToken(data.access_token)
      } else {
        setIsLogin(true)
        setError("Kayıt başarılı! Şimdi giriş yapabilirsiniz.")
      }
    } catch(err: any) {
      setError(err.message)
    }
  }

  // Token başarıyla alındıysa bu ekran çıkar
  if (token) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center text-white p-4">
        <div className="w-full max-w-md p-8 bg-slate-800 rounded-2xl shadow-2xl border border-slate-700 text-center">
          <h1 className="text-3xl font-bold mb-4 text-emerald-400">Hoş Geldiniz 🎉</h1>
          <p className="text-slate-400 mb-6">Sisteme başarıyla giriş yaptınız. Güvenli oturum açıldı! Token'ınız backend'den onaylandı.</p>
          <div className="bg-slate-900 p-4 rounded-xl text-left border border-slate-700 mb-6 break-all">
            <span className="text-xs font-mono text-slate-500">JWT Token ({token.slice(0, 15)}...)</span>
          </div>
          <button onClick={() => setToken(null)} className="px-6 py-2 bg-rose-500 hover:bg-rose-600 rounded-lg font-medium transition-all w-full">Çıkış Yap</button>
        </div>
      </div>
    )
  }

  // Auth Form Ekranı
  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4 selection:bg-blue-500/30">
      <div className="w-full max-w-md bg-slate-800/50 backdrop-blur-xl p-8 rounded-2xl shadow-2xl border border-slate-700">
        <h2 className="text-3xl font-bold text-center text-white mb-2">
          {isLogin ? "Yönetici Paneli" : "Yeni Hesap Kur"}
        </h2>
        <p className="text-center text-slate-400 mb-8">
          {isLogin ? "Sisteme giriş yaparak seferleri yönetin" : "Anlık sefer sistemi için hesap oluşturun"}
        </p>

        {error && (
          <div className={`p-4 rounded-lg mb-6 text-sm ${error.includes("başarılı") ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/50" : "bg-rose-500/20 text-rose-400 border border-rose-500/50"}`}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">E-posta</label>
            <input 
              type="email" 
              className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-white transition-all outline-none"
              placeholder="admin@anliksefer.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Şifre</label>
            <input 
              type="password" 
              className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-white transition-all outline-none"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button 
            type="submit" 
            className="w-full py-4 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl font-bold shadow-lg shadow-blue-500/30 transition-all active:scale-[0.98]"
          >
            {isLogin ? "Güvenli Giriş" : "Kaydı Tamamla"}
          </button>
        </form>

        <p className="mt-8 text-center text-sm text-slate-400">
          {isLogin ? "Hesabınız yok mu? " : "Zaten hesabınız var mı? "}
          <button 
            type="button"
            onClick={() => { setIsLogin(!isLogin); setError(""); }} 
            className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
          >
            {isLogin ? "Sisteme Katılın" : "Buradan Giriş Yapın"}
          </button>
        </p>
      </div>
    </div>
  )
}

export default App
