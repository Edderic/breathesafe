import {parseInspectionPLY,analysisBuffers,prepareInspectionMesh} from './webcam_mesh_buffers';
import {selectInspectionFaces} from './webcam_regional_buffers';
self.onmessage=({data})=>{
  try {
    let buffers=data.buffer ? parseInspectionPLY(data.buffer) : analysisBuffers(data.mesh);
    if(data.faceIndices)buffers=selectInspectionFaces(buffers,data.faceIndices);
    const result=prepareInspectionMesh(buffers,data.camera,data.scale);
    self.postMessage({result},[result.positions.buffer,result.indices.buffer,result.normals.buffer]);
  }catch(error){self.postMessage({error:error instanceof RangeError ? 'Mesh allocation exceeded available memory. Download the original for external inspection.' : error.message});}
};
