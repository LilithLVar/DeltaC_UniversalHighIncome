import { useState, useMemo, useCallback } from "react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine
} from "recharts";

// ─── Constants ───
const NUM_HH = 131_000_000;
const BASE_GDP = 29_000_000_000_000;
const BASE_YEAR = 2025;
const BASE_MEDIAN = 83_730;
const LVG_GLOBAL_BASELINE = 15000;
const TAU_CONSTANT = 13 / 12;

// ─── Color palette ───
const C = {
  wages: "#5B8DEF",
  swf: "#F5A623",
  ubi: "#2DD4A8",
  social: "#A78BFA",
  esop: "#FF6B6B",
  babyBonds: "#C084FC",
  dataRoyalty: "#38BDF8",
  privateInv: "#FB923C",
  carbon: "#34D399",
  deMonet: "#F472B6",
  deltaC: "#00F5FF",
  shapiro: "#EF4444",
  lattice: "#00F5FF",
};

const STREAM_META = [
  { key: "wages", label: "Residual Wages", color: C.wages },
  { key: "social", label: "Social Insurance", color: C.social },
  { key: "ubi", label: "Universal Basic Income", color: C.ubi },
  { key: "swf", label: "SWF Dividend", color: C.swf },
  { key: "esop", label: "ESOP / Co-op Share", color: C.esop },
  { key: "babyBonds", label: "Baby Bond Returns", color: C.babyBonds },
  { key: "dataRoyalty", label: "Data / AI Royalty", color: C.dataRoyalty },
  { key: "privateInv", label: "Private Investment", color: C.privateInv },
  { key: "carbon", label: "Carbon Dividend", color: C.carbon },
  { key: "deltaC", label: "Delta-C Coherence", color: C.deltaC },
  { key: "deMonet", label: "Demonetization Gain", color: C.deMonet },
];

// ─── Stress Test Scenarios ───
const STRESS_SCENARIOS = {
  none: { name: "No Stress Test", description: "Baseline simulation" },
  shockInjection: { name: "Shock Injection: 20% Automation Spike", description: "Sudden automation jump from 40% to 60% over 3 months", automationShockYear: 2035, automationShockAmount: 0.20, automationShockDuration: 0.25 },
  borderClosure: { name: "Border Closure: Capital Controls", description: "One nation imposes k > 0.7, testing clopen boundary", borderClosureYear: 2040, affectedNationKappa: 0.72 },
  sybilAttack: { name: "Sybil Attack: 10,000 Fake Chambers", description: "Mass fake chamber creation stress test", sybilAttackYear: 2038, fakeChambers: 10000 },
  treatyDivergence: { name: "Treaty Divergence: 5 Nations", description: "5 nations with k = 0.30, 0.45, 0.60, 0.68, 0.72", nations: [ { name: "Nation A", kappa: 0.30 }, { name: "Nation B", kappa: 0.45 }, { name: "Nation C", kappa: 0.60 }, { name: "Nation D", kappa: 0.68 }, { name: "Nation E", kappa: 0.72 } ] }
};

// ─── Defaults ───
const DEFAULTS = {
  endYear: 2060,
  automationPace: 2.5,
  baseGdpGrowth: 2.0,
  swfSeed: 100,
  swfContribRate: 1.5,
  swfReturnRate: 7.0,
  swfSpendRule: 3.0,
  ubiMonthly: 2000,
  ubiRampYears: 12,
  babyBondSeed: 5000,
  babyBondReturn: 7.0,
  babyBondMaturity: 18,
  esopGrowth: 7.0,
  dataRoyaltyMax: 12000,
  carbonBase: 900,
  carbonGrowth: 4.0,
  privateInvBase: 4185,
  privateInvGrowth: 3.5,
  demonetRate: 35,
  tauRate: 8.33,
  kappaThreshold: 0.7,
  stressScenario: 'none',
  enableTreatyRebalancing: true,
  enableSWF: true,
  enableUBI: true,
  enableBabyBonds: true,
  enableVAT: true,
  enableCarbon: true,
  enableAutoLevy: true,
  enableWealthTax: true,
  enableDataRoyalty: true,
  enableESOP: true,
  enableDemonet: true,
  enableDeltaC: false,
};

