// Imports
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';
import { FontLoader } from 'three/addons/loaders/FontLoader.js';
import * as BufferGeometryUtils from 'three/addons/utils/BufferGeometryUtils.js';

var webpageConfig= $$$PYTHON REPLACE: WEBPAGE_CONFIG$$$;

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
const camera = new THREE.PerspectiveCamera( $$$PYTHON REPLACE: CAM FOV$$$, w/h, 0.001, 1000 );
const controls = new OrbitControls( camera, renderer.domElement );
controls.target=new THREE.Vector3( 0, 0, -3 );
camera.position.set( 0, 0, 0 );
controls.update();

var cameraVelocity=[-1,0,0];
var lastUpdateTime=0;
// Anim Loop
function animation( time ) {
    controls.update();
    
    var deltaT=(time-lastUpdateTime)/1000; //seconds
    lastUpdateTime=time;
    
    var moveTarget=[]
        .concat(object_walls)
        .concat(object_texts)
        .concat(object_points)
        .concat(wire_meshes);
    for (var i in moveTarget){
        var obj=moveTarget[i];
        obj.position.x-=cameraVelocity[0]*deltaT;
        obj.position.y-=cameraVelocity[1]*deltaT;
        obj.position.z-=cameraVelocity[2]*deltaT;
    }
    
    renderer.render( scene, camera );
}



