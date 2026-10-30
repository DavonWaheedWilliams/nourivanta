import React,{useState} from 'react';
import {KeyboardAvoidingView,Platform,SafeAreaView,StyleSheet,Text,View} from 'react-native';
import {router} from 'expo-router';
import {Button,Card,Field} from '../src/components/UI';
import {C} from '../src/lib/theme';
import {useAuth} from '../src/context/AuthContext';

export default function Login(){
 const {signIn}=useAuth(); const [login,setLogin]=useState(''); const [password,setPassword]=useState(''); const [busy,setBusy]=useState(false); const [error,setError]=useState('');
 const go=async()=>{setBusy(true);setError('');try{await signIn(login,password);router.replace('/(tabs)');}catch(e:any){setError(e?.message||'Unable to sign in');}finally{setBusy(false);}};
 return <SafeAreaView style={s.safe}><KeyboardAvoidingView behavior={Platform.OS==='ios'?'padding':undefined} style={s.wrap}>
   <View><Text style={s.brand}>NouriVanta</Text><Text style={s.tag}>Nutrition · Training · Recovery</Text></View>
   <Card style={{marginTop:28}}><Text style={s.title}>Welcome back</Text><Text style={s.copy}>Use the same account you already use in NouriVanta Web.</Text>
     <Field label="Username or email" autoCapitalize="none" value={login} onChangeText={setLogin}/>
     <Field label="Password" secureTextEntry value={password} onChangeText={setPassword}/>
     {error?<Text style={s.error}>{error}</Text>:null}<Button title={busy?'Signing in…':'Sign in'} onPress={go} disabled={busy||!login||!password}/>
   </Card>
   <Text style={s.foot}>Your existing workouts, nutrition logs and goals stay in the same database.</Text>
 </KeyboardAvoidingView></SafeAreaView>;
}
const s=StyleSheet.create({safe:{flex:1,backgroundColor:C.bg},wrap:{flex:1,justifyContent:'center',padding:22},brand:{color:C.text,fontSize:38,fontWeight:'900'},tag:{color:C.cyan,fontSize:14,fontWeight:'700',marginTop:4},title:{color:C.text,fontSize:24,fontWeight:'900',marginBottom:4},copy:{color:C.muted,fontSize:14,lineHeight:20,marginBottom:18},error:{color:C.red,marginBottom:10},foot:{color:C.muted,textAlign:'center',fontSize:12,lineHeight:18,marginTop:12}});
