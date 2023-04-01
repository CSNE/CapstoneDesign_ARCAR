// Import Three.js and plugins
import * as THREE from "https://cdn.skypack.dev/three@0.132.2";
import { OrbitControls } from "https://cdn.skypack.dev/three@0.132.2/examples/jsm/controls/OrbitControls.js";




const scene = new THREE.Scene();


// Lights
const alight = new THREE.AmbientLight(0xFFFFFF, 0.5);
scene.add(alight);

const dlight = new THREE.DirectionalLight(0xFFFFFF, 1);
dlight.position.set(10, 10, 0);
dlight.target.position.set(-5, 0, 0);
scene.add(dlight);
scene.add(dlight.target);

// Base Lines
const baseline_thickness=0.02;
const baselineX_width=20;
const baselineX_spacing=5;
const baselineX_num=10;
const baselineZ_length=baselineX_spacing*baselineX_num;

const lineGeom = new THREE.BoxGeometry(16,baseline_thickness,baseline_thickness);
const lineMat= new THREE.MeshBasicMaterial();
lineMat.color.setRGB(1,1,0);
for (var i=0;i<(baselineX_num+1);i++){
	var baseLine = new THREE.Mesh(lineGeom,lineMat);
	baseLine.position.z=-i*baselineX_spacing;
	scene.add(baseLine);
}
const lineGeomZ = new THREE.BoxGeometry(baseline_thickness,baseline_thickness,baselineZ_length);
var baseLineZ = new THREE.Mesh(lineGeomZ,lineMat);
baseLineZ.position.z=-baselineZ_length/2;
scene.add(baseLineZ);

// Origin cube (represents viewer/camera)
const viewerGeometry = new THREE.BoxGeometry( 0.5, 0.5, 0.5 );
const viewerMat= new THREE.MeshPhongMaterial()
viewerMat.color.setRGB(1,0.5,0)
const viewerBox = new THREE.Mesh(viewerGeometry,viewerMat)
scene.add(viewerBox);



// Renderer
const w=720;
const h=405;
const renderer = new THREE.WebGLRenderer( { antialias: true, canvas:cvs} );
renderer.setSize(w,h);
renderer.setAnimationLoop( animation );

// Camera controls
const camera = new THREE.PerspectiveCamera( 70, w/h, 0.01, 1000 );
const controls = new OrbitControls( camera, renderer.domElement );
camera.position.set( 0, 3, 10 );
controls.update();

// Anim Loop
function animation( time ) {
	controls.update();
	renderer.render( scene, camera );
}

// Function for creating objects from the python server
const loader = new THREE.TextureLoader();
var object_meshes=[];
function setObjects(objs){
	// Remove all objects first
	for (var i=0;i<object_meshes.length;i++){
		scene.remove(object_meshes[i])
	}
	object_meshes=[];
	
	// Add objects
	for (var i=0;i<objs.length;i++){
		var obj=objs[i];
		
		const objGeom = new THREE.PlaneGeometry(obj["sizeX"], obj["sizeY"]);
		
		const objMat= new THREE.MeshBasicMaterial();
		objMat.side=THREE.DoubleSide;
		objMat.color.setRGB(1,1,1);
		objMat.map=loader.load(obj["texture"]);
		
		const objMesh = new THREE.Mesh(objGeom,objMat)
		objMesh.position.x=obj["coordX"];
		objMesh.position.y=obj["coordY"];
		objMesh.position.z=-obj["coordZ"];
		
		scene.add(objMesh);
		object_meshes.push(objMesh)
	}
	
}

// Periodically fetch objects from python server
function getObjData(){
	var xhr=new XMLHttpRequest();
	xhr.open("GET","/objects");
	xhr.addEventListener("load",function(e){
		if (xhr.status==200){
			var objson=JSON.parse(xhr.responseText);
			
			setObjects(objson);
		}
	});
	xhr.addEventListener("error",function(e){
		console.log("Request errored.");
	});
	xhr.send();
}
setInterval(getObjData,200);
