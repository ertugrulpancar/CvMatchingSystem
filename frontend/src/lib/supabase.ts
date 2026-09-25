import { createClient } from '@supabase/supabase-js'

// Frontend, veritabanına doğrudan erişmez; supabase-js burada SADECE Google
// girişi ve oturum (JWT) yönetimi için kullanılır. Tüm veri erişimi backend
// üzerinden gider (CLAUDE.md mimari kuralı).
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