function simulate(p) {
  const data = [];
  let gdp = BASE_GDP;
  let swfBalance = p.enableSWF ? p.swfSeed * 1e9 : 0;
  let automationLevel = 0.05;
  
  let automationShockApplied = false;
  let borderClosureActive = false;
  let sybilAttackActive = false;
  let treatyRebalancingActive = p.enableTreatyRebalancing;
  
  const nations = p.stressScenario === 'treatyDivergence'
    ? STRESS_SCENARIOS.treatyDivergence.nations.map(n => ({ ...n, originalKappa: n.kappa }))
    : [];

  for (let year = BASE_YEAR; year <= p.endYear; year++) {
    const t = year - BASE_YEAR;

    // STRESS TEST INJECTIONS
    if (p.stressScenario === 'shockInjection' && !automationShockApplied) {
      const shockYear = STRESS_SCENARIOS.shockInjection.automationShockYear;
      if (year >= shockYear && year < shockYear + STRESS_SCENARIOS.shockInjection.automationShockDuration) {
        automationLevel = Math.min(0.95, automationLevel + STRESS_SCENARIOS.shockInjection.automationShockAmount);
        automationShockApplied = true;
      }
    }

    if (p.stressScenario === 'borderClosure' && !borderClosureActive) {
      if (year >= STRESS_SCENARIOS.borderClosure.borderClosureYear) {
        borderClosureActive = true;
      }
    }

    if (p.stressScenario === 'sybilAttack' && !sybilAttackActive) {
      if (year >= STRESS_SCENARIOS.sybilAttack.sybilAttackYear) {
        sybilAttackActive = true;
      }
    }

    if (p.stressScenario === 'treatyDivergence' && nations.length > 0 && treatyRebalancingActive) {
      const nationE = nations.find(n => n.originalKappa === 0.72);
      if (nationE && nationE.kappa > 0.7) {
        nationE.kappa = Math.max(0.65, nationE.kappa - 0.01);
      }
    }

    // AUTOMATION LEVEL
    const rawPace = p.automationPace / 100;
    automationLevel = Math.min(0.95, automationLevel + rawPace * (1 + automationLevel) * (1 - automationLevel));

    // GDP growth
    const autoBoost = automationLevel * 0.025;
    gdp = gdp * (1 + p.baseGdpGrowth / 100 + autoBoost);

    // Revenue factor
    let revenueFactor = 0.6; 
    if (p.enableVAT) revenueFactor += 0.15;
    if (p.enableAutoLevy) revenueFactor += 0.10;
    if (p.enableWealthTax) revenueFactor += 0.08;
    revenueFactor = Math.min(1.0, revenueFactor);

    // WAGES
    const autoFromBase = Math.max(0, automationLevel - 0.05) / 0.95; 
    const wageMultiplier = Math.max(0.04, 1 - autoFromBase * 0.96);
    const productivityPremium = 1 + autoFromBase * 0.3;
    const wages = Math.max(3000, 68660 * wageMultiplier * productivityPremium);

    // SOCIAL INSURANCE
    const socialGrowth = Math.pow(gdp / BASE_GDP, 0.25);
    const social = 10885 * socialGrowth * (1 + t * 0.005);

    // SWF
    let swfDiv = 0;
    if (p.enableSWF) {
      const contrib = (p.swfContribRate / 100) * gdp * revenueFactor;
      const returns = swfBalance * (p.swfReturnRate / 100);
      const distribution = swfBalance * (p.swfSpendRule / 100);
      swfBalance = swfBalance + contrib + returns - distribution;
      swfDiv = distribution / NUM_HH;
    }

    // UBI
    let ubi = 0;
    if (p.enableUBI) {
      const ramp = Math.min(1, t / Math.max(1, p.ubiRampYears));
      ubi = p.ubiMonthly * 12 * 1.5 * ramp * revenueFactor;
    }

    // ESOP
    let esop = 0;
    if (p.enableESOP) {
      const ramp = Math.min(1, t / 5);
      esop = 800 * Math.pow(1 + p.esopGrowth / 100, t) * Math.pow(gdp / BASE_GDP, 0.3) * ramp;
      esop = Math.min(esop, 30000);
    }

    // BABY BONDS
    let babyBonds = 0;
    if (p.enableBabyBonds && t >= p.babyBondMaturity) {
      const yearsActive = t - p.babyBondMaturity;
      const maturedValue = p.babyBondSeed * Math.pow(1 + p.babyBondReturn / 100, p.babyBondMaturity);
      const cohortFraction = Math.min(1, yearsActive / 25);
      babyBonds = maturedValue * (p.babyBondReturn / 100) * cohortFraction;
    }

    // DATA / AI ROYALTY
    let dataRoyalty = 0;
    if (p.enableDataRoyalty) {
      const ramp = Math.min(1, t / 8);
      dataRoyalty = p.dataRoyaltyMax * automationLevel * Math.pow(gdp / BASE_GDP, 0.4) * revenueFactor * ramp;
    }

    // CARBON DIVIDEND
    let carbon = 0;
    if (p.enableCarbon) {
      const ramp = Math.min(1, t / 3);
      carbon = p.carbonBase * Math.pow(1 + p.carbonGrowth / 100, t) * ramp;
    }

    // PRIVATE INVESTMENT
    const privateInv = p.privateInvBase * Math.pow(1 + p.privateInvGrowth / 100, t) * Math.pow(gdp / BASE_GDP, 0.2);

    // DELTA-C MECHANICS
    let deltaC = 0;
    let currentKappa = 0;
    let kappaStrainShapiro = 0;
    let kappaStrainLattice = 0;
    let isShapiroCollapsing = false;
    let isLatticeHealing = false;
    
    if (p.enableDeltaC) {
      const rawCoherence = LVG_GLOBAL_BASELINE * Math.pow(1 + (p.tauRate / 100), t);
      currentKappa = (autoFromBase * NUM_HH) / 187_000_000;
      let coherenceEfficiency = 1.0;
      
      if (currentKappa > p.kappaThreshold) {
        if (treatyRebalancingActive && p.stressScenario === 'treatyDivergence') {
          coherenceEfficiency = Math.max(0.85, 1.0 - (currentKappa - p.kappaThreshold) * 0.5);
          currentKappa = Math.max(p.kappaThreshold - 0.05, currentKappa - 0.01);
          isLatticeHealing = true;
        } else {
          coherenceEfficiency = Math.max(0.15, 1.0 - (currentKappa - p.kappaThreshold));
        }
      } else {
        isLatticeHealing = true;
      }
      
      kappaStrainLattice = currentKappa;
      deltaC = rawCoherence * coherenceEfficiency;
      
      kappaStrainShapiro = autoFromBase * 1.5 * (1 / revenueFactor);
      if (kappaStrainShapiro > 0.7) isShapiroCollapsing = true;
      
    } else {
      kappaStrainShapiro = autoFromBase * 1.5 * (1 / revenueFactor);
      if (kappaStrainShapiro > 0.7) isShapiroCollapsing = true;
      
      // Apply stress test impacts to Shapiro track
      if (p.stressScenario === 'shockInjection' && automationShockApplied) {
        kappaStrainShapiro = Math.min(1.5, kappaStrainShapiro * 1.8);
        revenueFactor = Math.max(0.3, revenueFactor * 0.8);
      }
      
      if (p.stressScenario === 'borderClosure' && borderClosureActive) {
        revenueFactor = Math.max(0.2, revenueFactor * 0.5);
        kappaStrainShapiro = Math.min(1.5, kappaStrainShapiro * 1.5);
      }
      
      if (p.stressScenario === 'sybilAttack' && sybilAttackActive) {
        revenueFactor = Math.max(0.1, revenueFactor * 0.4);
        kappaStrainShapiro = Math.min(1.5, kappaStrainShapiro * 2.0);
      }
      
      if (p.stressScenario === 'treatyDivergence') {
        if (nations.some(n => n.kappa > 0.7)) {
          revenueFactor = Math.max(0.25, revenueFactor * 0.6);
          kappaStrainShapiro = Math.min(1.5, kappaStrainShapiro * 1.6);
          isShapiroCollapsing = true;
        }
      }
      
      kappaStrainLattice = kappaStrainShapiro;
    }

    // STRESS TEST SPECIFIC CALCULATIONS
    let adjustedWages = wages;
    let adjustedSocial = social;
    let adjustedUbi = ubi;
    
    if (p.stressScenario === 'shockInjection' && automationShockApplied && !p.enableDeltaC) {
      adjustedWages = wages * 0.7;
    }
    
    if (p.stressScenario === 'borderClosure' && borderClosureActive && !p.enableDeltaC) {
      adjustedSocial = social * 0.6;
      adjustedUbi = ubi * 0.4;
    }
    
    if (p.stressScenario === 'sybilAttack' && sybilAttackActive && !p.enableDeltaC) {
      adjustedUbi = ubi * 0.3;
    }

    // DEMONETIZATION
    let deMonet = 0;
    if (p.enableDemonet) {
      const costReduction = (p.demonetRate / 100) * autoFromBase;
      if (costReduction > 0 && costReduction < 1) {
        const ppMultiplier = 1 / (1 - costReduction);
        deMonet = (adjustedWages + adjustedSocial + adjustedUbi + swfDiv + esop + babyBonds + dataRoyalty + privateInv + deltaC) * (ppMultiplier - 1);
      }
    }

    const nominalTotal = adjustedWages + adjustedSocial + adjustedUbi + swfDiv + esop + babyBonds + dataRoyalty + privateInv + deltaC;
    const effectiveTotal = nominalTotal + deMonet;

    const activeTrack = p.enableDeltaC ? 'Lattice' : 'Shapiro';
    const trackStatus = isShapiroCollapsing ? 'COLLAPSING' : (isLatticeHealing ? 'HEALING' : 'STABLE');

    data.push({
      year,
      wages: Math.round(p.enableDeltaC ? wages : adjustedWages),
      social: Math.round(p.enableDeltaC ? social : adjustedSocial),
      ubi: Math.round(p.enableDeltaC ? ubi : adjustedUbi),
      swf: Math.round(swfDiv),
      esop: Math.round(esop),
      babyBonds: Math.round(babyBonds),
      dataRoyalty: Math.round(dataRoyalty),
      privateInv: Math.round(privateInv),
      carbon: Math.round(carbon),
      deltaC: Math.round(deltaC),
      deMonet: Math.round(deMonet),
      total: Math.round(effectiveTotal),
      automationLevel: Math.round(automationLevel * 100),
      gdpT: +(gdp / 1e12).toFixed(1),
      swfT: +(swfBalance / 1e12).toFixed(1),
      kappa: +kappaStrainLattice.toFixed(2),
      kappaShapiro: +kappaStrainShapiro.toFixed(2),
      isCollapsing: isShapiroCollapsing,
      isHealing: isLatticeHealing,
      track: activeTrack,
      status: trackStatus,
    });
  }
  return data;
}

