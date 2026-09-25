import { Navigate } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'
import { useLanguage } from '../i18n/useLanguage'

export function LoginPage() {
  const { session, isLoading, signInWithGoogle } = useAuth()
  const { t } = useLanguage()

  if (!isLoading && session) {
    return <Navigate to="/" replace />
  }

  return (
    <div className="login-page">
      <h2>{t('login.title')}</h2>
      <p>{t('login.description')}</p>
      <button type="button" onClick={() => void signInWithGoogle()}>
        {t('login.googleButton')}
      </button>
    </div>
  )
}
