'use client';
import { MyUser } from '@/types';
import React, { createContext, useContext, useState } from 'react';

interface IAuthorizationContext {
  user: MyUser;
  token: string;
  setToken: React.Dispatch<React.SetStateAction<string>>;
}

interface IAuthorizationProviderProps {
  user: MyUser;
  token: string;
}

const AuthorizationContext = createContext<IAuthorizationContext | null>(null);

const AuthorizationProvider = ({
  children,
  value: { user, token: originToken },
}: React.PropsWithChildren<{ value: IAuthorizationProviderProps }>) => {
  const [token, setToken] = useState(originToken);
  return (
    <AuthorizationContext.Provider value={{ user, token, setToken }}>
      {children}
    </AuthorizationContext.Provider>
  );
};

export default AuthorizationProvider;

export function useAuthorization() {
  const context = useContext(AuthorizationContext);
  if (!context) {
    throw new Error(
      'useAuthorization must be used within a AuthorizationProvider'
    );
  }
  return context;
}
