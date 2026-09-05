import React from "react";
import {View,Text,TouchableOpacity,StyleSheet} from "react-native";

export default function GuardianPanel({result,onSafe,onHelp}) {
  const danger=result.concern>=70;
  return <View style={[s.card,danger&&s.danger]}>
    <Text style={s.kicker}>NEXORA GUARDIAN</Text>
    <Text style={s.title}>{danger?"Possible impact detected":"Physical context stable"}</Text>
    <Text style={s.score}>Concern {result.concern}%</Text>
    <Text style={s.reason}>{result.reasons.join(" • ")}</Text>
    {danger && <>
      <Text style={s.question}>Are you safe?</Text>
      <View style={s.row}>
        <TouchableOpacity style={s.safe} onPress={onSafe}><Text style={s.safeText}>I'M SAFE</Text></TouchableOpacity>
        <TouchableOpacity style={s.help} onPress={onHelp}><Text style={s.helpText}>NEED HELP</Text></TouchableOpacity>
      </View>
    </>}
  </View>
}
const s=StyleSheet.create({
  card:{backgroundColor:"#0B1728",borderColor:"#17456F",borderWidth:1,borderRadius:24,padding:18},
  danger:{borderColor:"#FF496B",backgroundColor:"#240B14"},
  kicker:{color:"#49E7FF",fontWeight:"900",fontSize:10,letterSpacing:1.5},
  title:{color:"#F8FBFF",fontSize:22,fontWeight:"900",marginTop:8},
  score:{color:"#FFC95C",fontSize:16,fontWeight:"900",marginTop:8},
  reason:{color:"#91A9C2",marginTop:6},
  question:{color:"white",fontSize:28,fontWeight:"900",marginTop:20},
  row:{flexDirection:"row",gap:10,marginTop:12},
  safe:{flex:1,backgroundColor:"#44F0B0",padding:15,borderRadius:16,alignItems:"center"},
  safeText:{color:"#001A12",fontWeight:"900"},
  help:{flex:1,backgroundColor:"#FF496B",padding:15,borderRadius:16,alignItems:"center"},
  helpText:{color:"white",fontWeight:"900"}
});