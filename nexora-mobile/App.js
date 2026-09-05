import React,{useMemo,useState} from "react";
import {SafeAreaView,View,Text,StyleSheet,StatusBar,ScrollView} from "react-native";
import {usePhysicalContext} from "./src/usePhysicalContext";
import {evaluatePhysicalState} from "./src/physicalIntelligence";
import GuardianPanel from "./src/GuardianPanel";

export default function App(){
  const p=usePhysicalContext();
  const [lastInteraction,setLastInteraction]=useState(Date.now());
  const [status,setStatus]=useState("UNKNOWN");

  const result=useMemo(()=>evaluatePhysicalState({
    accelMagnitude:p.accelMagnitude,
    gyroMagnitude:p.gyroMagnitude,
    secondsSinceInteraction:(Date.now()-lastInteraction)/1000
  }),[p.accelMagnitude,p.gyroMagnitude,lastInteraction]);

  const safe=()=>{setStatus("RESPONSIVE");setLastInteraction(Date.now());};
  const help=()=>{setStatus("HELP_REQUESTED");setLastInteraction(Date.now());};

  return <SafeAreaView style={s.safe}>
    <StatusBar barStyle="light-content"/>
    <ScrollView contentContainerStyle={s.body}>
      <Text style={s.logo}>NEXORA</Text>
      <Text style={s.tag}>PHYSICAL AI GUARDIAN • v0.3</Text>

      <View style={s.hero}>
        <Text style={s.heroTitle}>Human Continuity</Text>
        <Text style={s.heroValue}>{result.continuity ?? (status==="RESPONSIVE"?100:62)}%</Text>
        <Text style={s.heroSub}>Prototype estimate — not a medical measurement.</Text>
      </View>

      <GuardianPanel result={result} onSafe={safe} onHelp={help}/>

      <View style={s.grid}>
        <View style={s.metric}><Text style={s.label}>ACCEL</Text><Text style={s.value}>{p.accelMagnitude.toFixed(2)}</Text></View>
        <View style={s.metric}><Text style={s.label}>GYRO</Text><Text style={s.value}>{p.gyroMagnitude.toFixed(2)}</Text></View>
      </View>

      <View style={s.card}>
        <Text style={s.label}>CURRENT RESPONSE STATE</Text>
        <Text style={s.state}>{status}</Text>
        <Text style={s.small}>Lat: {p.location?.coords?.latitude?.toFixed(5) ?? "—"}</Text>
        <Text style={s.small}>Lon: {p.location?.coords?.longitude?.toFixed(5) ?? "—"}</Text>
      </View>

      <Text style={s.disclaimer}>Research prototype only. It does not contact emergency services or diagnose injury.</Text>
    </ScrollView>
  </SafeAreaView>
}
const s=StyleSheet.create({
  safe:{flex:1,backgroundColor:"#040812"},
  body:{padding:20,paddingBottom:60},
  logo:{color:"#F8FBFF",fontSize:34,fontWeight:"900",letterSpacing:6},
  tag:{color:"#49E7FF",fontSize:9,letterSpacing:2,marginTop:4,marginBottom:20},
  hero:{backgroundColor:"#0A1730",borderColor:"#18466F",borderWidth:1,borderRadius:26,padding:20,marginBottom:14},
  heroTitle:{color:"#92A9C2",fontSize:12},
  heroValue:{color:"#47F0B0",fontSize:58,fontWeight:"900",marginTop:4},
  heroSub:{color:"#92A9C2",fontSize:11},
  grid:{flexDirection:"row",gap:10,marginTop:14},
  metric:{flex:1,backgroundColor:"#091321",borderColor:"#173B63",borderWidth:1,borderRadius:18,padding:16},
  label:{color:"#92A9C2",fontSize:10,fontWeight:"800",letterSpacing:1},
  value:{color:"#49E7FF",fontSize:22,fontWeight:"900",marginTop:5},
  card:{backgroundColor:"#091321",borderColor:"#173B63",borderWidth:1,borderRadius:20,padding:16,marginTop:14},
  state:{color:"#F8FBFF",fontSize:20,fontWeight:"900",marginTop:6},
  small:{color:"#92A9C2",fontSize:12,marginTop:5},
  disclaimer:{color:"#71869D",fontSize:10,lineHeight:15,marginTop:18,textAlign:"center"}
});