import React from 'react';
import {Pressable, StyleSheet, Text, TextInput, TextInputProps, View, ViewProps} from 'react-native';
import {C} from '../lib/theme';

export function ScreenTitle({kicker, title, copy}: {kicker?: string; title: string; copy?: string}) {
  return <View style={{marginBottom: 18}}>
    {kicker ? <Text style={s.kicker}>{kicker}</Text> : null}
    <Text style={s.h1}>{title}</Text>
    {copy ? <Text style={s.copy}>{copy}</Text> : null}
  </View>;
}

export function Card(props: ViewProps) { return <View {...props} style={[s.card, props.style]} />; }

export function Metric({label, value, meta, accent=C.purple}: {label: string; value: string; meta?: string; accent?: string}) {
  return <Card style={{flex: 1, minWidth: 150}}>
    <View style={[s.metricLine, {backgroundColor: accent}]} />
    <Text style={s.label}>{label}</Text><Text style={s.metric}>{value}</Text>{meta ? <Text style={s.meta}>{meta}</Text> : null}
  </Card>;
}

export function Field(props: TextInputProps & {label: string}) {
  const {label, ...rest} = props;
  return <View style={{gap: 6, marginBottom: 12}}><Text style={s.label}>{label}</Text><TextInput placeholderTextColor={C.muted} {...rest} style={[s.input, rest.style]} /></View>;
}

export function Button({title, onPress, secondary=false, danger=false, disabled=false}: {title:string; onPress:()=>void; secondary?:boolean; danger?:boolean; disabled?:boolean}) {
  return <Pressable disabled={disabled} onPress={onPress} style={({pressed})=>[s.button, secondary && s.buttonSecondary, danger && s.buttonDanger, (pressed||disabled)&&{opacity:.65}]}>
    <Text style={s.buttonText}>{title}</Text>
  </Pressable>;
}

export function SectionTitle({children}: {children: React.ReactNode}) { return <Text style={s.h2}>{children}</Text>; }
export function Empty({children}: {children: React.ReactNode}) { return <Card><Text style={s.meta}>{children}</Text></Card>; }

const s = StyleSheet.create({
  kicker:{color:C.cyan,fontSize:12,fontWeight:'800',letterSpacing:1.2,textTransform:'uppercase'},
  h1:{color:C.text,fontSize:30,fontWeight:'900',marginTop:3},
  h2:{color:C.text,fontSize:19,fontWeight:'850',marginTop:18,marginBottom:10},
  copy:{color:C.muted,fontSize:14,lineHeight:20,marginTop:5},
  card:{backgroundColor:C.panel,borderColor:C.border,borderWidth:1,borderRadius:18,padding:16,marginBottom:12},
  metricLine:{height:4,borderRadius:10,marginBottom:12},
  label:{color:C.muted,fontSize:12,fontWeight:'750'},
  metric:{color:C.text,fontSize:27,fontWeight:'900',marginTop:5},
  meta:{color:C.muted,fontSize:13,lineHeight:18,marginTop:4},
  input:{backgroundColor:C.panel2,borderWidth:1,borderColor:C.border,borderRadius:12,color:C.text,paddingHorizontal:13,paddingVertical:12,fontSize:15},
  button:{backgroundColor:C.purple,paddingHorizontal:16,paddingVertical:13,borderRadius:12,alignItems:'center',justifyContent:'center',marginTop:4},
  buttonSecondary:{backgroundColor:C.panel2,borderColor:C.border,borderWidth:1},
  buttonDanger:{backgroundColor:'#6a2630'},
  buttonText:{color:C.text,fontWeight:'850',fontSize:14},
});
