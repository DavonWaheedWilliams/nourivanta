import React,{useEffect,useState} from 'react';
import {ScrollView,StyleSheet,Text} from 'react-native';
import {router} from 'expo-router';
import {api} from '../../src/lib/api';
import {readHealthSnapshot} from '../../src/lib/health';
import {WearableRecord} from '../../src/lib/health.types';
import {useAuth} from '../../src/context/AuthContext';
import {Button,Card,Field,ScreenTitle,SectionTitle} from '../../src/components/UI';
import {C} from '../../src/lib/theme';

export default function Settings(){
 const {token,user,signOut}=useAuth();
 const [health,setHealth]=useState('Not checked');
 const [wearableStatus,setWearableStatus]=useState('No device sync in this session.');
 const [syncing,setSyncing]=useState(false);
 const [latest,setLatest]=useState<WearableRecord|null>(null);
 const [password,setPassword]=useState('');
 const [confirm,setConfirm]=useState('');
 const [deleteStatus,setDeleteStatus]=useState('');

 const loadLatest=async()=>{if(!token)return;try{const rows=await api<WearableRecord[]>('/wearables?days=14',{},token);setLatest(rows[0]||null);}catch{}};
 useEffect(()=>{loadLatest();},[token]);
 const check=async()=>{try{const r=await api<{ok:boolean;version:string;database:string}>('/health');setHealth(r.ok?`API online · v${r.version} · database ${r.database}`:'API reported a problem');}catch(e:any){setHealth(e.message||'API unavailable') }};
 const syncWearable=async()=>{if(!token||syncing)return;setSyncing(true);setWearableStatus('Requesting device health permission…');try{const snapshot=await readHealthSnapshot();const saved=await api<WearableRecord>('/wearables',{method:'POST',body:JSON.stringify(snapshot)},token);setLatest(saved);setWearableStatus(`${saved.source} synced for ${saved.metric_date}.`);}catch(e:any){setWearableStatus(e?.message||'Wearable sync failed.');}finally{setSyncing(false)}};
 const logout=async()=>{await signOut();router.replace('/login')};
 const deleteAccount=async()=>{if(!token)return;setDeleteStatus('');try{await api('/me',{method:'DELETE',body:JSON.stringify({password,confirm})},token);await signOut();router.replace('/login');}catch(e:any){setDeleteStatus(e.message||'Account could not be deleted')}};
 return <ScrollView style={s.screen} contentContainerStyle={s.content}><ScreenTitle kicker="Settings" title="NouriVanta Mobile" copy="Your mobile app and web app share the same account and core data."/>
 <Card><Text style={s.title}>{user?.display_name||user?.username}</Text><Text style={s.meta}>{user?.email}</Text></Card>
 <SectionTitle>Connection</SectionTitle><Card><Text style={s.title}>Mobile API</Text><Text style={s.meta}>{health}</Text><Button title="Run connection check" secondary onPress={check}/></Card>
 <SectionTitle>Wearable sync</SectionTitle><Card><Text style={s.title}>Apple Health / Health Connect</Text><Text style={s.meta}>Sync steps, sleep, resting heart rate, HRV and active calories. Permission stays under your phone's health settings.</Text><Button title={syncing?'Syncing…':'Sync health data now'} disabled={syncing||!token} onPress={syncWearable}/><Text style={s.meta}>{wearableStatus}</Text>{latest?<><Text style={s.valueSmall}>{latest.source} · {latest.metric_date}</Text><Text style={s.meta}>{latest.steps.toLocaleString()} steps · {latest.sleep_hours.toFixed(1)} h sleep · {latest.resting_hr||0} bpm resting HR · {latest.hrv_ms||0} ms HRV · {latest.active_calories.toFixed(0)} active kcal</Text></>:null}</Card>
 <SectionTitle>Targets</SectionTitle><Card><Text style={s.meta}>Calories</Text><Text style={s.value}>{user?.calorie_target} kcal</Text><Text style={s.meta}>Protein · Carbs · Fat</Text><Text style={s.value}>{user?.protein_target} g · {user?.carb_target} g · {user?.fat_target} g</Text><Text style={s.meta}>Water</Text><Text style={s.value}>{user?.water_target_ml} ml</Text></Card>
 <SectionTitle>Account</SectionTitle><Button title="Sign out" secondary onPress={logout}/>
 <Card style={{marginTop:16,borderColor:'#6a2630'}}><Text style={s.dangerTitle}>Delete NouriVanta account</Text><Text style={s.meta}>This permanently deletes the account and database records tied to it. This cannot be undone.</Text><Field label="Password" secureTextEntry value={password} onChangeText={setPassword}/><Field label='Type DELETE to confirm' autoCapitalize="characters" value={confirm} onChangeText={setConfirm}/>{deleteStatus?<Text style={s.error}>{deleteStatus}</Text>:null}<Button title="Permanently delete account" danger disabled={!password||confirm.trim().toUpperCase()!=='DELETE'} onPress={deleteAccount}/></Card>
 <SectionTitle>Release status</SectionTitle><Card><Text style={s.meta}>Native wearable permission code, secure token storage, camera barcode scanning, API-backed data and account deletion are included. Store submission still needs signed device builds, production API hosting, store privacy forms and device testing.</Text></Card>
 </ScrollView>}
const s=StyleSheet.create({screen:{flex:1,backgroundColor:C.bg},content:{padding:18,paddingTop:54,paddingBottom:100},title:{color:C.text,fontWeight:'900',fontSize:17},dangerTitle:{color:C.red,fontWeight:'900',fontSize:17},meta:{color:C.muted,fontSize:12,lineHeight:19,marginTop:4,marginBottom:10},value:{color:C.text,fontSize:20,fontWeight:'850',marginBottom:12,marginTop:3},valueSmall:{color:C.text,fontSize:15,fontWeight:'850',marginTop:12},error:{color:C.red,fontSize:12,marginBottom:8}});
