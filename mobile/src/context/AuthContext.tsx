import React, {createContext, useContext, useEffect, useMemo, useState} from 'react';
import * as SecureStore from 'expo-secure-store';
import {api} from '../lib/api';

type User = {id:number; username:string; email:string; display_name:string; calorie_target:number; protein_target:number; carb_target:number; fat_target:number; water_target_ml:number};
type AuthValue = {token:string|null; user:User|null; loading:boolean; signIn:(login:string,password:string)=>Promise<void>; signOut:()=>Promise<void>; refresh:()=>Promise<void>};
const AuthContext = createContext<AuthValue | null>(null);
const KEY='nourivanta.mobile.token';

export function AuthProvider({children}:{children:React.ReactNode}) {
  const [token,setToken]=useState<string|null>(null); const [user,setUser]=useState<User|null>(null); const [loading,setLoading]=useState(true);
  const load = async (t:string) => { const u=await api<User>('/me',{},t); setToken(t); setUser(u); };
  useEffect(()=>{(async()=>{try{const t=await SecureStore.getItemAsync(KEY); if(t) await load(t);}catch{}finally{setLoading(false);}})();},[]);
  const signIn=async(login:string,password:string)=>{const r=await api<{access_token:string;user:User}>('/auth/login',{method:'POST',body:JSON.stringify({login,password})}); await SecureStore.setItemAsync(KEY,r.access_token); setToken(r.access_token); setUser(r.user);};
  const signOut=async()=>{await SecureStore.deleteItemAsync(KEY);setToken(null);setUser(null);};
  const refresh=async()=>{if(token) await load(token);};
  const value=useMemo(()=>({token,user,loading,signIn,signOut,refresh}),[token,user,loading]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
export const useAuth=()=>{const v=useContext(AuthContext);if(!v) throw new Error('AuthProvider missing');return v;};
