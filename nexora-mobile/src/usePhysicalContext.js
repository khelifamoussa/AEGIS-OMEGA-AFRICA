import { useEffect, useMemo, useState } from "react";
import * as Location from "expo-location";
import { Accelerometer, Gyroscope } from "expo-sensors";

export function usePhysicalContext() {
  const [accel,setAccel]=useState({x:0,y:0,z:0});
  const [gyro,setGyro]=useState({x:0,y:0,z:0});
  const [location,setLocation]=useState(null);

  useEffect(()=>{
    Accelerometer.setUpdateInterval(100);
    Gyroscope.setUpdateInterval(100);
    const a=Accelerometer.addListener(setAccel);
    const g=Gyroscope.addListener(setGyro);
    let alive=true;
    (async()=>{
      const p=await Location.requestForegroundPermissionsAsync();
      if(p.status==="granted" && alive){
        const pos=await Location.getCurrentPositionAsync({accuracy:Location.Accuracy.Balanced});
        if(alive) setLocation(pos);
      }
    })();
    return()=>{alive=false;a.remove();g.remove();};
  },[]);

  const accelMagnitude=useMemo(()=>Math.sqrt(accel.x**2+accel.y**2+accel.z**2),[accel]);
  const gyroMagnitude=useMemo(()=>Math.sqrt(gyro.x**2+gyro.y**2+gyro.z**2),[gyro]);
  return {accel,gyro,location,accelMagnitude,gyroMagnitude};
}