// ─── UI Components ───
function Slider({ label, value, onChange, min, max, step = 1, unit = "", disabled = false }) {
  const range = max - min;
  const pct = range > 0 ? ((value - min) / range) * 100 : 0;
  return (
    <div style={{ marginBottom: 10, opacity: disabled ? 0.35 : 1, pointerEvents: disabled ? "none" : "auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
        <span style={{ fontSize: 11, color: "#94a3b8", letterSpacing: 0.3 }}>{label}</span>
        <span style={{ fontSize: 11, color: "#e2e8f0", fontFamily: "'JetBrains Mono', monospace", fontWeight: 600 }}>
          {typeof value === 'number' ? value.toLocaleString() : value}{unit}
        </span>
      </div>
      <input
        type="range" min={min} max={max} step={step} value={value}
        onChange={e => onChange(parseFloat(e.target.value))}
        style={{
          width: "100%", height: 4, appearance: "none", borderRadius: 2,
          background: `linear-gradient(to right, ${disabled ? '#334155' : (value >= max * 0.8 ? '#EF4444' : '#5B8DEF')} ${pct}%, ${disabled ? '#1e293b' : '#334155'} ${pct}%)`,
          cursor: disabled ? "not-allowed" : "pointer", outline: "none",
        }}
      />
    </div>
  );
}

function Toggle({ label, checked, onChange, color, disabled = false }) {
  return (
    <div
      onClick={() => !disabled && onChange()}
      role="button"
      tabIndex={0}
      onKeyDown={e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); !disabled && onChange(); } }}
      style={{
        display: "flex", alignItems: "center", gap: 8, cursor: disabled ? "not-allowed" : "pointer",
        padding: "5px 0", fontSize: 12, color: disabled ? "#475569" : (checked ? "#e2e8f0" : "#64748b"),
        transition: "color 0.2s", userSelect: "none", opacity: disabled ? 0.5 : 1,
      }}
    >
      <div style={{
        width: 34, height: 18, borderRadius: 9, position: "relative",
        background: disabled ? "#334155" : (checked ? (color || "#5B8DEF") : "#334155"),
        transition: "background 0.2s", flexShrink: 0,
      }}>
        <div style={{
          width: 14, height: 14, borderRadius: 7, background: "#fff",
          position: "absolute", top: 2, left: checked ? 18 : 2,
          transition: "left 0.2s", boxShadow: "0 1px 3px rgba(0,0,0,0.3)"
        }} />
      </div>
      {label}
    </div>
  );
}

