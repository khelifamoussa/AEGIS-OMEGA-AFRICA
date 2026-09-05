export const PhysicalState = {
  NORMAL:"NORMAL",
  UNUSUAL_MOTION:"UNUSUAL_MOTION",
  IMPACT_CANDIDATE:"IMPACT_CANDIDATE",
  VERIFYING:"VERIFYING",
  RESPONSIVE:"RESPONSIVE",
  NO_RESPONSE:"NO_RESPONSE"
};

export function evaluatePhysicalState({accelMagnitude,gyroMagnitude,secondsSinceInteraction=0}) {
  const impact = accelMagnitude > 2.6;
  const rotation = gyroMagnitude > 3.0;

  if (impact && rotation) {
    return {
      state: PhysicalState.IMPACT_CANDIDATE,
      concern: 78,
      reasons:["high acceleration","high rotational change"]
    };
  }

  if (impact) {
    return {
      state: PhysicalState.UNUSUAL_MOTION,
      concern: 48,
      reasons:["high acceleration"]
    };
  }

  const continuity = Math.max(0,100-Math.min(70,secondsSinceInteraction*0.8));

  return {
    state: PhysicalState.NORMAL,
    concern: 8,
    continuity,
    reasons:["motion within prototype baseline"]
  };
}

export function nextGuardianAction(result) {
  if(result.state===PhysicalState.IMPACT_CANDIDATE) return "ASK_USER";
  if(result.concern>=70) return "VERIFY_AND_PREPARE_ESCALATION";
  return "MONITOR";
}