// Import Three.js and plugins
import * as THREE from "https://cdn.skypack.dev/three@0.132.2";
import { OrbitControls } from "https://cdn.skypack.dev/three@0.132.2/examples/jsm/controls/OrbitControls.js";


function setupPointCloudRenderer(canvasDOM,jsonPath,updateInterval){
	

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
const baseline_thickness=0.01;
const baselineX_width=10;
const baselineX_spacing=1;
const baselineX_num=20;
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


// Renderer
const w=480;
const h=270;
const renderer = new THREE.WebGLRenderer( { antialias: true, canvas:canvasDOM} );
renderer.setSize(w,h);
renderer.setAnimationLoop( animation );

// Camera controls
const camera = new THREE.PerspectiveCamera( 60, w/h, 0.001, 1000 );
const controls = new OrbitControls( camera, renderer.domElement );
camera.position.set( 0, 1, 3 );
controls.update();

// Anim Loop
function animation( time ) {
	controls.update();
	renderer.render( scene, camera );
}
/*
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
		
		const objMesh = new THREE.Mesh(objGeom,objMat);
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
		//console.log("Request errored.");
	});
	xhr.send();
}*/

var object_points=[];
var pointCubeSize=0.10;
function setPointCloud(pointList){
	for (var i=0;i<object_points.length;i++){
		scene.remove(object_points[i])
	}
	object_points=[];
	//console.log(pointList);
	// Add objects
	for (var i=0;i<pointList.length;i++){
		var pnt=pointList[i];

		//console.log(pnt);

		const objGeom = new THREE.BoxGeometry(pointCubeSize,pointCubeSize,pointCubeSize);

		const objMat= new THREE.MeshBasicMaterial();
		//objMat.side=THREE.DoubleSide;
		const objMesh = new THREE.Mesh(objGeom,objMat);
		objMat.color.setRGB(pnt["r"],pnt["g"],pnt["b"]);
		objMesh.position.x=pnt["x"];
		objMesh.position.y=-pnt["y"];
		objMesh.position.z=-pnt["z"];

		scene.add(objMesh);
		object_points.push(objMesh)
	}

}

// Periodically fetch objects from python server
function getPointData(){
	var xhr=new XMLHttpRequest();
	xhr.open("GET",jsonPath);
	xhr.addEventListener("load",function(e){
		if (xhr.status==200){
			var objson=JSON.parse(xhr.responseText);
			
			setPointCloud(objson);
		}
	});
	xhr.addEventListener("error",function(e){
		console.log("Request errored.");
	});
	xhr.send();
}

//setInterval(getObjData,200);
setInterval(getPointData,updateInterval);

}

setupPointCloudRenderer(pc_monodepth,"/pc_monodepth.json",5000);
setupPointCloudRenderer(pc_opencv,"/pc_opencv.json",5000);
setupPointCloudRenderer(pc_psmnet,"/pc_psmnet.json",5000);
