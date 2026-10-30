import React,{useCallback,useEffect,useState} from 'react';
import {RefreshControl,ScrollView,StyleSheet,Text,View} from 'react-native';
import {api,todayISO} from '../../src/lib/api';
import {useAuth} from '../../src/context/AuthContext';
import {Card,Empty,Metric,ScreenTitle,SectionTitle} from '../../src/components/UI';
import {C} from '../../src/lib/theme';

type D={date:string;totals:{calories:number;protein:number;carbs:number;fat:number;water:number};targets:{calories:number;protein:number;carbs:number;fat:number;water:number};readiness:number;workout_count:number;workout_minutes:number;latest_weight_lb:number|null;recent_workouts:any[]};
export default function Dashboard(){const {token,user}=useAuth();const [d,setD]=useState<D|null>(null);const [loading,setLoading]=useState(false);const load=useCallback(async()=>{if(!token)return;setLoading(true);try{setD(await api<D>(`/dashboard?day=${todayISO()}`,{},token));}finally{setLoading(false)}},[token]);useEffect(()=>{load()},[load]);
 const pct=(v:number,t:number)=>`${Math.round(v)}/${Math.round(t)}`;
 return <ScrollView style={s.screen} contentContainerStyle={s.content} refreshControl={<RefreshControl refreshing={loading} onRefresh={load} tintColor={C.cyan}/>}>
  <ScreenTitle kicker="Today" title={`Welcome back, ${user?.display_name||user?.username||''}`} copy="Daily fuel, training and recovery in one mobile view."/>
  {d?<><View style={s.grid}><Metric label="Calories" value={`${Math.round(d.totals.calories)}`} meta={`of ${d.targets.calories} kcal`} accent={C.purple}/><Metric label="Protein" value={`${Math.round(d.totals.protein)} g`} meta={`of ${d.targets.protein} g`} accent={C.cyan}/></View><View style={s.grid}><Metric label="Carbs" value={`${Math.round(d.totals.carbs)} g`} meta={`of ${d.targets.carbs} g`} accent={C.orange}/><Metric label="Fat" value={`${Math.round(d.totals.fat)} g`} meta={`of ${d.targets.fat} g`} accent={C.pink}/></View>
  <SectionTitle>Daily balance</SectionTitle><View style={s.grid}><Metric label="Water" value={`${Math.round(d.totals.water/29.5735)} fl oz`} meta={`${Math.round(d.totals.water)}/${d.targets.water} ml`} accent={C.blue}/><Metric label="Readiness" value={`${d.readiness}/100`} meta={d.readiness>=80?'High readiness':d.readiness>=60?'Moderate readiness':'Recovery focus'} accent={d.readiness>=80?C.green:d.readiness>=60?C.cyan:C.orange}/></View><View style={s.grid}><Metric label="Training" value={`${d.workout_minutes} min`} meta={`${d.workout_count} session${d.workout_count===1?'':'s'}`} accent={C.purple}/><Metric label="Weight" value={d.latest_weight_lb?`${d.latest_weight_lb.toFixed(1)} lb`:'—'} meta="Latest measurement" accent={C.green}/></View>
  <SectionTitle>Recent workouts</SectionTitle>{d.recent_workouts.length?d.recent_workouts.map(w=><Card key={w.id}><Text style={s.itemTitle}>{w.name}</Text><Text style={s.itemMeta}>{w.date} · {w.category} · {w.duration_min} min</Text></Card>):<Empty>No workouts logged yet.</Empty>}</>:<Empty>Pull down to load your dashboard.</Empty>}
 </ScrollView>}
const s=StyleSheet.create({screen:{flex:1,backgroundColor:C.bg},content:{padding:18,paddingTop:54,paddingBottom:100},grid:{flexDirection:'row',gap:10},itemTitle:{color:C.text,fontWeight:'850',fontSize:15},itemMeta:{color:C.muted,fontSize:12,marginTop:5}});
