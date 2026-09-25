import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './auth/AuthProvider'
import { ProtectedRoute } from './auth/ProtectedRoute'
import { useAuth } from './auth/useAuth'
import type { Language } from './i18n/context'
import { LanguageProvider } from './i18n/LanguageContext'
import { useLanguage } from './i18n/useLanguage'
import { LoginPage } from './pages/LoginPage'
import { NewAnalysisPage } from './pages/NewAnalysisPage'

function LanguageSwitcher() {
  const { language, setLanguage } = useLanguage()

  return (
    <select value={language} onChange={(event) => setLanguage(event.target.value as Language)}>
      <option value="tr">Türkçe</option>
      <option value="en">English</option>
    </select>
  )
}

function SignOutButton() {
  const { session, signOut } = useAuth()
  const { t } = useLanguage()

  if (!session) {
    return null
  }

  return (
    <button type="button" onClick={() => void signOut()}>
      {t('app.signOut')}
    </button>
  )
}

function AppShell() {
  const { t } = useLanguage()

  return (
    <div className="app-shell">
      <header>
        <h1>{t('app.title')}</h1>
        <div className="header-actions">
          <LanguageSwitcher />
          <SignOutButton />
        </div>
      </header>
      <main>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <NewAnalysisPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <LanguageProvider>
      <BrowserRouter>
        <AuthProvider>
          <AppShell />
        </AuthProvider>
      </BrowserRouter>
    </LanguageProvider>
  )
}
