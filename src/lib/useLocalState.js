'use client';

import { useEffect, useState } from 'react';
import { loadState, saveState } from './localDb';

export function useLocalState() {
  const [state, setState] = useState(loadState());

  useEffect(() => {
    // keep in sync across tabs
    const onStorage = (e) => {
      if (e.key) setState(loadState());
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, []);

  const update = (mutator) => {
    setState((prev) => {
      const next = mutator(structuredClone(prev));
      saveState(next);
      return next;
    });
  };

  return { state, update };
}
