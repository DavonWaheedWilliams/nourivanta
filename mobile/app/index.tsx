import React from 'react';
import {ActivityIndicator, View} from 'react-native';
import {Redirect} from 'expo-router';
import {useAuth} from '../src/context/AuthContext';
import {C} from '../src/lib/theme';
export default function Index(){const {token,loading}=useAuth();if(loading)return <View style={{flex:1,alignItems:'center',justifyContent:'center',backgroundColor:C.bg}}><ActivityIndicator color={C.cyan}/></View>;return <Redirect href={token?'/(tabs)':'/login'} />;}
