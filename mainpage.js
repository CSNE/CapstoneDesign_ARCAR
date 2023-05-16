// Imports
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';
import { FontLoader } from 'three/addons/loaders/FontLoader.js';

const scene = new THREE.Scene();

// Lights
const alight = new THREE.AmbientLight(0xFFFFFF, 0.5);
scene.add(alight);


// Renderer
const w=480;
const h=270;
const renderer = new THREE.WebGLRenderer( { antialias: true, canvas:ar_canvas} );
//renderer.setSize(w,h);
renderer.setAnimationLoop( animation );

// Fullscreen canvas
window.addEventListener('resize', makeCanvasFull);
window.addEventListener('load', makeCanvasFull);

function makeCanvasFull(){
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize( window.innerWidth, window.innerHeight );
}

// Camera controls
const camera = new THREE.PerspectiveCamera( 60, w/h, 0.001, 1000 );
const controls = new OrbitControls( camera, renderer.domElement );
controls.target=new THREE.Vector3( 0, 0, -3 );
camera.position.set( 0, 0, 0 );
controls.update();

// Anim Loop
function animation( time ) {
    controls.update();
    renderer.render( scene, camera );
}



function request(location,succ,fail){
    var xhr=new XMLHttpRequest();
    xhr.open("GET",location);
    xhr.addEventListener("load",function(e){
        if (xhr.status==200) succ(xhr.responseText);
        else fail(xhr.status);
    });
    xhr.addEventListener("error",function(e){
        fail(e);
    });
    xhr.send();
}

// Display: SegDepth
const tloader = new THREE.TextureLoader();
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
        objMat.map=tloader.load(obj["texture"]);

        const objMesh = new THREE.Mesh(objGeom,objMat);
        objMesh.position.x=obj["coordX"];
        objMesh.position.y=obj["coordY"];
        objMesh.position.z=-obj["coordZ"];

        scene.add(objMesh);
        object_meshes.push(objMesh);
    }

}

// Periodically fetch objects from python server
function getObjData(){
    request(
        "/objects",
        function(resp){setObjects(JSON.parse(resp));},
        function(){})
}


// Display: Seg3D
function buildWireMesh(pointlist){
    const geometry = new THREE.BufferGeometry();

    let positions=[];
    for (var i in pointlist){
        var pt=pointlist[i];
        positions.push(pt[0]);
        positions.push(pt[1]);
        positions.push(pt[2]);
        //console.log(pt);
    }
    const vertices = new Float32Array(positions);
    //console.log(vertices);

    // itemSize = 3 because there are 3 values (components) per vertex
    geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
    //const material = new THREE.MeshBasicMaterial( { color: 0xff0000 } );
    //const mesh = new THREE.Mesh( geometry, material );
    geometry.computeBoundingSphere();
    //const wireframe = new THREE.WireframeGeometry( geometry );

    //const line = new THREE.LineSegments( wireframe );
    //line.material.depthTest = false;
    //line.material.opacity = 0.25;
    //line.material.transparent = true;

    const material = new THREE.LineBasicMaterial();
    material.linewidth=10;
    material.color=new THREE.Color(1,0,0);
    var line = new THREE.Line( geometry, material );

    return line;
}

var wire_meshes=[];
function setSeg3D(s3d){
    // Remove all objects first
    for (var i=0;i<wire_meshes.length;i++){
        scene.remove(wire_meshes[i])
    }
    wire_meshes=[];

    for (var i in s3d){
        let name = s3d[i]["name"];
        let pointlist= s3d[i]["pointlist"];
        let wm=buildWireMesh(pointlist);
        scene.add(wm);
        wire_meshes.push(wm);
    }
}

function updateSeg3D(){
    request(
        "seg3d",
        function(resp){setSeg3D(JSON.parse(resp));},
        function(){});
}


// Display: Point Cloud

var object_points=[];
var pointCubeSize=0.03;
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
        objMesh.position.y=pnt["y"];
        objMesh.position.z=pnt["z"];

        scene.add(objMesh);
        object_points.push(objMesh);
    }
}

function updatePC(){
    request(
        "pointcloud",
        function(resp){setPointCloud(JSON.parse(resp));},
        function(){});
}


// Display: Texts
const floader = new FontLoader();