function StressTestSelector({ value, onChange }) {
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
        <span style={{ fontSize: 11, color: "#94a3b8", letterSpacing: 0.3 }}>Stress Test Scenario</span>
      </div>
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        style={{
          width: "100%", padding: "6px 8px", fontSize: 12, background: "#1e293b", 
          color: "#e2e8f0", border: "1px solid #334155", borderRadius: 4, cursor: "pointer",
          fontFamily: "'JetBrains Mono', monospace",
        }}
      >
        {Object.entries(STRESS_SCENARIOS).map(([key, scenario]) => (
          <option key={key} value={key}>
            {scenario.name}
          </option>
        ))}
      </select>
      {value !== 'none' && (
        <div style={{ fontSize: 10, color: "#64748b", marginTop: 4, paddingLeft: 2 }}>
          {STRESS_SCENARIOS[value]?.description}
        </div>
      )}
    </div>
  );
}

function Section({ title, children }) {
  const [open, setOpen] = useState(true);
  return (
    <div style={{ marginBottom: 12 }}>
      <div
        onClick={() => setOpen(!open)}
        style={{
          display: "flex", alignItems: "center", justifyContent: "space-between",
          cursor: "pointer", padding: "6px 0", borderBottom: "1px solid #1e293b",
          marginBottom: open ? 8 : 0,
        }}
      >
        <span style={{ fontSize: 10, fontWeight: 700, textTransform: "uppercase", letterSpacing: 1.5, color: "#64748b" }}>
          {title}
        </span>
        <span style={{ fontSize: 10, color: "#475569" }}>{open ? "▾" : "▸"}</span>
      </div>
      {open && children}
    </div>
  );
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  const total = payload.reduce((s, p) => s + (p.value || 0), 0);
  const row = payload[0]?.payload || {};
  
  const getStatusColor = () => {
    if (row.isCollapsing) return C.shapiro;
    if (row.isHealing) return C.lattice;
    return "#e2e8f0";
  };
  
  return (
    <div style={{
      background: "#0f172aee", border: "1px solid #1e293b", borderRadius: 8,
      padding: "12px 16px", fontSize: 11, color: "#e2e8f0", minWidth: 280,
      backdropFilter: "blur(8px)", zIndex: 50,
    }}>
      <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 6, color: "#f8fafc" }}>
        {label} — ${total.toLocaleString()}/yr
      </div>
      <div style={{ fontSize: 10, color: "#94a3b8", marginBottom: 8 }}>
        Automation: {row.automationLevel}% · GDP: ${row.gdpT}T
        {row.kappa > 0 && ` · k-Strain: ${row.kappa}`}
        {row.kappaShapiro > 0 && row.kappaShapiro !== row.kappa && ` · Shapiro k: ${row.kappaShapiro}`}
      </div>
      {row.status && (
        <div style={{ 
          fontSize: 10, color: getStatusColor(), 
          marginBottom: 8, fontWeight: 600, 
          padding: "2px 6px", 
          background: getStatusColor() + "20",
          borderRadius: 3,
          display: "inline-block"
        }}>
          {row.track} Track: {row.status}
        </div>
      )}
      {[...payload].reverse().filter(p => p.value > 0).map(p => (
        <div key={p.dataKey} style={{ display: "flex", justifyContent: "space-between", padding: "2px 0" }}>
          <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ width: 8, height: 8, borderRadius: 2, background: p.color, display: "inline-block" }} />
            {STREAM_META.find(s => s.key === p.dataKey)?.label}
          </span>
          <span style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 600 }}>
            ${p.value.toLocaleString()}
          </span>
        </div>
      ))}
    </div>
  );
}

