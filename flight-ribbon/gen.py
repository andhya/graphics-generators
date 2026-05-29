#!/usr/bin/env python3
"""Generate flight-ribbon/index.html — 3D pipe viz of REDARROW flight trace."""
import json, math

with open('/home/frank/graphics-generators/flight-ribbon/trace_43c453.json') as f:
    raw = json.load(f)

pts = []
for pt in raw['trace']:
    lat, lon = pt[1], pt[2]
    if lat is None or lon is None:
        continue
    alt   = 0   if pt[3] == 'ground' else (pt[3] if isinstance(pt[3], (int, float)) else 0)
    speed = round(pt[4], 1) if isinstance(pt[4], (int, float)) else 0
    flags = pt[6] if pt[6] is not None else 0
    pts.append([round(lat, 6), round(lon, 6), int(alt), speed, flags])

# Coordinate system: 1 unit = 100 m, 1:1 vertical scale (no exaggeration)
# X = east, Y = altitude (up), Z = -north  (right-hand Y-up)
center_lat = sum(p[0] for p in pts) / len(pts)
center_lon = sum(p[1] for p in pts) / len(pts)
M = 111320.0
cos_lat = math.cos(math.radians(center_lat))
SCALE = 1.0 / 100.0   # 1 scene-unit = 100 m

# Camera targets the Exeter/Paignton midpoint
def to_scene_xz(lat, lon):
    x = (lon - center_lon) * M * cos_lat * SCALE
    z = -(lat - center_lat) * M * SCALE
    return x, z

ex_x, ex_z = to_scene_xz(50.734, -3.413)   # Exeter Airport
pa_x, pa_z = to_scene_xz(50.440, -3.560)   # Paignton
cam_tx = (ex_x + pa_x) / 2
cam_tz = (ex_z + pa_z) / 2

pts_js = json.dumps(pts, separators=(',', ':'))

# ── Tube radius: 45 m = 0.45 units ──────────────────────────────────────────
TUBE_R = 45 * SCALE   # 0.45

# ── Read and patch library files for inline embedding ───────────────────────
import re, pathlib
HERE = pathlib.Path('/home/frank/graphics-generators/flight-ribbon')

three_src = (HERE / 'three.min.js').read_text()

oc_src = (HERE / 'OrbitControls.js').read_text()
# Replace ESM import with THREE.* aliases
oc_imports = ['EventDispatcher','MOUSE','Quaternion','Spherical','TOUCH',
               'Vector2','Vector3','Plane','Ray','MathUtils']
