import { createContext } from 'react'

/** React context follows portal dialogs while keeping legacy routes independent. */
export const UIContext = createContext<'legacy' | 'v2'>('legacy')
