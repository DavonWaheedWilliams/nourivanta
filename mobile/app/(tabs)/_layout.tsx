import React from 'react';
import {Redirect,Tabs} from 'expo-router';
import {Ionicons} from '@expo/vector-icons';
import {useAuth} from '../../src/context/AuthContext';
import {C} from '../../src/lib/theme';

const icon=(name:any)=>(p:any)=><Ionicons name={name} size={p.size} color={p.color}/>;
export default function TabsLayout(){const {token}=useAuth();if(!token)return <Redirect href="/login"/>;return <Tabs screenOptions={{headerShown:false,tabBarStyle:{backgroundColor:'#091424',borderTopColor:C.border,height:68,paddingBottom:8,paddingTop:8},tabBarActiveTintColor:C.cyan,tabBarInactiveTintColor:C.muted,tabBarLabelStyle:{fontSize:10,fontWeight:'700'}}}>
 <Tabs.Screen name="index" options={{title:'Today',tabBarIcon:icon('pulse')}}/>
 <Tabs.Screen name="nutrition" options={{title:'Nutrition',tabBarIcon:icon('restaurant')}}/>
 <Tabs.Screen name="workouts" options={{title:'Workouts',tabBarIcon:icon('barbell')}}/>
 <Tabs.Screen name="readiness" options={{title:'Readiness',tabBarIcon:icon('heart')}}/>
 <Tabs.Screen name="progress" options={{title:'Progress',tabBarIcon:icon('trending-up')}}/>
 <Tabs.Screen name="settings" options={{title:'Settings',tabBarIcon:icon('settings')}}/>
 </Tabs>}
