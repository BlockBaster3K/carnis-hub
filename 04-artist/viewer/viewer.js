import * as THREE from 'three';
import { OrbitControls } from './OrbitControls.js';

const DEG = THREE.MathUtils.degToRad;
const app = document.getElementById('app');

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x14121a);
scene.fog = new THREE.Fog(0x14121a, 90, 190);

const camera = new THREE.PerspectiveCamera(45, innerWidth / innerHeight, 0.1, 500);
const CAM_HOME = new THREE.Vector3(27, 30, -48);
camera.position.copy(CAM_HOME);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
app.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 18, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.autoRotate = true;
controls.autoRotateSpeed = 1.1;
controls.minDistance = 18;
controls.maxDistance = 140;
controls.maxPolarAngle = Math.PI * 0.52;

// свет
scene.add(new THREE.AmbientLight(0x9a8a90, 0.6));
const key = new THREE.DirectionalLight(0xffe8e0, 1.15); key.position.set(24, 44, -28); scene.add(key);
const rim = new THREE.DirectionalLight(0x7a8aff, 0.4); rim.position.set(-28, 22, 32); scene.add(rim);
const brainLight = new THREE.PointLight(0xff5c39, 2.2, 55, 1.8); brainLight.position.set(0, 32, -5); scene.add(brainLight);

// пол и сетка
const ground = new THREE.Mesh(
  new THREE.CircleGeometry(34, 64),
  new THREE.MeshStandardMaterial({ color: 0x1c1822, roughness: 1, metalness: 0 }));
ground.rotation.x = -Math.PI / 2; ground.position.y = -0.06; scene.add(ground);
const grid = new THREE.GridHelper(68, 34, 0x4a3a4a, 0x2a2430);
grid.position.y = 0.0; scene.add(grid);

