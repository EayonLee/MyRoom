import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { RectAreaLightUniformsLib } from "three/addons/lights/RectAreaLightUniformsLib.js";

RectAreaLightUniformsLib.init();

/**
 * The GLB is exported Y-up, so Blender's (x, y, z) lands at (x, z, -y).
 * Every hand-placed position below is written in Blender metres and run
 * through this helper, which keeps the two files readable side by side.
 */
function bl(x: number, y: number, z: number): [number, number, number] {
  return [x, z, -y];
}

const canvas = document.getElementById("stage") as HTMLCanvasElement;
const statEl = document.getElementById("stat")!;
const viewHint = document.getElementById("view-hint")!;
const freeButton = document.getElementById("free-view") as HTMLButtonElement;

const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
  powerPreference: "high-performance",
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
// Keep the tungsten look subdued, with enough exposure left to read the empty shell.
renderer.toneMappingExposure = 0.92;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x07080a);
scene.fog = new THREE.FogExp2(0x07080a, 0.035);

const camera = new THREE.PerspectiveCamera(
  46,
  window.innerWidth / window.innerHeight,
  0.05,
  80,
);
camera.position.set(...bl(2.45, 2.40, 1.42));

const controls = new OrbitControls(camera, canvas);
controls.target.set(...bl(0.45, 2.40, 1.10));
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 0.35;
controls.maxDistance = 5.0;
controls.maxPolarAngle = Math.PI * 0.62;
controls.update();
controls.enabled = false;

// The same Blender-space convention as the room model. These are framing
// presets, not separate rooms; they can be adjusted as the layout evolves.
const views = {
  desk: { position: bl(2.45, 2.40, 1.42), target: bl(0.45, 2.40, 1.10) },
  computer: { position: bl(1.80, 2.05, 1.42), target: bl(1.05, 0.45, 1.05) },
  side: { position: bl(0.55, 1.10, 1.42), target: bl(0.95, 3.20, 1.05) },
} satisfies Record<string, { position: [number, number, number]; target: [number, number, number] }>;
type ViewName = keyof typeof views;
const viewButtons = Array.from(document.querySelectorAll<HTMLButtonElement>("[data-view]"));
let currentView: ViewName = "desk";
let freeView = false;
let transition: {
  fromPosition: THREE.Vector3;
  fromTarget: THREE.Vector3;
  toPosition: THREE.Vector3;
  toTarget: THREE.Vector3;
  elapsed: number;
  duration: number;
} | null = null;

function updateViewUI(): void {
  for (const button of viewButtons) {
    button.setAttribute("aria-pressed", String(!freeView && button.dataset.view === currentView));
  }
  freeButton.setAttribute("aria-pressed", String(freeView));
  document.body.classList.toggle("free-view", freeView);
  viewHint.textContent = freeView
    ? "拖动旋转 · 滚轮缩放 · Esc 返回主桌 · F 返回当前机位"
    : "选择机位 · Esc 返回主桌 · F 自由查看";
}

function selectView(name: ViewName): void {
  currentView = name;
  freeView = false;
  controls.enabled = false;
  controls.enableDamping = false;
  const preset = views[name];
  transition = {
    fromPosition: camera.position.clone(),
    fromTarget: controls.target.clone(),
    toPosition: new THREE.Vector3(...preset.position),
    toTarget: new THREE.Vector3(...preset.target),
    elapsed: 0,
    duration: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 0.8,
  };
  updateViewUI();
}

function toggleFreeView(): void {
  if (freeView) {
    selectView(currentView);
    return;
  }
  transition = null;
  freeView = true;
  controls.enableDamping = true;
  controls.enabled = true;
  updateViewUI();
}

for (const button of viewButtons) {
  button.addEventListener("click", () => {
    const name = button.dataset.view as ViewName;
    if (name in views) selectView(name);
  });
}
freeButton.addEventListener("click", toggleFreeView);
window.addEventListener("keydown", (event) => {
  if (event.repeat || event.altKey || event.ctrlKey || event.metaKey) return;
  const target = event.target;
  if (target instanceof HTMLElement && (target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName))) return;
  const key = event.key.toLowerCase();
  if (key === "1") selectView("desk");
  else if (key === "2") selectView("computer");
  else if (key === "3") selectView("side");
  else if (key === "escape") selectView("desk");
  else if (key === "f") toggleFreeView();
  else return;
  event.preventDefault();
});

