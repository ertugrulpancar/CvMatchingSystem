import type { Language } from './i18n/context'
import { LanguageProvider } from './i18n/LanguageContext'
import { NewAnalysisPage } from './pages/NewAnalysisPage'
import { useLanguage } from './i18n/useLanguage'

function LanguageSwitcher() {
  const { language, setLanguage } = useLanguage()

  return (
    <select value={language} onChange={(event) => setLanguage(event.target.value as Language)}>
      <option value="tr">Türkçe</option>
      <option value="en">English</option>
    </select>
  )
}

function AppShell() {
  const { t } = useLanguage()

  return (
    <div className="app-shell">
      <header>
        <h1>{t('app.title')}</h1>
        <LanguageSwitcher />
      </header>
      <main>
        <NewAnalysisPage />
      </main>
    </div>
  )
}

export default function App() {
  return (
    <LanguageProvider>
      <AppShell />
    </LanguageProvider>
  )
}
