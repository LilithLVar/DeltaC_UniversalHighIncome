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

// Delta-C Specific Constants
const LVG_GLOBAL_BASELINE = 15000; // Human sovereignty base index ($/HH equivalent)
const TAU_CONSTANT = 13 / 12;      // 1.0833 L'Varian expansion factor

// ─── Color palette ───
const C = {
  wages:       "#5B8DEF",
  swf:         "#F5A623",
  ubi:         "#2DD4A8",
  social:      "#A78BFA",
  esop:        "#FF6B6B",
  babyBonds:   "#C084FC",
  dataRoyalty: "#38BDF8",
  privateInv:  "#FB923C",
  carbon:      "#34D399",
  deMonet:     "#F472B6",
  deltaC:      "#00F5FF", // Crystalline cyan for Delta-C Coherence
};

const STREAM_META = [
  { key: "wages",       label: "Residual Wages",       color: C.wages },
  { key: "social",      label: "Social Insurance",     color: C.social },
  { key: "ubi",         label: "Universal Basic Income",color: C.ubi },
  { key: "swf",         label: "SWF Dividend",         color: C.swf },
  { key: "esop",        label: "ESOP / Co-op Share",   color: C.esop },
  { key: "babyBonds",   label: "Baby Bond Returns",    color: C.babyBonds },
  { key: "dataRoyalty", label: "Data / AI Royalty",    color: C.dataRoyalty },
  { key: "privateInv",  label: "Private Investment",   color: C.privateInv },
  { key: "carbon",      label: "Carbon Dividend",      color: C.carbon },
  { key: "deltaC",      label: "Delta-C Coherence",    color: C.deltaC },
  { key: "deMonet",     label: "Demonetization Gain",  color: C.deMonet },
];

// ─── Defaults ───
const DEFAULTS = {
  endYear: 2060,
  automationPace: 2.5,    // % per year
  baseGdpGrowth: 2.0,      // % real
  swfSeed: 100,            // $B
  swfContribRate: 1.5,     // % of GDP
  swfReturnRate: 7.0,      // %
  swfSpendRule: 3.0,       // %
  ubiMonthly: 2000,        // $/month per adult
  ubiRampYears: 12,
  babyBondSeed: 5000,      // $
  babyBondReturn: 7.0,     // %
  babyBondMaturity: 18,    // years
  esopGrowth: 7.0,         // %/yr coverage growth
  dataRoyaltyMax: 12000,   // $/HH at full automation
  carbonBase: 900,         // $/HH/yr
  carbonGrowth: 4.0,       // %/yr
  privateInvBase: 4185,    // $/HH/yr
  privateInvGrowth: 3.5,   // %/yr
  demonetRate: 35,         // % cost reduction at full automation
  // Delta-C Specific Controls
  tauRate: 8.33,           // Base expansion rate (~13/12 logic)
  kappaThreshold: 0.7,     // Soft structural harmony cap
  // Toggles
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
  enableDeltaC: false,     // Toggled off by default to preserve baseline Shapiro presets
};