const fmtK = v => v >= 1000 ? `$${Math.round(v / 1000)}k` : `$${v}`;
const fmtFull = v => `$${v.toLocaleString()}`;

// ─── Main component ───
export default function UHISimulator() {
  const [params, setParams] = useState(DEFAULTS);
  const [panelOpen, setPanelOpen] = useState(true);

  const set = useCallback((key, val) => {
    setParams(prev => ({ ...prev, [key]: val }));
  }, []);

  const data = useMemo(() => simulate(params), [params]);

  const firstRow = data[0];
  const lastRow = data[data.length - 1];
  const midIdx = Math.floor(data.length / 2);
  const midRow = data[midIdx];

  const collapseYear = data.find(d => d.isCollapsing)?.year;
  const healingYear = data.find(d => d.isHealing)?.year;

  const activeStreams = STREAM_META.filter(s => {
    if (s.key === "wages" || s.key === "social" || s.key === "privateInv") return true;
    if (s.key === "swf") return params.enableSWF;
    if (s.key === "ubi") return params.enableUBI;
    if (s.key === "esop") return params.enableESOP;
    if (s.key === "babyBonds") return params.enableBabyBonds;
    if (s.key === "dataRoyalty") return params.enableDataRoyalty;
    if (s.key === "carbon") return params.enableCarbon;
    if (s.key === "deltaC") return params.enableDeltaC;
    if (s.key === "deMonet") return params.enableDemonet;
    return true;
  });

  const applyPreset = (preset) => {
    const basePreset = { ...DEFAULTS };
    if (preset === "proactive") setParams(basePreset);
    if (preset === "reactive") setParams({ ...basePreset, swfSeed: 0, swfContribRate: 0.8, ubiRampYears: 18, babyBondSeed: 2000, automationPace: 2.5 });
    if (preset === "delayed") setParams({ ...basePreset, enableSWF: false, enableBabyBonds: false, enableDataRoyalty: false, enableESOP: false, ubiRampYears: 22, enableVAT: false, enableWealthTax: false });
    if (preset === "noAction") setParams({ ...basePreset, enableSWF: false, enableUBI: false, enableBabyBonds: false, enableVAT: false, enableCarbon: false, enableAutoLevy: false, enableWealthTax: false, enableDataRoyalty: false, enableESOP: false, enableDemonet: false });
    if (preset === "deltaC") {
      setParams({
        ...basePreset,
        enableDeltaC: true,
        enableSWF: false, enableUBI: false, enableBabyBonds: false,
        enableVAT: false, enableAutoLevy: false, enableWealthTax: false,
        enableDataRoyalty: false, enableESOP: false, enableCarbon: false
      });
    }
    if (preset === "clopen") {
      setParams({
        ...basePreset,
        enableDeltaC: true,
        stressScenario: 'treatyDivergence',
        enableTreatyRebalancing: true,
      });
    }
  };

  return (
    <div style={{
      fontFamily: "'IBM Plex Sans', 'Segoe UI', system-ui, sans-serif",
      background: "#0a0f1a", color: "#e2e8f0", minHeight: "100vh", display: "flex", flexDirection: "column",
    }}>
      <div style={{
        padding: "16px 24px", borderBottom: "1px solid #1e293b",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        background: "linear-gradient(180deg, #0f172a 0%, #0a0f1a 100%)",
        flexWrap: "wrap", gap: 12,
      }}>
        <div style={{ flex: 1, minWidth: 200 }}>
          <h1 style={{
            margin: 0, fontSize: 18, fontWeight: 800, letterSpacing: -0.5,
            background: "linear-gradient(135deg, #5B8DEF, #00F5FF)",
            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
          }}>
            Clopenly Glocal Economic Simulator
          </h1>
          <p style={{ margin: "2px 0 0", fontSize: 11, color: "#64748b" }}>
            Stress-Testing Shapiro's Extractive Modules vs. L'Varian Autopoietic Lattice
          </p>
        </div>
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          {[
            ["proactive", "Proactive"],
            ["reactive", "Reactive"],
            ["delayed", "Delayed"],
            ["noAction", "No Action"],
            ["deltaC", "Delta-C Phase"],
            ["clopen", "Clopen Stress"],
          ].map(([k, l]) => (
            <button key={k} onClick={() => applyPreset(k)} style={{
              padding: "5px 10px", fontSize: 10, fontWeight: 600, borderRadius: 4,
              border: "1px solid #334155", 
              background: k === "clopen" ? "#0f2d3a" : k === "deltaC" ? "#0f172a" : "#1e293b", 
              color: k === "clopen" ? C.lattice : k === "deltaC" ? C.deltaC : "#94a3b8", 
              cursor: "pointer", transition: "all 0.15s",
            }}>
              {l}
            </button>
          ))}
        </div>
      </div>

      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        <div style={{
          width: panelOpen ? 320 : 0, overflow: panelOpen ? "auto" : "hidden",
          transition: "width 0.3s", background: "#0f172a",
          borderRight: "1px solid #1e293b", flexShrink: 0,
          padding: panelOpen ? "16px" : 0,
        }}>
          {panelOpen && (
            <>
              <Section title="Stress Tests">
                <StressTestSelector value={params.stressScenario} onChange={v => set("stressScenario", v)} />
                {params.stressScenario === 'treatyDivergence' && (
                  <Toggle label="Enable k-Rebalancing Treaties" checked={params.enableTreatyRebalancing} onChange={() => set("enableTreatyRebalancing", !params.enableTreatyRebalancing)} color={C.lattice} />
                )}
              </Section>

              <Section title="Delta-C Sovereign Lattice">
                <Toggle label="Enable Delta-C Framework" checked={params.enableDeltaC} onChange={() => set("enableDeltaC", !params.enableDeltaC)} color={C.deltaC} />
                <Slider label="t-Expansion Factor" value={params.tauRate} onChange={v => set("tauRate", v)} min={1.0} max={15.0} step={0.1} unit="%" disabled={!params.enableDeltaC} />
                <Slider label="k-Strain Soft Threshold" value={params.kappaThreshold} onChange={v => set("kappaThreshold", v)} min={0.4} max={0.9} step={0.05} disabled={!params.enableDeltaC} />
              </Section>

              <Section title="Simulation Range">
                <Slider label="End Year" value={params.endYear} onChange={v => set("endYear", v)} min={2035} max={2100} step={5} />
              </Section>

              <Section title="Automation & Growth">
                <Slider label="Automation Pace" value={params.automationPace} onChange={v => set("automationPace", v)} min={0.5} max={6} step={0.1} unit="%/yr" />
                <Slider label="Base GDP Growth" value={params.baseGdpGrowth} onChange={v => set("baseGdpGrowth", v)} min={0.5} max={5} step={0.1} unit="%" />
              </Section>

              <Section title="Sovereign Wealth Fund">
                <Toggle label="Enable SWF" checked={params.enableSWF} onChange={() => set("enableSWF", !params.enableSWF)} color={C.swf} />
                <Slider label="Initial Seed" value={params.swfSeed} onChange={v => set("swfSeed", v)} min={0} max={500} step={10} unit="B" disabled={!params.enableSWF} />
                <Slider label="Annual Contribution" value={params.swfContribRate} onChange={v => set("swfContribRate", v)} min={0.1} max={5} step={0.1} unit="% GDP" disabled={!params.enableSWF} />
              </Section>

              <Section title="Universal Basic Income">
                <Toggle label="Enable UBI" checked={params.enableUBI} onChange={() => set("enableUBI", !params.enableUBI)} color={C.ubi} />
                <Slider label="Target (per adult/mo)" value={params.ubiMonthly} onChange={v => set("ubiMonthly", v)} min={250} max={5000} step={50} unit="$" disabled={!params.enableUBI} />
              </Section>

              <Section title="Other Systems">
                <Toggle label="ESOP Co-op Expansion" checked={params.enableESOP} onChange={() => set("enableESOP", !params.enableESOP)} color={C.esop} />
                <Toggle label="Data / AI Royalty" checked={params.enableDataRoyalty} onChange={() => set("enableDataRoyalty", !params.enableDataRoyalty)} color={C.dataRoyalty} />
                <Toggle label="Carbon Dividend" checked={params.enableCarbon} onChange={() => set("enableCarbon", !params.enableCarbon)} color={C.carbon} />
              </Section>

              <Section title="Revenue Sources">
                <Toggle label="Value-Added Tax (VAT)" checked={params.enableVAT} onChange={() => set("enableVAT", !params.enableVAT)} />
                <Toggle label="Automation Levy" checked={params.enableAutoLevy} onChange={() => set("enableAutoLevy", !params.enableAutoLevy)} />
                <Toggle label="Wealth Tax" checked={params.enableWealthTax} onChange={() => set("enableWealthTax", !params.enableWealthTax)} />
              </Section>

              <Section title="Demonetization & Deflation">
                <Toggle label="Enable Demonetization" checked={params.enableDemonet} onChange={() => set("enableDemonet", !params.enableDemonet)} color={C.deMonet} />
                <Slider label="Max Cost Reduction" value={params.demonetRate} onChange={v => set("demonetRate", v)} min={0} max={60} step={1} unit="%" disabled={!params.enableDemonet} />
              </Section>
            </>
          )}
        </div>

        <div style={{ display: "flex", alignItems: "center", flexShrink: 0 }}>
          <button onClick={() => setPanelOpen(!panelOpen)} style={{
            width: 20, height: 44, borderRadius: "0 6px 6px 0", background: "#1e293b", border: "1px solid #334155", borderLeft: "none", color: "#64748b", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            {panelOpen ? "◂" : "▸"}
          </button>
        </div>

        <div style={{ flex: 1, display: "flex", flexDirection: "column", padding: "16px 24px 16px 32px", minWidth: 0 }}>
          <div style={{ display: "flex", gap: 16, marginBottom: 16, flexWrap: "wrap" }}>
            {[
              { label: String(BASE_YEAR), value: fmtFull(firstRow?.total || 0), sub: "Starting Income", accent: "#94a3b8" },
              { label: String(midRow?.year), value: fmtFull(midRow?.total || 0), sub: midRow?.automationLevel + "% Auto", accent: "#5B8DEF" },
              { label: String(lastRow?.year), value: fmtFull(lastRow?.total || 0), sub: lastRow?.track + " " + (lastRow?.status ? "(" + lastRow.status + ")" : ""), accent: lastRow?.isCollapsing ? C.shapiro : (lastRow?.isHealing ? C.lattice : "#2DD4A8") },
              { label: "Lattice Dynamic", value: params.enableDeltaC ? "k: " + lastRow?.kappa : "$" + lastRow?.swfT + "T", sub: params.enableDeltaC ? "Base Space Strain" : "SWF Asset Total", accent: "#F5A623" },
              { label: "vs. Today", value: String(Math.round(((lastRow?.total || 0) / BASE_MEDIAN) * 100)) + "%", sub: "Baseline: " + fmtK(BASE_MEDIAN), accent: "#C084FC" },
            ].map((m, i) => (
              <div key={i} style={{ background: "#0f172a", border: "1px solid #1e293b", borderRadius: 8, padding: "10px 16px", flex: "1 1 140px", minWidth: 120 }}>
                <div style={{ fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: 1, color: "#475569", marginBottom: 2 }}>{m.label}</div>
                <div style={{ fontSize: 20, fontWeight: 800, color: m.accent, fontFamily: "'JetBrains Mono', monospace", letterSpacing: -0.5 }}>{m.value}</div>
                <div style={{ fontSize: 10, color: "#64748b", marginTop: 1 }}>{m.sub}</div>
              </div>
            ))}
          </div>

          {params.stressScenario !== 'none' && (
            <div style={{
              background: params.enableDeltaC ? "linear-gradient(90deg, " + C.lattice + "20, " + C.lattice + "10)" : "linear-gradient(90deg, " + C.shapiro + "20, " + C.shapiro + "10)",
              border: "1px solid " + (params.enableDeltaC ? C.lattice : C.shapiro),
              borderRadius: 8, padding: "12px 16px", marginBottom: 16,
              display: "flex", alignItems: "center", gap: 12,
            }}>
              <div style={{ fontSize: 24, opacity: 0.8 }}>⚡</div>
              <div>
                <div style={{ fontSize: 12, fontWeight: 700, color: params.enableDeltaC ? C.lattice : C.shapiro, marginBottom: 2 }}>
                  {STRESS_SCENARIOS[params.stressScenario]?.name || 'Custom Stress Test'}
                </div>
                <div style={{ fontSize: 10, color: "#94a3b8" }}>
                  {STRESS_SCENARIOS[params.stressScenario]?.description}
                  {collapseYear && !params.enableDeltaC && (
                    <span style={{ color: C.shapiro, marginLeft: 8 }}>⚠️ Collapse detected in {collapseYear}</span>
                  )}
                  {healingYear && params.enableDeltaC && (
                    <span style={{ color: C.lattice, marginLeft: 8 }}>✓ Healing active from {healingYear}</span>
                  )}
                </div>
              </div>
            </div>
          )}

          <div style={{ flex: 1, minHeight: 0 }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
                <defs>
                  {activeStreams.map(s => (
                    <linearGradient key={s.key} id={"g_" + s.key} x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={s.color} stopOpacity={0.8} />
                      <stop offset="100%" stopColor={s.color} stopOpacity={0.2} />
                    </linearGradient>
                  ))}
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="year" stroke="#475569" fontSize={11} tick={{ fill: "#64748b" }} tickLine={{ stroke: "#334155" }} />
                <YAxis stroke="#475569" fontSize={10} tick={{ fill: "#64748b" }} tickFormatter={fmtK} tickLine={{ stroke: "#334155" }} width={55} />
                <Tooltip content={<CustomTooltip />} />
                <ReferenceLine y={BASE_MEDIAN} stroke="#475569" strokeDasharray="6 4" />
                {activeStreams.map(s => (
                  <Area key={s.key} type="monotone" dataKey={s.key} stackId="1" stroke={s.color} fill={"url(#g_" + s.key + ")"} strokeWidth={0.5} />
                ))}
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px 16px", padding: "10px 0 4px", justifyContent: "center" }}>
            {activeStreams.map(s => (
              <div key={s.key} style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 10, color: "#94a3b8" }}>
                <div style={{ width: 10, height: 10, borderRadius: 2, background: s.color }} />
                {s.label}
              </div>
            ))}
          </div>

          {params.stressScenario !== 'none' && (
            <div style={{
              background: "#0f172a", border: "1px solid #1e293b", borderRadius: 8, 
              padding: "12px 16px", marginTop: 8, fontSize: 11,
            }}>
              <div style={{ color: "#64748b", marginBottom: 6, fontWeight: 600 }}>Stress Test Results:</div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                <div>
                  <span style={{ color: C.shapiro }}>Shapiro Track:</span> 
                  <span style={{ color: collapseYear ? C.shapiro : "#94a3b8", marginLeft: 8 }}>
                    {collapseYear ? "COLLAPSED in " + collapseYear : "Stable"}
                  </span>
                </div>
                <div>
                  <span style={{ color: C.lattice }}>L'Varian Lattice:</span> 
                  <span style={{ color: healingYear ? C.lattice : "#94a3b8", marginLeft: 8 }}>
                    {healingYear ? "HEALING from " + healingYear : "Stable"}
                  </span>
                </div>
                <div>
                  <span style={{ color: "#94a3b8" }}>Peak k (Shapiro):</span> 
                  <span style={{ marginLeft: 8 }}>
                    {data.reduce((max, d) => Math.max(max, d.kappaShapiro || 0), 0).toFixed(2)}
                  </span>
                </div>
                <div>
                  <span style={{ color: "#94a3b8" }}>Peak k (Lattice):</span> 
                  <span style={{ marginLeft: 8 }}>
                    {data.reduce((max, d) => Math.max(max, d.kappa || 0), 0).toFixed(2)}
                  </span>
                </div>
              </div>
              {params.stressScenario === 'treatyDivergence' && params.enableTreatyRebalancing && (
                <div style={{ marginTop: 8, paddingTop: 8, borderTop: "1px solid #1e293b", color: C.lattice, fontSize: 10 }}>
                  ✓ Treaty k-rebalancing active: Nation E healing from k=0.72 to k&lt;0.7
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
