import { Navigate } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'
import { EvidenceIcon, ScoreIcon, ShieldIcon } from '../components/FeatureIcons'
import { GoogleIcon } from '../components/GoogleIcon'
import { useLanguage } from '../i18n/useLanguage'

const FEATURES = [
  { Icon: ScoreIcon, key: 'login.feature1' },
  { Icon: EvidenceIcon, key: 'login.feature2' },
  { Icon: ShieldIcon, key: 'login.feature3' },
]

export function LoginPage() {
  const { session, isLoading, signInWithGoogle } = useAuth()
  const { t } = useLanguage()

  if (!isLoading && session) {
    return <Navigate to="/" replace />
  }

  return (
    <div className="login-page">
      <div className="login-intro">
        <span className="login-badge">{t('login.badge')}</span>
        <h1 className="login-title">{t('login.title')}</h1>
        <p className="login-subtitle">{t('login.subtitle')}</p>
      </div>

      <ul className="login-features">
        {FEATURES.map(({ Icon, key }) => (
          <li key={key} className="login-feature">
            <span className="login-feature-icon">
              <Icon />
            </span>
            <span>{t(key)}</span>
          </li>
        ))}
      </ul>

      <div className="login-card">
        <button
          type="button"
          className="btn btn-google btn-block"
          onClick={() => void signInWithGoogle()}
        >
          <GoogleIcon />
          {t('login.googleButton')}
        </button>
        <p className="privacy-notice">{t('login.privacyNote')}</p>
      </div>
    </div>
  )
}