/**
 * Stand-in lighting. The article's finish bakes four light channels into
 * texture atlases with Cycles; until that pipeline lands this keeps the shell
 * readable so geometry can be judged on its own.
 */
function studioLights(): void {
  // Warm tungsten key from the room's front-right, matching the reference's
  // low, amber pool of light instead of a bright neutral studio wash.
  const warmColor = new THREE.Color().setRGB(1.0, 0.58, 0.26);
  const warm = new THREE.SpotLight(warmColor, 22, 8, 0.72, 0.62, 1.6);
  warm.position.set(...bl(2.85, 0.80, 1.55));
  warm.target.position.set(...bl(2.40, 1.05, 0.75));
  warm.castShadow = true;
  warm.shadow.mapSize.set(2048, 2048);
  warm.shadow.bias = -0.0012;
  warm.shadow.normalBias = 0.02;
  scene.add(warm, warm.target);

  // RectArea intensity is luminance, unlike Blender's total power in watts.
  // Keep this night-window fill faint so tungsten remains the dominant light.
  const windowLight = new THREE.RectAreaLight(0x9fc0ff, 0.65, 1.65, 1.20);
  windowLight.position.set(...bl(-0.30, 2.40, 1.645));
  windowLight.lookAt(...bl(3.60, 2.70, 0.85));
  scene.add(windowLight);

  // A small amber bounce keeps the plaster readable without lifting the shadows.
  const bounce = new THREE.PointLight(0xffa35c, 1.35, 3.6, 2.0);
  bounce.position.set(...bl(1.30, 1.60, 1.25));
  scene.add(bounce);

  // Broad, dim reflected tungsten light replaces the indirect illumination
  // that Cycles computes for the offline render.
  const reflectedWarm = new THREE.RectAreaLight(warmColor, 0.85, 2.8, 2.0);
  reflectedWarm.position.set(...bl(2.75, 1.20, 1.80));
  reflectedWarm.lookAt(...bl(0.65, 3.50, 1.0));
  scene.add(reflectedWarm);

  scene.add(new THREE.HemisphereLight(0x252a35, 0x100a06, 0.20));
}

studioLights();

let tris = 0;
const loader = new GLTFLoader();
loader.load(
  "/assets/room.glb",
  (gltf) => {
    const root = gltf.scene;
    root.traverse((obj) => {
      const mesh = obj as THREE.Mesh;
      if (!mesh.isMesh) return;
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      const geom = mesh.geometry as THREE.BufferGeometry;
      const count = geom.index ? geom.index.count / 3 : geom.attributes.position.count / 3;
      tris += count;
    });
    scene.add(root);
    statEl.textContent = `${Math.round(tris).toLocaleString()} tris`;
  },
  undefined,
  (err) => {
    console.error(err);
    statEl.textContent = "glb failed";
  },
);

const clock = new THREE.Clock();
let frames = 0;
let acc = 0;
let fps = 0;

function loop(): void {
  requestAnimationFrame(loop);
  const dt = clock.getDelta();
  if (transition) {
    transition.elapsed += dt;
    const t = transition.duration === 0 ? 1 : Math.min(transition.elapsed / transition.duration, 1);
    const eased = t * t * (3 - 2 * t);
    camera.position.lerpVectors(transition.fromPosition, transition.toPosition, eased);
    controls.target.lerpVectors(transition.fromTarget, transition.toTarget, eased);
    if (t === 1) transition = null;
  }
  acc += dt;
  frames += 1;
  if (acc >= 0.5) {
    fps = Math.round(frames / acc);
    frames = 0;
    acc = 0;
    if (tris > 0) {
      statEl.textContent = `${Math.round(tris).toLocaleString()} tris · ${fps} fps`;
    }
  }
  controls.update();
  renderer.render(scene, camera);
}
loop();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