oc_src = re.sub(r"import \{[^}]+\} from 'three';", '', oc_src, flags=re.DOTALL)
oc_src = (''.join(f'const {n} = THREE.{n};\n' for n in oc_imports)
          + oc_src.replace('export { OrbitControls };',
                           'window.OrbitControls = OrbitControls;'))

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>3D Pipe — XX319 REDARROW · Exeter / Paignton</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#04080f;overflow:hidden}}
#hud{{
  position:fixed;top:20px;left:20px;
  color:#7aa8c8;font:13px/1.8 'SF Mono',Consolas,monospace;
  background:rgba(4,8,15,.82);padding:14px 18px;border-radius:6px;
  border:1px solid rgba(80,140,200,.18);pointer-events:none;
}}
#hud strong{{color:#d8eeff;font-size:15px;letter-spacing:.03em}}
#hud .dim{{color:#2a4055}}
#legend{{
  position:fixed;bottom:22px;left:50%;transform:translateX(-50%);
  display:flex;align-items:center;gap:10px;
  color:#5a8aaa;font:11px 'SF Mono',Consolas,monospace;pointer-events:none;
}}
#grad{{width:180px;height:10px;border-radius:2px;
  background:linear-gradient(to right,#87cfff,#ffffff,#ff1212)}}
</style>
</head>
<body>
<div id="hud">
  <strong>XX319</strong>&nbsp;·&nbsp;43C453<br>
  British Aerospace Hawk T.1<br>
  REDARROW&nbsp;·&nbsp;Royal Air Force<br>
  <span class="dim">────────────────────</span><br>
  {len(pts)} pts · 3 legs · 90 m ⌀ pipe<br>
  1:1 scale · CatmullRom · speed colour<br>
  <span class="dim">drag · scroll · right-drag pan</span>
</div>
<div id="legend">
  <span>0 kt</span><div id="grad"></div><span>600 kt</span>
</div>

<script>{three_src}</script>
<script>{oc_src}</script>
<script>
// ── embedded trace: [lat, lon, alt_ft, speed_kts, flags] ────────────────────
const RAW = {pts_js};

// ── coordinate projection (1 unit = 100 m, 1:1 scale) ───────────────────────
const CX = {center_lat}, CY = {center_lon};
const M  = 111320, CLAT = Math.cos(CX * Math.PI / 180);
const S  = {SCALE};           // units per metre

function proj(lat, lon, altFt) {{
  return new THREE.Vector3(
    (lon - CY) * M * CLAT * S,
    Math.max(altFt, 0) * 0.3048 * S,
   -(lat - CX) * M * S
  );
}}

// ── colour ramp by speed ─────────────────────────────────────────────────────
// 0 kt → sky blue, 300 kt → white, 600 kt → red
const SPD_MIN = 0, SPD_MAX = 600;
const RAMP = [
  [0.00, 0.53, 0.81, 1.00],   //   0 kt  sky blue
  [0.50, 1.00, 1.00, 1.00],   // 300 kt  white
  [1.00, 1.00, 0.07, 0.07],   // 600 kt  red
];
function spdRGB(spd) {{
  const t = Math.max(0, Math.min(1, (spd - SPD_MIN) / (SPD_MAX - SPD_MIN)));
  for (let i = 0; i < RAMP.length - 1; i++) {{
    if (t <= RAMP[i+1][0]) {{
      const u = (t - RAMP[i][0]) / (RAMP[i+1][0] - RAMP[i][0]);
      return [
        RAMP[i][1] + (RAMP[i+1][1] - RAMP[i][1]) * u,
        RAMP[i][2] + (RAMP[i+1][2] - RAMP[i][2]) * u,
        RAMP[i][3] + (RAMP[i+1][3] - RAMP[i][3]) * u,
      ];
    }}
  }}
  return [1, 0.15, 0];
}}

// ── split into legs on flag bit 1 (leg_start) ───────────────────────────────
const legs = [];
let cur = [];
for (const p of RAW) {{
  if ((p[4] & 2) && cur.length) {{ legs.push(cur); cur = []; }}
  cur.push(p);
}}
if (cur.length) legs.push(cur);

// ── build tube geometry for one leg ─────────────────────────────────────────
const TUBE_R = {TUBE_R:.4f};     // 45 m in scene units
const RADIAL  = 16;              // sides around the pipe

function buildTube(leg) {{
  // Project raw points; keep parallel speed array for colour interpolation
  const ctrlPts   = leg.map(p => proj(p[0], p[1], p[2]));
  const ctrlSpeeds = leg.map(p => p[3]);   // speed_kts at each control point

  // Smooth via CatmullRom spline
  const curve = new THREE.CatmullRomCurve3(ctrlPts, false, 'catmullrom', 0.5);
  const SEG = ctrlPts.length * 8;   // 8× upsampling for smoothness
  const sampled = curve.getPoints(SEG);  // SEG+1 points

  // Linearly interpolate speed at each sample using control-point spacing
  const K = ctrlSpeeds.length;
  const sampledSpeed = sampled.map((_, i) => {{
    const idx = (i / SEG) * (K - 1);
    const i0 = Math.floor(idx), i1 = Math.min(K - 1, i0 + 1);
    return ctrlSpeeds[i0] + (ctrlSpeeds[i1] - ctrlSpeeds[i0]) * (idx - i0);
  }});

  // Stable "parallel-transport" frames — avoids Frenet singularities
  // on the nearly-flat flight-path geometry
  const UP = new THREE.Vector3(0, 1, 0);
  const frames = sampled.map((p, i) => {{
    const prev = sampled[Math.max(0, i - 1)];
    const next = sampled[Math.min(SEG, i + 1)];
    const T = new THREE.Vector3().subVectors(next, prev);
    if (T.lengthSq() < 1e-12) T.set(1, 0, 0);
    T.normalize();
    // right = T × UP  (pointing right in horizontal plane)
    const R = new THREE.Vector3().crossVectors(T, UP);
    if (R.lengthSq() < 1e-12) R.set(1, 0, 0);
    R.normalize();
    // "up" of frame = R × T
    const N = new THREE.Vector3().crossVectors(R, T).normalize();
    return {{R, N}};
  }});

  // Build BufferGeometry with vertex colours
  const nVerts = (SEG + 1) * RADIAL;
  const positions = new Float32Array(nVerts * 3);
  const colors    = new Float32Array(nVerts * 3);
  const indices   = [];
  const PI2 = Math.PI * 2;

  for (let i = 0; i <= SEG; i++) {{
    const p  = sampled[i];
    const {{R, N}} = frames[i];
    const [r, g, b] = spdRGB(sampledSpeed[i]);
    const base = i * RADIAL;
    for (let j = 0; j < RADIAL; j++) {{
      const theta = (j / RADIAL) * PI2;
      const c = Math.cos(theta), s = Math.sin(theta);
      const vi = (base + j) * 3;
      positions[vi]   = p.x + TUBE_R * (c * R.x + s * N.x);
      positions[vi+1] = p.y + TUBE_R * (c * R.y + s * N.y);
      positions[vi+2] = p.z + TUBE_R * (c * R.z + s * N.z);
      colors[vi]   = r;
      colors[vi+1] = g;
      colors[vi+2] = b;
    }}
    if (i < SEG) {{
      for (let j = 0; j < RADIAL; j++) {{
        const a = base + j,              b2 = base + (j+1) % RADIAL;
        const c = base + RADIAL + j,    d  = base + RADIAL + (j+1) % RADIAL;
        indices.push(a, b2, d,  a, d, c);
      }}
    }}
  }}

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geo.setAttribute('color',    new THREE.Float32BufferAttribute(colors, 3));
  geo.setIndex(indices);
  geo.computeVertexNormals();
  return new THREE.Mesh(geo, new THREE.MeshPhongMaterial({{
    vertexColors: true,
    shininess: 60,
    specular: new THREE.Color(0x334455),
  }}));
}}

// ── scene setup ──────────────────────────────────────────────────────────────
const renderer = new THREE.WebGLRenderer({{antialias: true}});
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = false;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x04080f);
scene.fog = new THREE.FogExp2(0x04080f, 0.00025);

