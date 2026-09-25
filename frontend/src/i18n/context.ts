import { createContext } from 'react'

export type Language = 'tr' | 'en'

export type LanguageContextValue = {
  language: Language
  setLanguage: (language: Language) => void
  t: (path: string) => string
}

export const LanguageContext = createContext<LanguageContextValue | null>(null)