// ─── Simulation engine ───
function simulate(p) {
  const data = [];
  let gdp = BASE_GDP;
  let swfBalance = p.enableSWF ? p.swfSeed * 1e9 : 0;
  let automationLevel = 0.05; // 5% in 2025

  for (let year = BASE_YEAR; year <= p.endYear; year++) {
    const t = year - BASE_YEAR;

    // Automation level (sigmoid-ish)
    const rawPace = p.automationPace / 100;
    automationLevel = Math.min(0.95, automationLevel + rawPace * (1 + automationLevel) * (1 - automationLevel));

    // GDP grows faster with more automation
    const autoBoost = automationLevel * 0.025;
    gdp = gdp * (1 + p.baseGdpGrowth / 100 + autoBoost);

    // Revenue factor for taxation tracks
    let revenueFactor = 0.6; 
    if (p.enableVAT) revenueFactor += 0.15;
    if (p.enableAutoLevy) revenueFactor += 0.10;
    if (p.enableWealthTax) revenueFactor += 0.08;
    revenueFactor = Math.min(1.0, revenueFactor);

    // ── WAGES ──
    const autoFromBase = Math.max(0, automationLevel - 0.05) / 0.95; 
    const wageMultiplier = Math.max(0.04, 1 - autoFromBase * 0.96);
    const productivityPremium = 1 + autoFromBase * 0.3;
    const wages = Math.max(3000, 68660 * wageMultiplier * productivityPremium);

    // ── SOCIAL INSURANCE ──
    const socialGrowth = Math.pow(gdp / BASE_GDP, 0.25);
    const social = 10885 * socialGrowth * (1 + t * 0.005);

    // ── SWF ──
    let swfDiv = 0;
    if (p.enableSWF) {
      const contrib = (p.swfContribRate / 100) * gdp * revenueFactor;
      const returns = swfBalance * (p.swfReturnRate / 100);
      const distribution = swfBalance * (p.swfSpendRule / 100);
      swfBalance = swfBalance + contrib + returns - distribution;
      swfDiv = distribution / NUM_HH;
    }

    // ── UBI ──
    let ubi = 0;
    if (p.enableUBI) {
      const ramp = Math.min(1, t / Math.max(1, p.ubiRampYears));
      ubi = p.ubiMonthly * 12 * 1.5 * ramp * revenueFactor;
    }

    // ── ESOP / CO-OP ──
    let esop = 0;
    if (p.enableESOP) {
      const ramp = Math.min(1, t / 5);
      esop = 800 * Math.pow(1 + p.esopGrowth / 100, t) * Math.pow(gdp / BASE_GDP, 0.3) * ramp;
      esop = Math.min(esop, 30000);
    }

    // ── BABY BONDS ──
    let babyBonds = 0;
    if (p.enableBabyBonds && t >= p.babyBondMaturity) {
      const yearsActive = t - p.babyBondMaturity;
      const maturedValue = p.babyBondSeed * Math.pow(1 + p.babyBondReturn / 100, p.babyBondMaturity);
      const cohortFraction = Math.min(1, yearsActive / 25);
      babyBonds = maturedValue * (p.babyBondReturn / 100) * cohortFraction;
    }

    // ── DATA / AI ROYALTY ──
    let dataRoyalty = 0;
    if (p.enableDataRoyalty) {
      const ramp = Math.min(1, t / 8);
      dataRoyalty = p.dataRoyaltyMax * automationLevel * Math.pow(gdp / BASE_GDP, 0.4) * revenueFactor * ramp;
    }

    // ── CARBON DIVIDEND ──
    let carbon = 0;
    if (p.enableCarbon) {
      const ramp = Math.min(1, t / 3);
      carbon = p.carbonBase * Math.pow(1 + p.carbonGrowth / 100, t) * ramp;
    }

    // ── PRIVATE INVESTMENT ──
    const privateInv = p.privateInvBase * Math.pow(1 + p.privateInvGrowth / 100, t) * Math.pow(gdp / BASE_GDP, 0.2);

    // ── L'VARIAN DELTA-C MECHANICS (Autopoietic System Alignment) ──
    let deltaC = 0;
    let currentKappa = 0;
    if (p.enableDeltaC) {
      // Compounded coherence baseline via selected tau rate
      const rawCoherence = LVG_GLOBAL_BASELINE * Math.pow(1 + (p.tauRate / 100), t);
      
      // Calculate Kappa Accumulator (Systemic friction strain from rapid automation)
      currentKappa = (autoFromBase * NUM_HH) / 187_000_000;
      let coherenceEfficiency = 1.0;
      
      // Degrade baseline efficiency if network strain crosses the soft threshold
      if (currentKappa > p.kappaThreshold) {
        coherenceEfficiency = Math.max(0.15, 1.0 - (currentKappa - p.kappaThreshold));
      }
      deltaC = rawCoherence * coherenceEfficiency;
    }

    // ── NOMINAL TOTAL ──
    const nominalTotal = wages + social + ubi + swfDiv + esop + babyBonds + dataRoyalty + carbon + privateInv + deltaC;

    // ── DEMONETIZATION ──
    let deMonet = 0;
    if (p.enableDemonet) {
      const costReduction = (p.demonetRate / 100) * autoFromBase;
      if (costReduction > 0 && costReduction < 1) {
        const ppMultiplier = 1 / (1 - costReduction);
        deMonet = nominalTotal * (ppMultiplier - 1);
      }
    }

    const effectiveTotal = nominalTotal + deMonet;

    data.push({
      year,
      wages: Math.round(wages),
      social: Math.round(social),
      ubi: Math.round(ubi),
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
      kappa: +currentKappa.toFixed(2),
    });
  }
  return data;
}