// текстуры
const tl = new THREE.TextureLoader();
function pixelTex(url) {
  const t = tl.load(url);
  t.magFilter = THREE.NearestFilter;
  t.minFilter = THREE.NearestFilter;
  t.generateMipmaps = false;
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
const tex = pixelTex('../textures/cerebral_nexus.png');
const glowTex = pixelTex('../textures/cerebral_nexus_glowmask.png');

const mat = new THREE.MeshStandardMaterial({
  map: tex, emissiveMap: glowTex, emissive: new THREE.Color(0xffffff),
  emissiveIntensity: 1.5, roughness: 0.82, metalness: 0.0,
});

const FACE_ORDER = ['east', 'west', 'up', 'down', 'south', 'north']; // +x,-x,+y,-y,+z,-z

function makeCube(c, pivot, W, H) {
  const [w, h, d] = c.size;
  const geo = new THREE.BoxGeometry(w, h, d);
  const uv = geo.attributes.uv;
  for (let fi = 0; fi < 6; fi++) {
    const r = c.uv[FACE_ORDER[fi]];
    if (!r) continue;
    const [ru, rv] = r.uv, [rw, rh] = r.uv_size;
    for (let vi = 0; vi < 4; vi++) {
      const idx = fi * 4 + vi;
      const u0 = uv.getX(idx), v0 = uv.getY(idx);
      uv.setXY(idx, (ru + u0 * rw) / W, 1 - (rv + (1 - v0) * rh) / H);
    }
  }
  uv.needsUpdate = true;
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set(c.origin[0] + w / 2 - pivot[0], c.origin[1] + h / 2 - pivot[1], c.origin[2] + d / 2 - pivot[2]);
  return mesh;
}

const boneMap = {};
let clips = {};
let root = new THREE.Group();
scene.add(root);

async function build() {
  const geo = await (await fetch('../models/cerebral_nexus.geo.json')).json();
  const anim = await (await fetch('../animations/cerebral_nexus.animation.json')).json();
  clips = anim.animations;
  const g = geo['minecraft:geometry'][0];
  const W = g.description.texture_width, H = g.description.texture_height;

  for (const b of g.bones) {
    const grp = new THREE.Group(); grp.name = b.name;
    boneMap[b.name] = { group: grp, pivot: b.pivot || [0, 0, 0], rot: b.rotation || [0, 0, 0], parent: b.parent };
  }
  for (const b of g.bones) {
    const info = boneMap[b.name];
    const pp = b.parent ? boneMap[b.parent].pivot : [0, 0, 0];
    info.group.position.set(info.pivot[0] - pp[0], info.pivot[1] - pp[1], info.pivot[2] - pp[2]);
    info.basePos = info.group.position.clone();
    info.group.rotation.set(DEG(info.rot[0]), DEG(info.rot[1]), DEG(info.rot[2]), 'XYZ');
    if (b.parent) boneMap[b.parent].group.add(info.group); else root.add(info.group);
  }
  for (const b of g.bones) {
    const info = boneMap[b.name];
    for (const c of (b.cubes || [])) info.group.add(makeCube(c, info.pivot, W, H));
  }
  document.getElementById('loading').style.display = 'none';
}

// ── анимации ──
function sample(kf, t) {
  const keys = Object.keys(kf).map(Number).sort((a, b) => a - b);
  if (t <= keys[0]) return kf[keys[0].toFixed(2)];
  if (t >= keys[keys.length - 1]) return kf[keys[keys.length - 1].toFixed(2)];
  for (let i = 0; i < keys.length - 1; i++) {
    const a = keys[i], b = keys[i + 1];
    if (a <= t && t <= b) {
      const f = b > a ? (t - a) / (b - a) : 0;
      const va = kf[a.toFixed(2)], vb = kf[b.toFixed(2)];
      return va.map((x, j) => x + (vb[j] - x) * f);
    }
  }
  return kf[keys[keys.length - 1].toFixed(2)];
}

let current = 'animation.cerebral_nexus.idle';
let animTime = 0, playing = true, glowOn = true;

function resetBones() {
  for (const k in boneMap) {
    const info = boneMap[k];
    info.group.rotation.set(DEG(info.rot[0]), DEG(info.rot[1]), DEG(info.rot[2]), 'XYZ');
    info.group.scale.set(1, 1, 1);
    info.group.position.copy(info.basePos);
  }
}

function applyPose(name, t) {
  const clip = clips[name]; if (!clip) return;
  const L = clip.animation_length;
  const tt = clip.loop ? (t % L) : Math.min(t, L);
  resetBones();
  for (const bn in clip.bones) {
    const info = boneMap[bn]; if (!info) continue;
    const ch = clip.bones[bn];
    if (ch.rotation) {
      const v = sample(ch.rotation, tt);
      info.group.rotation.set(DEG(info.rot[0] + v[0]), DEG(info.rot[1] + v[1]), DEG(info.rot[2] + v[2]), 'XYZ');
    }
    if (ch.scale) { const v = sample(ch.scale, tt); info.group.scale.set(v[0], v[1], v[2]); }
    if (ch.position) { const v = sample(ch.position, tt); info.group.position.set(info.basePos.x + v[0], info.basePos.y + v[1], info.basePos.z + v[2]); }
  }
  return { tt, L, loop: !!clip.loop };
}

function setClip(name) {
  current = name; animTime = 0; playing = true;
  document.getElementById('clip-name').textContent = name.split('.').pop();
  for (const id of ['idle', 'pulse', 'death']) document.getElementById('btn-' + id).classList.remove('active');
  const map = { 'animation.cerebral_nexus.idle': 'idle', 'animation.cerebral_nexus.psychic_pulse': 'pulse', 'animation.cerebral_nexus.death': 'death' };
  document.getElementById('btn-' + map[name]).classList.add('active');
}

// ── UI ──
document.getElementById('btn-idle').onclick = () => setClip('animation.cerebral_nexus.idle');
document.getElementById('btn-pulse').onclick = () => setClip('animation.cerebral_nexus.psychic_pulse');
document.getElementById('btn-death').onclick = () => setClip('animation.cerebral_nexus.death');
document.getElementById('btn-glow').onclick = (e) => {
  glowOn = !glowOn; e.target.classList.toggle('active', glowOn);
  mat.emissiveIntensity = glowOn ? 1.5 : 0;
};
document.getElementById('btn-rotate').onclick = (e) => {
  controls.autoRotate = !controls.autoRotate; e.target.classList.toggle('active', controls.autoRotate);
};
document.getElementById('btn-wire').onclick = (e) => {
  mat.wireframe = !mat.wireframe; e.target.classList.toggle('active', mat.wireframe);
};
document.getElementById('btn-reset').onclick = () => {
  camera.position.copy(CAM_HOME); controls.target.set(0, 18, 0);
};
addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

// ── цикл ──
const clock = new THREE.Clock();
function tick() {
  requestAnimationFrame(tick);
  const dt = Math.min(clock.getDelta(), 0.05);
  if (playing) animTime += dt;
  const st = applyPose(current, animTime);
  if (st && !st.loop && st.tt >= st.L) {
    if (current.endsWith('psychic_pulse')) setClip('animation.cerebral_nexus.idle');
    else playing = false; // death — удержать финальную позу
  }
  if (st) document.getElementById('clip-time').textContent = st.tt.toFixed(2) + 's';
  // атмосферный пульс света в ритме idle
  const pulse = 0.5 + 0.5 * Math.sin(animTime * (2 * Math.PI / 1.5));
  brainLight.intensity = glowOn ? (1.6 + 1.4 * pulse) : 0;
  controls.update();
  renderer.render(scene, camera);
}

build().then(() => tick()).catch(err => {
  document.getElementById('loading').textContent = 'ОШИБКА: ' + err.message;
  console.error(err);
});