// Lights
scene.add(new THREE.AmbientLight(0x223344, 1.8));
const sun = new THREE.DirectionalLight(0xffffff, 2.2);
sun.position.set(300, 800, -400);
scene.add(sun);
const fill = new THREE.DirectionalLight(0x4488aa, 0.8);
fill.position.set(-500, 200, 600);
scene.add(fill);

// Ground grid (at y = 0)
const grid = new THREE.GridHelper(4000, 60, 0x0a1e30, 0x071525);
grid.position.set({(ex_x+pa_x)/2:.1f}, 0, {(ex_z+pa_z)/2:.1f});
scene.add(grid);

// Add all legs
for (const leg of legs) scene.add(buildTube(leg));

// ── camera: start looking at Exeter/Paignton from the south-east ─────────────
const TARGET = new THREE.Vector3({cam_tx:.1f}, 5, {cam_tz:.1f});
const camera = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 0.1, 15000);
camera.position.set(
  TARGET.x + 180,   // east
  120,              // elevated (~12 km, exaggerated view of the terrain)
  TARGET.z + 280    // south
);

const controls = new window.OrbitControls(camera, renderer.domElement);
controls.target.copy(TARGET);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 1;
controls.maxDistance = 6000;
controls.update();
window.__camera = camera;
window.__controls = controls;

window.addEventListener('resize', () => {{
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}});

(function loop() {{
  requestAnimationFrame(loop);
  controls.update();
  renderer.render(scene, camera);
}})();
</script>
</body>
</html>
"""

out = '/home/frank/graphics-generators/flight-ribbon/index.html'
with open(out, 'w') as f:
    f.write(HTML)
print(f"Written {len(HTML):,} chars → {out}")
print(f"Tube radius: {TUBE_R:.4f} units = 45 m")
print(f"Camera target: ({cam_tx:.1f}, {cam_tz:.1f})")