// ─── Slider component ───
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
          background: `linear-gradient(to right, #5B8DEF ${pct}%, #334155 ${pct}%)`,
          cursor: "pointer", outline: "none",
        }}
      />
    </div>
  );
}

// ─── Toggle component ───
function Toggle({ label, checked, onChange, color }) {
  return (
    <div
      onClick={onChange}
      role="button"
      tabIndex={0}
      onKeyDown={e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onChange(); } }}
      style={{
        display: "flex", alignItems: "center", gap: 8, cursor: "pointer",
        padding: "5px 0", fontSize: 12, color: checked ? "#e2e8f0" : "#64748b",
        transition: "color 0.2s", userSelect: "none",
      }}
    >
      <div style={{
        width: 34, height: 18, borderRadius: 9, position: "relative",
        background: checked ? (color || "#5B8DEF") : "#334155",
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

// ─── Section header ───
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

// ─── Custom tooltip ───
function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  const total = payload.reduce((s, p) => s + (p.value || 0), 0);
  const row = payload[0]?.payload || {};
  return (
    <div style={{
      background: "#0f172aee", border: "1px solid #1e293b", borderRadius: 8,
      padding: "12px 16px", fontSize: 11, color: "#e2e8f0", minWidth: 240,
      backdropFilter: "blur(8px)", zIndex: 50,
    }}>
      <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 6, color: "#f8fafc" }}>
        {label} — ${total.toLocaleString()}/yr
      </div>
      <div style={{ fontSize: 10, color: "#94a3b8", marginBottom: 8 }}>
        Automation: {row.automationLevel}% · GDP: ${row.gdpT}T {row.kappa > 0 && `· κ-Strain: ${row.kappa}`}
      </div>
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
  };

  return (
    <div style={{
      fontFamily: "'IBM Plex Sans', 'Segoe UI', system-ui, sans-serif",
      background: "#0a0f1a", color: "#e2e8f0", minHeight: "100vh", display: "flex", flexDirection: "column",
    }}>
      {/* Header */}
      <div style={{
        padding: "16px 24px", borderBottom: "1px solid #1e293b",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        background: "linear-gradient(180deg, #0f172a 0%, #0a0f1a 100%)",
      }}>
        <div>
          <h1 style={{
            margin: 0, fontSize: 18, fontWeight: 800, letterSpacing: -0.5,
            background: "linear-gradient(135deg, #5B8DEF, #00F5FF)",
            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
          }}>
            Universal High Income & Coherence Simulator
          </h1>
          <p style={{ margin: "2px 0 0", fontSize: 11, color: "#64748b" }}>
            Contrasting Extractive Policy Modules with Autopoietic Delta-C ($\delta^c$) Lattices
          </p>
        </div>
        <div style={{ display: "flex", gap: 6 }}>
          {[
            ["proactive", "Proactive"],
            ["reactive", "Reactive"],
            ["delayed", "Delayed"],
            ["noAction", "No Action"],
            ["deltaC", "Delta-C Phase"],
          ].map(([k, l]) => (
            <button key={k} onClick={() => applyPreset(k)} style={{
              padding: "5px 10px", fontSize: 10, fontWeight: 600, borderRadius: 4,
              border: "1px solid #334155", background: k === "deltaC" ? "#0f2d3a" : "#1e293b", 
              color: k === "deltaC" ? C.deltaC : "#94a3b8", cursor: "pointer", transition: "all 0.15s",
            }}>
              {l}
            </button>
          ))}
        </div>
      </div>

      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        {/* Control Panel */}
        <div style={{
          width: panelOpen ? 300 : 0, overflow: panelOpen ? "auto" : "hidden",
          transition: "width 0.3s", background: "#0f172a",
          borderRight: "1px solid #1e293b", flexShrink: 0,
          padding: panelOpen ? "16px" : 0,
        }}>
          {panelOpen && (
            <>
              <Section title="Delta-C Sovereign Lattice">
                <Toggle label="Enable Delta-C Framework" checked={params.enableDeltaC} onChange={() => set("enableDeltaC", !params.enableDeltaC)} color={C.deltaC} />
                <Slider label="τ-Expansion Factor" value={params.tauRate} onChange={v => set("tauRate", v)}
                  min={1.0} max={15.0} step={0.1} unit="%" disabled={!params.enableDeltaC} />
                <Slider label="κ-Strain Soft Threshold" value={params.kappaThreshold} onChange={v => set("kappaThreshold", v)}
                  min={0.4} max={0.9} step={0.05} disabled={!params.enableDeltaC} />
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

        {/* Toggle Button */}
        <div style={{ display: "flex", alignItems: "center", flexShrink: 0 }}>
          <button onClick={() => setPanelOpen(!panelOpen)} style={{
            width: 20, height: 44, borderRadius: "0 6px 6px 0", background: "#1e293b", border: "1px solid #334155", borderLeft: "none", color: "#64748b", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            {panelOpen ? "◂" : "▸"}
          </button>
        </div>

        {/* Chart Area */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", padding: "16px 24px 16px 32px", minWidth: 0 }}>
          {/* Key Metrics */}
          <div style={{ display: "flex", gap: 16, marginBottom: 16, flexWrap: "wrap" }}>
            {[
              { label: `${BASE_YEAR}`, value: fmtFull(firstRow?.total || 0), sub: "Starting Income", accent: "#94a3b8" },
              { label: `${midRow?.year}`, value: fmtFull(midRow?.total || 0), sub: `Mid · ${midRow?.automationLevel}% Auto`, accent: "#5B8DEF" },
              { label: `${lastRow?.year}`, value: fmtFull(lastRow?.total || 0), sub: `End State Income`, accent: params.enableDeltaC ? C.deltaC : "#2DD4A8" },
              { label: "Lattice Dynamic", value: params.enableDeltaC ? `κ: ${lastRow?.kappa}` : `$${lastRow?.swfT}T`, sub: params.enableDeltaC ? "Base Space Strain" : "SWF Asset Total", accent: "#F5A623" },
              { label: "vs. Today", value: `${Math.round(((lastRow?.total || 0) / BASE_MEDIAN) * 100)}%`, sub: `Baseline: ${fmtK(BASE_MEDIAN)}`, accent: "#C084FC" },
            ].map((m, i) => (
              <div key={i} style={{ background: "#0f172a", border: "1px solid #1e293b", borderRadius: 8, padding: "10px 16px", flex: "1 1 140px", minWidth: 120 }}>
                <div style={{ fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: 1, color: "#475569", marginBottom: 2 }}>{m.label}</div>
                <div style={{ fontSize: 20, fontWeight: 800, color: m.accent, fontFamily: "'JetBrains Mono', monospace", letterSpacing: -0.5 }}>{m.value}</div>
                <div style={{ fontSize: 10, color: "#64748b", marginTop: 1 }}>{m.sub}</div>
              </div>
            ))}
          </div>

          {/* Chart */}
          <div style={{ flex: 1, minHeight: 0 }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
                <defs>
                  {activeStreams.map(s => (
                    <linearGradient key={s.key} id={`g_${s.key}`} x1="0" y1="0" x2="0" y2="1">
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
                  <Area key={s.key} type="monotone" dataKey={s.key} stackId="1" stroke={s.color} fill={`url(#g_${s.key})`} strokeWidth={0.5} />
                ))}
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Legend */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px 16px", padding: "10px 0 4px", justifyContent: "center" }}>
            {activeStreams.map(s => (
              <div key={s.key} style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 10, color: "#94a3b8" }}>
                <div style={{ width: 10, height: 10, borderRadius: 2, background: s.color }} />
                {s.label}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
