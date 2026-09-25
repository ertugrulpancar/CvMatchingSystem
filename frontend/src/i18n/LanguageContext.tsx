import { useMemo, useState, type ReactNode } from 'react'
import { LanguageContext, type Language, type LanguageContextValue } from './context'
import en from './en.json'
import tr from './tr.json'

const TRANSLATIONS: Record<Language, typeof tr> = { tr, en }

function resolve(source: unknown, path: string): string {
  const value = path.split('.').reduce<unknown>((current, key) => {
    if (current && typeof current === 'object' && key in current) {
      return (current as Record<string, unknown>)[key]
    }
    return undefined
  }, source)
  return typeof value === 'string' ? value : path
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>('tr')

  const value = useMemo<LanguageContextValue>(
    () => ({
      language,
      setLanguage,
      t: (path: string) => resolve(TRANSLATIONS[language], path),
    }),
    [language],
  )

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
}
