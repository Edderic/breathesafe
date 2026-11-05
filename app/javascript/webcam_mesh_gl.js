// Indexed GPU rendering leaves the bounded SVG annotation/picking limits intact.
const vertexSource=`#version 300 es
in vec3 position;in vec3 normal;
uniform vec3 center;uniform float pixelsPerUnit;uniform float yaw;uniform float pitch;uniform float radius;
out vec3 litNormal;out vec3 modelPoint;
vec3 rotate(vec3 p){float a=cos(yaw),b=sin(yaw),c=cos(pitch),d=sin(pitch);vec3 q=vec3(a*p.x+b*p.z,p.y,-b*p.x+a*p.z);return vec3(q.x,c*q.y-d*q.z,d*q.y+c*q.z);}
void main(){vec3 p=rotate(position-center);modelPoint=p;litNormal=rotate(normal);
gl_Position=vec4(p.x*pixelsPerUnit/360.,p.y*pixelsPerUnit/240.,-p.z/radius,1.);}`;
const fragmentSource=`#version 300 es
precision highp float;
in vec3 litNormal;in vec3 modelPoint;uniform float azimuth;uniform bool smoothLight;uniform bool edges;
out vec4 color;
void main(){if(edges){color=vec4(.07,.12,.17,1.);return;}
vec3 n=smoothLight?normalize(litNormal):normalize(cross(dFdx(modelPoint),dFdy(modelPoint)));
if(n.z<0.)n=-n;vec3 light=normalize(vec3(sin(azimuth),.7,cos(azimuth)));
float brightness=.14+.78*max(0.,dot(n,light))+.08*max(0.,n.z);
color=vec4(vec3(218.,210.,198.)/255.*brightness,1.);}`;

export function createMeshRenderer(canvas,onFailure) {
  const gl=canvas.getContext('webgl2',{antialias:true,alpha:false});
  if(!gl)throw Error('WebGL 2 is unavailable. The existing analysis view and original mesh download remain available.');
  let program,vao,edgesBuffer,edgeCount=0,count=0,disposed=false;
  const buffers=[],shaders=[];
  function cleanup(){for(const b of buffers)gl.deleteBuffer(b);if(vao)gl.deleteVertexArray(vao);if(program)gl.deleteProgram(program);for(const s of shaders)gl.deleteShader(s);}
  function lost(event){event.preventDefault();onFailure('GPU context lost. Close other GPU-heavy tabs and retry inspection.');}
  canvas.addEventListener('webglcontextlost',lost);
  try {
    program=gl.createProgram();if(!program)throw Error('Could not allocate a GPU program.');
    for(const [type,source] of [[gl.VERTEX_SHADER,vertexSource],[gl.FRAGMENT_SHADER,fragmentSource]]) {
      const shader=gl.createShader(type);if(!shader)throw Error('Could not allocate GPU shaders.');shaders.push(shader);
      gl.shaderSource(shader,source);gl.compileShader(shader);
      if(!gl.getShaderParameter(shader,gl.COMPILE_STATUS))throw Error('Mesh shader compilation failed: '+gl.getShaderInfoLog(shader));
      gl.attachShader(program,shader);
    }
    gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error('Mesh GPU program could not link.');
    vao=gl.createVertexArray();if(!vao)throw Error('Could not allocate GPU vertex data.');gl.bindVertexArray(vao);gl.useProgram(program);
    function buffer(target,values) {
      const value=gl.createBuffer();if(!value)throw Error('Could not allocate GPU mesh memory.');buffers.push(value);
      gl.bindBuffer(target,value);gl.bufferData(target,values,gl.STATIC_DRAW);
      if(gl.getError()!==gl.NO_ERROR)throw Error('GPU mesh allocation failed. Download the original for external inspection.');
      return value;
    }
    const uniforms=Object.fromEntries(['center','pixelsPerUnit','yaw','pitch','radius','azimuth','smoothLight','edges'].map(name=>[name,gl.getUniformLocation(program,name)]));
    let data;
    return {
      upload(mesh) {
        data={indices:mesh.indices};count=mesh.indices.length;
        for(const [name,values] of [['position',mesh.positions],['normal',mesh.normals]]) {
          buffer(gl.ARRAY_BUFFER,values);const location=gl.getAttribLocation(program,name);
          gl.enableVertexAttribArray(location);gl.vertexAttribPointer(location,3,gl.FLOAT,false,0,0);
        }
        buffer(gl.ELEMENT_ARRAY_BUFFER,mesh.indices);
      },
      draw(view) {
        if(disposed || gl.isContextLost())return;
        const ratio=Math.min(window.devicePixelRatio||1,2),width=Math.max(1,Math.round(canvas.clientWidth*ratio)),height=Math.max(1,Math.round(width*2/3));
        if(canvas.width!==width || canvas.height!==height){canvas.width=width;canvas.height=height;}
        gl.viewport(0,0,canvas.width,canvas.height);gl.useProgram(program);gl.bindVertexArray(vao);
        gl.clearColor(25/255,43/255,56/255,1);gl.enable(gl.DEPTH_TEST);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
        gl.uniform3fv(uniforms.center,view.frame.center);gl.uniform1f(uniforms.pixelsPerUnit,view.frame.scale*view.zoom);
        gl.uniform1f(uniforms.yaw,view.yaw*Math.PI/180);gl.uniform1f(uniforms.pitch,view.pitch*Math.PI/180);
        gl.uniform1f(uniforms.radius,190/view.frame.scale*2);gl.uniform1f(uniforms.azimuth,view.lightAzimuth*Math.PI/180);
        gl.uniform1i(uniforms.smoothLight,view.smoothLighting);gl.uniform1i(uniforms.edges,false);
        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,buffers[2]);gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(1,1);
        gl.drawElements(gl.TRIANGLES,count,gl.UNSIGNED_INT,0);gl.disable(gl.POLYGON_OFFSET_FILL);
        if(view.surfaceEdges) {
          if(!edgesBuffer) {
            const edges=new Uint32Array(count*2);for(let i=0;i<count;i+=3)edges.set([data.indices[i],data.indices[i+1],data.indices[i+1],data.indices[i+2],data.indices[i+2],data.indices[i]],i*2);
            edgeCount=edges.length;edgesBuffer=buffer(gl.ELEMENT_ARRAY_BUFFER,edges);
          }
          gl.uniform1i(uniforms.edges,true);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,edgesBuffer);gl.drawElements(gl.LINES,edgeCount,gl.UNSIGNED_INT,0);
        }
        if(gl.getError()!==gl.NO_ERROR)throw Error('GPU drawing failed. Retry with mesh edges disabled or download the original.');
      },
      dispose(){if(disposed)return;disposed=true;canvas.removeEventListener('webglcontextlost',lost);cleanup();data=null;gl.getExtension('WEBGL_lose_context')?.loseContext();},
    };
  }catch(error){canvas.removeEventListener('webglcontextlost',lost);cleanup();gl.getExtension('WEBGL_lose_context')?.loseContext();throw error;}
}
