import React from 'react';
import {Stack} from 'expo-router';
import {StatusBar} from 'expo-status-bar';
import {AuthProvider} from '../src/context/AuthContext';
import {C} from '../src/lib/theme';

export default function RootLayout(){
  return <AuthProvider>
    <StatusBar style="light" />
    <Stack screenOptions={{headerShown:false,contentStyle:{backgroundColor:C.bg}}} />
  </AuthProvider>;
}