function request(location,succ,fail){
    var xhr=new XMLHttpRequest();
    xhr.timeout=1000;
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

function updateCV(){
    request(
        "camVelocity",
        function(resp){
            cameraVelocity=JSON.parse(resp);
            //console.log(cameraVelocity);
        },
        function(){});
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

// Use Catmull-Rom Curve
function buildWireMeshCC(pointlist,w){
    
    let points=[];
    for (var i in pointlist){
        var pt=pointlist[i];
        points.push(new THREE.Vector3(pt[0],pt[1],pt[2]));
    }
    const curve = new THREE.CatmullRomCurve3(points);
    
    //const curvePoints = curve.getPoints( 100 );
    //const geometry = new THREE.BufferGeometry().setFromPoints( curvePoints );
    const geometry = new THREE.TubeGeometry(
        curve,
        128, //Curve Segments
        w/2, //Radius
        4,   //Radial Segments
        true //Closed
    )
    
    const material = new THREE.MeshBasicMaterial();
    material.color=new THREE.Color(1,0,0);
    var line = new THREE.Mesh( geometry, material );
    
    return line;
}

var wire_meshes=[];
function setSeg3D(s3d){
    var new_wires=[];

    for (var i in s3d){
        let name = s3d[i]["name"];
        let width = s3d[i]["width"];
        let pointlist= s3d[i]["pointlist"];
        let wm=buildWireMeshCC(pointlist,width);
        new_wires.push(wm);
    }
    
    for (var i=0;i<new_wires.length;i++){
        scene.add(new_wires[i]);
    }
    for (var i=0;i<wire_meshes.length;i++){
        scene.remove(wire_meshes[i])
    }
    wire_meshes=new_wires;
}

function updateSeg3D(){
    request(
        "seg3d",
        function(resp){
            setSeg3D(JSON.parse(resp));
            //console.log("  Updated SEG3D");
        },
        function(){});
}


// Display: Point Cloud

var object_points=[];
var pointCubeSize=0.03;
function setPointCloud(pointList){
    var new_points=[];
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

        new_points.push(objMesh);
    }
    
    for (var i=0;i<new_points.length;i++){
        scene.add(new_points[i]);
        
    }
    for (var i=0;i<object_points.length;i++){
        scene.remove(object_points[i])
    }
    object_points=new_points;
}

function updatePC(){
    request(
        "pointcloud",
        function(resp){
            setPointCloud(JSON.parse(resp));
            //console.log("  Updated POINTCLOUD");
        },
        function(){});
}


// Display: Texts
const floader = new FontLoader();

var font;
floader.load( 'font.typeface.json', function ( f ) { font=f;});
var object_texts=[];
function setTexts(textList){
    
    var new_texts=[];

    for (var i=0;i<textList.length;i++){
        let tContent=textList[i]["text"];
        let tSize=textList[i]["size"];
        
        let x=textList[i]["x"];
        let y=textList[i]["y"];
        let z=textList[i]["z"];
        
        let r=textList[i]["r"];
        let g=textList[i]["g"];
        let b=textList[i]["b"];

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
        textMat.color=new THREE.Color(r,g,b);
        textMesh.position.x=x;
        textMesh.position.y=y;
        textMesh.position.z=z;

        new_texts.push(textMesh);
    
    }
    
    for (var i=0;i<new_texts.length;i++){
        scene.add(new_texts[i]);
        
    }
    for (var i=0;i<object_texts.length;i++){
        scene.remove(object_texts[i])
    }
    object_texts=new_texts;
    
}
//setTexts([{"text":"TEST","size":1,"x":0,"y":0,"z":-10}]);
function updateTexts(){
    request(
        "texts",
        function(resp){
            setTexts(JSON.parse(resp));
            //console.log("  Updated TEXT");
        },
        function(){});
}

function createSquareFrameGeometry(innerL,outerL){
    const geometry = new THREE.BufferGeometry();
    
    let i1=[+innerL,+innerL,0];
    let i2=[-innerL,+innerL,0];
    let i3=[-innerL,-innerL,0];
    let i4=[+innerL,-innerL,0];
    let o1=[+outerL,+outerL,0];
    let o2=[-outerL,+outerL,0];
    let o3=[-outerL,-outerL,0];
    let o4=[+outerL,-outerL,0];
    const vertices = new Float32Array( [
        +innerL,+innerL,0,
        -outerL,+outerL,0,
        +outerL,+outerL,0,
        
        +innerL,+innerL,0,
        -outerL,+outerL,0,
        -innerL,+innerL,0,
        
        
        -innerL,+innerL,0,
        -outerL,-outerL,0,
        -outerL,+outerL,0,
        
        -innerL,+innerL,0,
        -outerL,-outerL,0,
        -innerL,-innerL,0,
        
        
        -innerL,-innerL,0,
        +outerL,-outerL,0,
        -outerL,-outerL,0,
        
        -innerL,-innerL,0,
        +outerL,-outerL,0,
        +innerL,-innerL,0,
        
        
        +innerL,-innerL,0,
        +outerL,+outerL,0,
        +outerL,-outerL,0,
        
        +innerL,-innerL,0,
        +outerL,+outerL,0,
        +innerL,+innerL,0]
    );
    
    //console.log(vertices);

    // itemSize = 3 because there are 3 values (components) per vertex
    geometry.setAttribute( 'position', new THREE.BufferAttribute( vertices, 3 ) );
    geometry.computeBoundingBox();
    return geometry;
}

// Display: Walls
var object_walls=[];
var planeSize=3.0;
function setWalls(wallList){
    floader.load( 'font.typeface.json', function ( font ) {
        var new_walls=[];
        
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
            let tSize=0.4;
            
            /*
            
            const objGeom = new THREE.PlaneGeometry(planeSize,planeSize);
            const objMat= new THREE.MeshStandardMaterial();
            objMat.wireframe=true;
            //const objMat = new THREE.LineBasicMaterial();
            objMat.color=new THREE.Color(0,1,1);
            //objMat.side=THREE.DoubleSide;
            const objMesh = new THREE.Mesh(objGeom,objMat);*/
            const objGeom=BufferGeometryUtils.mergeGeometries(
                [createSquareFrameGeometry(0.9,1.0),
                createSquareFrameGeometry(1.2,1.3)],false);
                                                            
            
            const objMat = new THREE.MeshBasicMaterial( { color: 0xff0000 } );
            objMat.color = new THREE.Color(0.5,0.0,0.5);
            objMat.side=THREE.DoubleSide;
            const objMesh = new THREE.Mesh( objGeom, objMat );
        
            objMesh.position.x=x;
            objMesh.position.y=y;
            objMesh.position.z=z;
            
            objMesh.lookAt(laX,laY,laZ);
            
            new_walls.push(objMesh);
                
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
            textMat.color=new THREE.Color(1.0,0.3,1.0);
            textMesh.position.x=x;
            textMesh.position.y=y;
            textMesh.position.z=z;
            textMesh.lookAt(laX,laY,laZ);
            
            
            new_walls.push(textMesh);
            
        }
        
        
        
        for (var i=0;i<new_walls.length;i++){
            scene.add(new_walls[i]);
            
        }
        for (var i=0;i<object_walls.length;i++){
            scene.remove(object_walls[i])
        }
        object_walls=new_walls;
    });
}

function updateWalls(){
    request(
        "walls",
        function(resp){
            setWalls(JSON.parse(resp));
            //console.log("  Updated WALL");
        },
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
                updateSeg3D();
                updateTexts();
                updateCV();
                if (webpageConfig["pointcloud"]) updatePC();
                if (webpageConfig["walls"]) updateWalls();
            }
        },
        function(e){}
    );
}
setInterval(updateCheck,50);