var object_texts=[];
function setTexts(textList){
    for (var i=0;i<object_texts.length;i++){
        scene.remove(object_texts[i])
    }
    object_texts=[];

    for (var i=0;i<textList.length;i++){
        let tContent=textList[i]["text"];
        let tSize=textList[i]["size"];
        let x=textList[i]["x"];
        let y=textList[i]["y"];
        let z=textList[i]["z"];

        floader.load( 'font.typeface.json', function ( font ) {

            const textGeom = new TextGeometry( tContent, {
                font: font,
                size: tSize, //80,
                height: tSize/10, //5,
                curveSegments: 12,
                //bevelEnabled: true,
                //bevelThickness: 10,
                //bevelSize: 8,
                //bevelOffset: 0,
                //bevelSegments: 5
            } );
            
            textGeom.computeBoundingBox();
            //textGeom.translate(-textGeom.boundingBox.max.x/2,0,0);
            textGeom.center();
            
            const textMat= new THREE.MeshBasicMaterial();
            //objMat.side=THREE.DoubleSide;
            const textMesh = new THREE.Mesh(textGeom,textMat);
            textMat.color=new THREE.Color(0,1,1);
            textMesh.position.x=x;
            textMesh.position.y=y;
            textMesh.position.z=z;

            scene.add(textMesh);
            object_texts.push(textMesh);
        });
    }
}
//setTexts([{"text":"TEST","size":1,"x":0,"y":0,"z":-10}]);
function updateTexts(){
    request(
        "texts",
        function(resp){setTexts(JSON.parse(resp));},
        function(){});
}

// Display: Point Cloud
var object_walls=[];
var planeSize=3.0;
function setWalls(wallList){
    for (var i=0;i<object_walls.length;i++){
        scene.remove(object_walls[i])
    }
    object_walls=[];
    
    // Add objects
    for (var i=0;i<wallList.length;i++){
        var wall=wallList[i];
        
        let x=wall["x"];
        let y=wall["y"];
        let z=wall["z"];
        let laX=wall["x"]+wall["nvX"];
        let laY=wall["y"]+wall["nvY"];
        let laZ=wall["z"]+wall["nvZ"];
        let tContent = "Wall "+i;
        let tSize=0.5;
        
        const objGeom = new THREE.PlaneGeometry(planeSize,planeSize);
        const objMat= new THREE.MeshStandardMaterial();
        objMat.wireframe=true;
        //const objMat = new THREE.LineBasicMaterial();
        objMat.color=new THREE.Color(0,1,1);
        //objMat.side=THREE.DoubleSide;
        const objMesh = new THREE.Mesh(objGeom,objMat);
        objMesh.position.x=x;
        objMesh.position.y=y;
        objMesh.position.z=z;
        
        objMesh.lookAt(laX,laY,laZ);
        
        scene.add(objMesh);
        object_walls.push(objMesh);
        
        floader.load( 'font.typeface.json', function ( font ) {
            
            const textGeom = new TextGeometry( tContent, {
                font: font,
                size: tSize,
                height: tSize/10,
                curveSegments: 12,
            } );
            textGeom.computeBoundingBox();
            //textGeom.translate(-textGeom.boundingBox.max.x/2,0,0);
            textGeom.center();
            const textMat= new THREE.MeshBasicMaterial();
            //objMat.side=THREE.DoubleSide;
            const textMesh = new THREE.Mesh(textGeom,textMat);
            textMat.color=new THREE.Color(0,1,1);
            textMesh.position.x=x;
            textMesh.position.y=y;
            textMesh.position.z=z;
            textMesh.lookAt(laX,laY,laZ);
            
            scene.add(textMesh);
            object_walls.push(textMesh);
        });
        
        
    }
}

function updateWalls(){
    request(
        "walls",
        function(resp){setWalls(JSON.parse(resp));},
            function(){});
}

var last_update_flag;
function updateCheck(){
    request(
        "/update_flag",
        function(resp){
            if (resp != last_update_flag){
                console.log("Updating "+resp);
                last_update_flag=resp;
                //getObjData();
                updateSeg3D();
                updatePC();
                updateTexts();
                updateWalls();
            }
        },
        function(e){}
    );
}
setInterval(updateCheck,50);


