import {parseInspectionPLY,analysisBuffers,prepareInspectionMesh} from './webcam_mesh_buffers';
self.onmessage=({data})=>{
  try {
    const buffers=data.buffer ? parseInspectionPLY(data.buffer) : analysisBuffers(data.mesh);
    const result=prepareInspectionMesh(buffers,data.camera,data.scale);
    self.postMessage({result},[result.positions.buffer,result.indices.buffer,result.normals.buffer]);
  }catch(error){self.postMessage({error:error instanceof RangeError ? 'Mesh allocation exceeded available memory. Download the original for external inspection.' : error.message});}
};
